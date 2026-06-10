# Referência de Medidas DAX

Medidas prontas para copiar e colar no Power BI (botão direito na tabela `_Medidas` →
**Nova medida**). Cada uma tem o código e uma explicação curta. Os nomes das tabelas e
colunas seguem exatamente o schema `dw` deste projeto.

> **Antes de começar, entenda o grão da fato.** Veja a seção
> [O grão da `fato_matricula`](#o-grão-da-fato_matricula) no final — ela explica por que
> algumas medidas usam `SUMX`/`DISTINCTCOUNT` e não um simples `SUM`/`COUNT`.

---

## Medidas básicas

### Cursos Vendidos
```dax
Cursos Vendidos = COUNTROWS ( fato_matricula )
```
Conta as linhas da fato. Como o grão é **um curso por linha**, isso é o total de cursos
vendidos (itens de matrícula). Equivale a `cursos_vendidos` da `vw_receita_mensal`.

### Total Matrículas
```dax
Total Matrículas = DISTINCTCOUNT ( fato_matricula[nk_matricula] )
```
Conta **matrículas distintas**. Como uma matrícula com vários cursos ocupa várias linhas,
usamos `DISTINCTCOUNT` para não contar a mesma matrícula mais de uma vez. Equivale a
`total_matriculas` das views.

### Receita Total ✅ (versão correta)
```dax
Receita Total =
SUMX (
    VALUES ( fato_matricula[nk_matricula] ),
    CALCULATE ( MAX ( fato_matricula[valor_total] ) )
)
```
Soma o `valor_total` **uma vez por matrícula**. `VALUES(...)` gera a lista de matrículas
distintas no contexto atual; para cada uma, `CALCULATE(MAX(...))` pega o `valor_total`
daquela matrícula (que é o mesmo em todas as suas linhas); `SUMX` soma esses valores. É a
forma **correta** de calcular receita, sem duplicação.

### Receita (ingênua) ❌ — NÃO use, só para comparar
```dax
Receita (ingênua) = SUM ( fato_matricula[valor_total] )
```
Esta soma **todas** as linhas, repetindo o valor da matrícula uma vez por curso. Resultado:
receita **inflada** para matrículas com 2+ cursos. Crie esta medida lado a lado com a correta
para **ver a diferença** num cartão — é a melhor forma de internalizar o conceito de grão.

### Ticket Médio
```dax
Ticket Médio = DIVIDE ( [Receita Total], [Total Matrículas] )
```
Receita média por matrícula. `DIVIDE` é preferível a `/` porque trata divisão por zero sem
erro. Equivale a `ticket_medio` da `vw_receita_mensal`.

---

## Medidas de evasão (Página 3)

### Matrículas em Evasão
```dax
Matrículas em Evasão =
CALCULATE (
    [Total Matrículas],
    dim_status[codigo_status] IN { "Trancada", "Cancelada" }
)
```
Reaproveita `[Total Matrículas]`, mas filtrando só os status considerados evasão pela regra de
negócio do projeto (Trancada e Cancelada).

### Taxa de Evasão %
```dax
Taxa de Evasão % = DIVIDE ( [Matrículas em Evasão], [Total Matrículas] )
```
Percentual de matrículas em evasão. Formate como **Porcentagem** em Ferramentas de Medida.
Equivale a `SUM(percentual) WHERE is_evasao` da `vw_funil_evasao`.

### Receita em Risco
```dax
Receita em Risco =
CALCULATE (
    [Receita Total],
    dim_status[codigo_status] IN { "Trancada", "Cancelada" }
)
```
Receita das matrículas em evasão — quanto de dinheiro está "em risco".

---

## Medidas de curso (Página 2)

### Receita por Hora
```dax
Receita por Hora = DIVIDE ( [Receita Total], SUM ( dim_curso[carga_horaria] ) )
```
Receita gerada por hora de curso — uma métrica de eficiência. Funciona no contexto de cada
curso (quando `dim_curso[nome_curso]` está no eixo). Espelha `receita_por_hora` da
`vw_desempenho_cursos`.

> Observação: no nível "total" (todos os cursos juntos) essa medida divide a receita pela
> soma de todas as cargas horárias, então só interprete-a **por curso** (com a dimensão no
> eixo do visual).

---

## O grão da `fato_matricula`

**Grão = o que representa uma linha.** Aqui, **cada linha é um curso dentro de uma
matrícula** (par matrícula-curso). Ver `etl/load_fato_matricula.py` (linhas 8-13 e 282-285).

As métricas `valor_total`, `qtd_cursos` e `valor_medio_curso` foram **calculadas no nível da
matrícula inteira e replicadas** em cada linha de curso daquela matrícula. Exemplo de uma
matrícula (`nk_matricula = 50`) com 3 cursos somando R$ 900:

| nk_matricula | sk_curso | valor_total | qtd_cursos |
|--------------|----------|-------------|------------|
| 50           | 12       | 900         | 3          |
| 50           | 7        | 900         | 3          |
| 50           | 3        | 900         | 3          |

Consequências práticas para o DAX:

| Você quer...                  | Errado ❌                  | Certo ✅                                      |
|-------------------------------|----------------------------|-----------------------------------------------|
| Receita total                 | `SUM(valor_total)` (3×)    | `SUMX(VALUES(nk_matricula), CALCULATE(MAX(valor_total)))` |
| Nº de matrículas              | `COUNTROWS` (conta itens)  | `DISTINCTCOUNT(nk_matricula)`                 |
| Nº de cursos vendidos         | —                          | `COUNTROWS(fato_matricula)` (aqui o item é o certo) |

**Regra de ouro:** antes de somar ou contar, pergunte "uma linha aqui é o quê?". Se a métrica
está num nível mais "alto" que a linha (valor da matrícula numa tabela de itens), ela está
**repetida** — e somar direto duplica. Esse é um dos conceitos mais importantes da modelagem
dimensional (Kimball) e o erro nº 1 de quem está começando.
