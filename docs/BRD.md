# BRD (Business Requirements Document) — Gestão Educacional

> **Data:** 2026-04-30  
> **Área Solicitante:** Diretoria Executiva / Comercial  
> **Status:** Aprovado  

---

## 1. Contexto de Negócio

A Diretoria da rede educacional está operando "no escuro" em relação a três pilares estratégicos: saúde financeira, rentabilidade de produtos (cursos) e retenção de alunos. Os dados atuais existem no sistema transacional da escola, mas são difíceis de extrair e cruzar. 

O objetivo deste projeto de dados é fornecer **visibilidade absoluta e automatizada** sobre as métricas-chave da instituição, permitindo tomadas de decisão baseadas em fatos e viabilizando o crescimento escalável do negócio.

---

## 2. Matriz de Requisitos Analíticos (As 3 Perguntas Vitais)

A arquitetura de dados (Camada Semântica) deve ser construída de forma a responder, com extrema precisão e velocidade, às seguintes perguntas de negócio:

### 2.1 Evolução da Receita Mensal
- **A Pergunta:** Qual é o valor financeiro total gerado por matrículas ao longo dos meses?
- **Métrica Principal:** `Receita Total (R$)`.
- **Fórmula de Negócio:** Soma do valor fixado no ato da matrícula (não o valor de catálogo atual, pois preços sofrem inflação/mudanças).
- **Dimensões / Agrupamentos:** Por `Ano` e `Mês`.
- **Origem do Dado Desejado:** Precisamos cruzar o histórico de matrículas com as dimensões de calendário de forma consistente.

### 2.2 Desempenho e Ticket Médio por Curso
- **A Pergunta:** Quais cursos trazem mais dinheiro para a escola em termos absolutos, e qual é o valor médio desembolsado por cada aluno em cada curso?
- **Métricas Principais:** `Receita por Curso (R$)` e `Ticket Médio (R$)`.
- **Fórmula de Negócio (Ticket Médio):** `(Receita Total do Curso) / (Quantidade de Alunos Matriculados no Curso)`.
- **Dimensões / Agrupamentos:** Por `Nome do Curso`.

### 2.3 Funil de Evasão (Status)
- **A Pergunta:** Como está a saúde da base de alunos atual? Estamos retendo os alunos ou há alta taxa de cancelamento?
- **Métrica Principal:** `Quantidade de Matrículas`.
- **Fórmula de Negócio (Taxa de Evasão):** `(Matrículas com Status de Evasão) / (Total de Matrículas)`.
- **Dimensões / Agrupamentos:** Por `Status da Matrícula` (Ativa, Concluída, Trancada, Cancelada).

---

## 3. Regras de Negócio (Business Rules & Data Quality)

Para que a Engenharia de Dados consiga desenhar a solução técnica correta, as seguintes regras devem ser rigorosamente atendidas na construção do Data Warehouse:

| Regra (BR) | Descrição e Impacto no Dado |
|---|---|
| **BR-01: Rastreamento Histórico de Preços** | O preço dos cursos sofre reajustes anuais ou por campanhas promocionais. Se o preço do catálogo for alterado hoje no sistema, **não podemos perder o histórico**. A receita do passado deve continuar refletindo o preço antigo cobrado do aluno na época. |
| **BR-02: Receita vs. Fluxo de Caixa** | Para fins deste relatório executivo, a "Receita" é reconhecida no momento da assinatura da matrícula (`data_matricula`), considerando o valor fixado no item. Não estamos mensurando fluxo de caixa (inadimplência ou a data efetiva do boleto pago) neste painel específico. |
| **BR-03: Definição de Evasão** | Os status que configuram evasão e acendem alerta para a área de retenção são exclusivamente: `Trancada` e `Cancelada`. O status `Concluída` indica sucesso acadêmico do aluno, não evasão. |

---

## 4. Requisitos Não Funcionais (SLAs e Integração)

- **Frequência de Atualização (SLA):** Os indicadores não precisam ser computados em tempo real (Real-Time). Uma carga em lote (Batch) rodando fora do horário comercial (ex: madrugada / D-1) é 100% suficiente para a gestão tática/estratégica da Diretoria.
- **Ferramentas de Consumo:** A entrega final do time de dados deve ser abstraída no formato de **Views Analíticas (SQL)** no banco de dados. A área de negócios usará ferramentas como Power BI, Metabase ou até Excel conectados diretamente nessas Views de forma "Plug-and-Play".
- **Imutabilidade Histórica:** Nenhuma métrica gerencial validada no passado pode sofrer alteração retrospectiva que corrompa o fechamento financeiro de meses anteriores, reforçando a necessidade de uma infraestrutura robusta de Data Warehousing.
