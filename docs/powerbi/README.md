# Dashboard no Power BI — Guia passo a passo (nível iniciante)

Este guia mostra como construir, **do zero**, um dashboard no Power BI Desktop em cima do
Data Warehouse deste projeto. O foco é **aprender os conceitos centrais do Power BI**:

1. Conectar a uma fonte de dados (PostgreSQL)
2. Modelar relacionamentos (a *Model View* / "Exibição de Modelo")
3. Escrever medidas em **DAX**
4. Montar visuais e páginas

> Vamos conectar diretamente nas tabelas do **star schema** (`fato_matricula` + as 4
> dimensões), e **não** nas views prontas (`vw_*`). Conectar nas tabelas é o que ensina a
> parte mais importante do Power BI: relacionamentos e DAX. As views ficam como **gabarito**
> para conferir se os números do dashboard estão certos (ver "Passo 5 — Validação").

---

## Pré-requisitos

- **Power BI Desktop** instalado (Windows). Download gratuito na Microsoft Store ou em
  [powerbi.microsoft.com/desktop](https://powerbi.microsoft.com/desktop/).
- Acesso ao banco PostgreSQL do projeto (hospedado no Render).
- A connection string do banco, que está na variável `DATABASE_URL` do seu arquivo `.env`.

### Decompondo a `DATABASE_URL`

O Power BI pede os campos de conexão separadamente. A `DATABASE_URL` tem este formato:

```
postgresql://USUARIO:SENHA@HOST:PORTA/NOME_DO_BANCO
```

Exemplo (fictício) e o que cada parte vira no Power BI:

| Parte da URL        | Onde usar no Power BI                         |
|---------------------|-----------------------------------------------|
| `HOST:PORTA`        | **Servidor** (ex.: `dpg-xxxx.oregon-postgres.render.com:5432`) |
| `NOME_DO_BANCO`     | **Banco de dados**                            |
| `USUARIO` / `SENHA` | **Nome de usuário** / **Senha** (aba credenciais) |

> Dica: o Render fornece tanto a *Internal* quanto a *External Database URL*. Para conectar
> da sua máquina, use a **External Database URL**.

---

## Passo 0 — Garantir que há dados no DW

Se você ainda **não** rodou o seed + ETL + views (ou não tem certeza), execute na raiz do
projeto, **nesta ordem**:

```bash
poetry install                                   # instala dependências
poetry run python tests/test_database.py         # cria os schemas oltp e dw
poetry run python scripts/create_tables.py       # cria todas as tabelas
poetry run python scripts/seed_data.py           # popula OLTP + dim_tempo (dados sintéticos)
poetry run python etl/load_fato_matricula.py     # popula dimensões + fato_matricula
poetry run python scripts/create_views.py        # cria as 3 views (gabarito de validação)
```

Para conferir rapidamente que o DW foi populado:

```bash
poetry run python scripts/validate_dw.py
```

Se as contagens de `dw.fato_matricula` e das dimensões aparecerem com valores > 0, você está
pronto para conectar o Power BI.

---

## Passo 1 — Conectar o Power BI ao PostgreSQL

1. Abra o **Power BI Desktop** → **Página Inicial** → **Obter Dados** → **Mais...**
2. Procure por **PostgreSQL database** (Banco de dados PostgreSQL) → **Conectar**.
   - Se for a primeira vez, o Power BI pode pedir para instalar o conector **Npgsql**.
     Aceite e instale (reinicie o Power BI se necessário).
3. Preencha:
   - **Servidor:** `HOST:PORTA` (ex.: `dpg-xxxx.oregon-postgres.render.com:5432`)
   - **Banco de dados:** o `NOME_DO_BANCO` da sua URL.
4. Em **Modo de Conectividade de Dados**, escolha **Importar** (não use *DirectQuery* —
   *Import* é o padrão para iniciantes e mantém tudo em memória, rápido e simples).
5. Clique **OK**. Na tela de credenciais, escolha a aba **Banco de dados** e informe
   **Usuário** e **Senha** da URL.
6. **Importante (Render exige SSL):** marque a opção de **criptografar conexão / usar
   conexão criptografada (SSL)**. Se a conexão falhar por SSL, tente novamente com essa
   opção marcada.
7. No **Navegador**, expanda o schema **`dw`** e marque **apenas** estas 5 tabelas:
   - `fato_matricula`
   - `dim_aluno`
   - `dim_curso`
   - `dim_tempo`
   - `dim_status`
8. Clique em **Carregar** (não precisamos transformar nada no Power Query agora).

> **Por que não importar as views `vw_*`?** Porque elas já vêm agregadas e prontas — se
> usássemos elas, você pularia justamente o que queremos aprender (relacionamentos e DAX).
> Vamos reconstruir essa lógica nós mesmos e depois conferir com as views.

---

## Passo 2 — Model View: criar os relacionamentos (star schema)

Clique no ícone **Exibição de Modelo** (Model View), no lado esquerdo. Você verá as 5
tabelas. Agora vamos ligar a tabela fato a cada dimensão pelas **surrogate keys (sk_)**.

Arraste o campo da fato para o campo correspondente da dimensão (ou use **Gerenciar
Relacionamentos**). Crie estes **4 relacionamentos**:

| Da tabela fato            | Para a dimensão          |
|---------------------------|--------------------------|
| `fato_matricula[sk_aluno]`  | `dim_aluno[sk_aluno]`    |
| `fato_matricula[sk_curso]`  | `dim_curso[sk_curso]`    |
| `fato_matricula[sk_tempo]`  | `dim_tempo[sk_tempo]`    |
| `fato_matricula[sk_status]` | `dim_status[sk_status]`  |

Para **cada** relacionamento, confirme:

- **Cardinalidade:** **Um para muitos (1:*)** — 1 linha na dimensão, muitas na fato.
- **Direção do filtro cruzado:** **Única** (a dimensão filtra a fato, não o contrário).
  Essa é a forma correta no star schema e evita ambiguidades.

O resultado visual é uma **estrela**: a `fato_matricula` no centro, as 4 dimensões ao redor.

### Marcar a dimensão de tempo como Tabela de Datas

1. Selecione a tabela **`dim_tempo`**.
2. **Ferramentas de Tabela** → **Marcar como tabela de datas** → escolha a coluna
   **`data_completa`**.

Isso habilita a inteligência de tempo do Power BI (ordenação correta de meses, hierarquias
de data etc.).

> **Conceito-chave:** num star schema, os **filtros** sempre fluem das **dimensões** para a
> **fato**. Por isso, nos eixos dos gráficos usamos colunas das **dimensões**
> (`dim_curso[nome_curso]`, `dim_tempo[nome_mes]`...) e nos valores usamos **medidas** que
> agregam a fato.

---

## Passo 3 — Criar as medidas DAX

As **medidas** são os cálculos do dashboard (receita, ticket médio, taxa de evasão...).

1. Boa prática: crie uma tabela só para organizar as medidas. **Página Inicial** →
   **Inserir Dados** → crie uma tabela vazia chamada **`_Medidas`** (uma coluna qualquer, que
   você pode ocultar depois). Todas as medidas ficarão agrupadas ali.
2. Para cada medida: clique com o botão direito em `_Medidas` → **Nova medida** → cole o
   código DAX.

Os códigos completos, com explicação de cada um, estão em
[`medidas-dax.md`](./medidas-dax.md). Comece criando estas:

- `Cursos Vendidos`
- `Total Matrículas`
- `Receita Total`
- `Ticket Médio`
- `Matrículas em Evasão`
- `Taxa de Evasão %`
- `Receita por Hora`

### ⚠️ A lição mais importante: o GRÃO da tabela fato

A `fato_matricula` tem **uma linha por curso de cada matrícula** (grão por item). O detalhe
crítico: as colunas `valor_total`, `qtd_cursos` e `valor_medio_curso` guardam o valor da
**matrícula inteira**, **repetido** em cada linha de curso daquela matrícula.

Exemplo — uma matrícula com 3 cursos vira 3 linhas, todas com `valor_total = 900`:

| nk_matricula | sk_curso | valor_total |
|--------------|----------|-------------|
| 50           | 12       | 900         |
| 50           | 7        | 900         |
| 50           | 3        | 900         |

Se você fizer `SUM(valor_total)`, o Power BI soma **900 + 900 + 900 = 2700** — ou seja,
**conta a receita em triplo**! Por isso a medida `Receita Total` usa `SUMX` deduplicando por
matrícula (soma o `valor_total` **uma vez por matrícula**). Veja a explicação completa em
[`medidas-dax.md`](./medidas-dax.md).

> Esse é o conceito de **grão (grain)** da modelagem dimensional de Kimball: você precisa
> saber "o que é uma linha" antes de somar qualquer coisa.

---

## Passo 4 — Montar as 3 páginas do dashboard

Cada página responde a uma das 3 perguntas de negócio do projeto. Use o painel
**Visualizações** para arrastar os visuais e o painel **Dados** para arrastar campos.

### Página 1 — Receita Mensal
*Pergunta: "Qual a receita mensal e o ticket médio da escola?"*

- **3 Cartões (Card):** `Receita Total`, `Total Matrículas`, `Ticket Médio`.
- **Gráfico de Linhas:** Eixo = `dim_tempo[ano]` + `dim_tempo[nome_mes]`; Valores =
  `Receita Total`.
- **Segmentação de Dados (Slicer):** `dim_tempo[ano]` e/ou `dim_tempo[trimestre]`.

### Página 2 — Desempenho de Cursos
*Pergunta: "Quais cursos geram mais receita e melhor ticket médio?"*

- **Gráfico de Barras:** Eixo = `dim_curso[nome_curso]`; Valores = `Receita Total`
  (ordene do maior para o menor; use *Top N* se quiser destacar os melhores).
- **Tabela / Matriz:** linhas = `dim_curso[nome_curso]`; colunas = `Receita Total`,
  `Cursos Vendidos`, `Ticket Médio`, `Receita por Hora`.
- **Cartão:** curso campeão de receita (ou de `Receita por Hora`).

### Página 3 — Funil de Evasão
*Pergunta: "Qual a taxa de evasão e quanta receita está em risco?"*

- **Gráfico de Rosca (Donut) ou Colunas:** Legenda/Eixo = `dim_status[descricao_status]`;
  Valores = `Total Matrículas`.
- **Cartão:** `Taxa de Evasão %`.
- **Cartão:** `Receita Total` filtrada para status em evasão (receita em risco) — você pode
  usar a medida `Receita em Risco` (ver `medidas-dax.md`) ou um filtro de nível de visual em
  `dim_status[codigo_status]` = *Trancada* / *Cancelada*.

> Dica de design: mantenha as 3 páginas com o mesmo cabeçalho e cores. Coloque os slicers no
> canto superior esquerdo de cada página.

---

## Passo 5 — Validação (conferir com o gabarito)

As views `vw_*` são o nosso gabarito. Rode no banco (psql, DBeaver, pgAdmin...) e compare:

```sql
SELECT * FROM dw.vw_receita_mensal   ORDER BY ano, mes;
SELECT * FROM dw.vw_desempenho_cursos ORDER BY receita_gerada DESC;
SELECT * FROM dw.vw_funil_evasao;
```

O que deve acontecer:

| Medida no Power BI         | Comparar com                                  | Deve bater? |
|----------------------------|-----------------------------------------------|-------------|
| `Total Matrículas`         | `vw_receita_mensal.total_matriculas`          | ✅ Sim, exatamente |
| `Cursos Vendidos`          | `vw_receita_mensal.cursos_vendidos`           | ✅ Sim, exatamente |
| `Taxa de Evasão %`         | `SUM(percentual) WHERE is_evasao` em `vw_funil_evasao` | ✅ Sim |
| `Receita Total` (com SUMX) | `vw_receita_mensal.receita_total`             | ⚠️ **Vai divergir** — veja abaixo |

> **Por que a receita diverge?** A view `vw_receita_mensal` usa `SUM(valor_total)`, que sofre
> exatamente da duplicação explicada no Passo 3. A sua medida `Receita Total` (com `SUMX`)
> está **correta** — ela soma cada matrícula uma única vez. Ou seja: aqui o seu dashboard
> está **mais certo que a view**. (Corrigir as views SQL é uma melhoria opcional do projeto,
> fora do escopo deste guia.) Você pode confirmar o valor correto com:
>
> ```sql
> SELECT SUM(valor_total) FROM (
>   SELECT DISTINCT nk_matricula, valor_total FROM dw.fato_matricula
> ) AS receita_por_matricula;
> ```

---

## Boas práticas para iniciantes

- **Nomeie medidas** de forma clara e em português (`Receita Total`, não `Measure 1`).
- **Formate moeda:** selecione a medida → **Ferramentas de Medida** → Formato **Moeda** (R$).
- **Oculte as colunas técnicas** (`sk_*`, `nk_*`, `data_carga`) na *Model View* — clique com
  o botão direito → **Ocultar na exibição de relatório**. Elas servem para relacionamento, não
  para o usuário final.
- **Eixos = dimensões, Valores = medidas.** Nunca arraste colunas da fato direto para um
  gráfico; use sempre medidas.
- **Salve cedo e sempre** o arquivo `.pbix`.

---

## Resumo do que você aprendeu

| Conceito do Power BI       | Onde apareceu neste guia                          |
|----------------------------|---------------------------------------------------|
| Conexão a dados            | Passo 1 (PostgreSQL, modo Import, SSL)            |
| Modelagem / relacionamentos| Passo 2 (star schema, cardinalidade, filtro)      |
| Tabela de datas            | Passo 2 (marcar `dim_tempo`)                      |
| Medidas DAX                | Passo 3 + `medidas-dax.md`                        |
| Grão de tabela fato        | Passo 3 (a lição do `SUMX` vs `SUM`)              |
| Visuais e páginas          | Passo 4 (cartões, barras, linhas, rosca, slicers) |
| Validação de dados         | Passo 5 (comparar com as views)                   |
