# PRD — Modelagem e Arquitetura de Dados Educacional

> **Versão:** 1.0  
> **Data:** 2026-04-29  
> **Nível:** Intermediário  
> **Status:** Em Revisão

---

## 1. Sumário Executivo

### 1.1 O Desafio de Negócio (Mini-Case)

A Diretoria de uma escola precisa acompanhar a saúde financeira e o engajamento dos alunos de forma ágil, respondendo a perguntas vitais como: a evolução da receita mensal, o ticket médio por curso e a taxa de evasão (status de matrículas). 
Atualmente, os dados estão presos em tabelas operacionais puras, impossibilitando análises rápidas e consistentes por parte da gestão executiva.

### 1.2 Solução Proposta

Desenvolver uma **arquitetura de dados end-to-end** dentro de um único banco PostgreSQL, que não apenas sustente a operação, mas entregue valor analítico imediato na ponta. O fluxo proposto é:

- **Camada OLTP (2NF)** — banco operacional simulando a operação diária.
- **Pipeline ETL (Python/SQLAlchemy)** — movimenta e transforma os dados.
- **Camada DW / Data Mart (Star Schema)** — estrutura analítica robusta baseada na metodologia de Kimball.
- **Camada Semântica (Views Analíticas)** — *data products* finais em SQL (ex: `vw_receita_mensal`) prontos para consumo por ferramentas de BI, respondendo diretamente às perguntas da Diretoria.

### 1.3 Critérios de Sucesso

| # | Critério | Métrica |
|---|---|---|
| 1 | Modelo OLTP em 2NF | 5 tabelas funcionando no PostgreSQL com constraints e FKs |
| 2 | Star Schema completo | 4 dimensões + 1 tabela fato populados via ETL |
| 3 | ETL funcional | Pipeline Python/SQLAlchemy + Pydantic executando sem erros |
| 4 | Documentação completa | Modelos conceitual, lógico e físico documentados para OLTP e DW |

---

## 2. Experiência do Usuário e Funcionalidade

### 2.1 Personas

| Persona | Descrição | Necessidade |
|---|---|---|
| **Analista de Dados Iniciante/Intermediário** | Profissional aprendendo modelagem de dados | Entender como transformar processos reais em estruturas de banco |
| **Gestor Educacional** | Coordenador da escola | Consultar KPIs de matrículas, receita e desempenho |

### 2.2 User Stories

#### OLTP (Operacional)

| ID | Story | Critério de Aceite |
|---|---|---|
| US-01 | Como gestor, quero cadastrar alunos para manter o registro atualizado | Tabela `aluno` aceita INSERT com validação de CPF e email únicos |
| US-02 | Como gestor, quero registrar cursos oferecidos pela escola | Tabela `curso` armazena nome, preço e carga horária |
| US-03 | Como gestor, quero criar matrículas vinculando aluno a um ou mais cursos | Matrícula criada com itens e preço registrado no momento da inscrição |
| US-04 | Como gestor, quero registrar pagamentos das matrículas | Tabela `pagamento` vinculada 1:1 com matrícula |

#### DW (Analítico)

| ID | Story | Critério de Aceite |
|---|---|---|
| US-05 | Como analista, quero consultar o total de matrículas por período | `fato_matricula` + `dim_tempo` retorna agregações por mês/trimestre/ano |
| US-06 | Como analista, quero analisar ticket médio por curso | `fato_matricula` + `dim_curso` calcula valor médio por curso |
| US-07 | Como analista, quero ver a distribuição de status das matrículas | `fato_matricula` + `dim_status` agrupa por Ativa/Trancada/Concluída |

### 2.3 Non-Goals (Fora do Escopo)

- ❌ Dashboard ou frontend de visualização (Foco 100% em Engenharia/Arquitetura de Dados, entregando Views Analíticas no banco)
- ❌ API REST
- ❌ Autenticação de usuários
- ❌ Segunda tabela fato (`fato_pagamento`) — versão futura
- ❌ Migrations com Alembic
- ❌ Testes automatizados

---

## 3. Especificações Técnicas

### 3.1 Stack Tecnológico

| Componente | Tecnologia | Papel |
|---|---|---|
| Banco de Dados | PostgreSQL (Render) | Armazenamento OLTP e DW |
| ORM | SQLAlchemy | Mapeamento objeto-relacional e persistência |
| Validação/Transformação | Pydantic | Validação de tipos e transformação de dados no ETL |
| Geração de Dados | Faker | Geração de dados sintéticos realistas para o Seed |
| Linguagem | Python | Linguagem principal do projeto |
| Separação de Camadas | PG Schemas (`oltp`, `dw`) | Isolamento lógico entre operacional e analítico |

### 3.2 Arquitetura Geral

```
┌──────────────────────────────────────────────────────────┐
│                   PostgreSQL (Render)                     │
│                                                           │
│  ┌──────────────────┐        ┌─────────────────────┐     │
│  │  Schema: oltp     │        │  Schema: dw          │    │
│  │  (2NF)            │        │  (Star Schema)       │    │
│  │                   │        │                      │    │
│  │  ├── aluno        │        │  ├── dim_aluno       │    │
│  │  ├── curso        │        │  ├── dim_curso       │    │
│  │  ├── matricula    │        │  ├── dim_tempo       │    │
│  │  ├── item_matricula│       │  ├── dim_status      │    │
│  │  └── pagamento    │        │  └── fato_matricula  │    │
│  └────────┬─────────┘        └──────────▲───────────┘    │
│           │                              │                │
│           │   ┌──────────────────────┐   │                │
│           │   │   ETL (Python)        │   │                │
│           │   │                      │   │                │
│           └──▶│  1. Extract (SQLAlchemy) │                │
│               │  2. Transform (Pydantic) │                │
│               │  3. Load (SQLAlchemy) │──┘                │
│               └──────────────────────┘                    │
└──────────────────────────────────────────────────────────┘
```

### 3.3 Estrutura do Projeto

```
projeto/
├── config/
│   └── database.py            # Conexão PostgreSQL / Engine SQLAlchemy
├── models/
│   ├── __init__.py
│   ├── oltp/                  # Modelos SQLAlchemy (2NF)
│   │   ├── __init__.py
│   │   ├── aluno.py
│   │   ├── curso.py
│   │   ├── matricula.py
│   │   ├── item_matricula.py
│   │   └── pagamento.py
│   └── dw/                    # Modelos SQLAlchemy (Star Schema)
│       ├── __init__.py
│       ├── dim_aluno.py
│       ├── dim_curso.py
│       ├── dim_tempo.py
│       ├── dim_status.py
│       └── fato_matricula.py
├── schemas/                    # Schemas Pydantic (Validação e Transformação)
│   ├── __init__.py
│   ├── aluno_schema.py        # Validação de dados do aluno
│   ├── curso_schema.py        # Validação de dados do curso
│   ├── matricula_schema.py    # Validação de dados da matrícula
│   └── fato_matricula_schema.py # Transformação OLTP → DW
├── etl/
│   └── load_fato_matricula.py # Pipeline ETL OLTP → DW
├── scripts/
│   └── seed_data.py           # Dados de exemplo para popular o OLTP
├── docs/
│   ├── PRD.md                 # Este documento
│   └── modelagem/
│       ├── oltp_modelagem.md  # Documentação da modelagem OLTP
│       └── dw_modelagem.md    # Documentação da modelagem DW
├── pyproject.toml
├── poetry.lock
└── GEMINI.md
```

---

## 4. Modelagem de Dados — Raciocínio e Decisões

> Esta seção documenta o **pensamento** por trás de cada decisão de modelagem.

### 4.1 Camada OLTP — Raciocínio

#### Por que 2NF (Segunda Forma Normal)?

A 2NF foi escolhida como equilíbrio entre organização e simplicidade:

- **1NF** → Elimina grupos repetitivos (já atendido pela estrutura relacional)
- **2NF** → Elimina dependências parciais (todo atributo não-chave depende da chave inteira)
- Não avançamos para 3NF porque adicionaria complexidade sem benefício claro para este domínio

#### Decisões de Design OLTP

| Decisão | Raciocínio |
|---|---|
| `item_matricula` como entidade separada | Resolve o relacionamento N:N entre Matrícula e Curso, e permite registrar `preco_momento` |
| `preco_momento` no item, não no curso | O preço pode mudar ao longo do tempo; registramos o preço no ato da matrícula |
| `pagamento` 1:1 com matrícula | Simplifica o controle financeiro; cada matrícula tem um único registro de pagamento |
| CPF e email como UNIQUE | Garante integridade dos dados do aluno sem duplicação |
| Status como VARCHAR, não ENUM | Flexibilidade para adicionar novos status sem ALTER TYPE |

---

#### 4.1.1 Modelo Conceitual OLTP

**Entidades identificadas a partir do domínio:**

```
[ALUNO] ──(realiza)──→ [MATRÍCULA] ──(possui)──→ [ITEM MATRÍCULA] ←──(compõe)── [CURSO]
                            │
                            └──(gera)──→ [PAGAMENTO]
```

**Regras de negócio mapeadas:**

- Aluno (1) → (N) Matrícula
- Matrícula (1) → (N) Item Matrícula
- Curso (1) → (N) Item Matrícula
- Matrícula (1) → (1) Pagamento

---

#### 4.1.2 Modelo Lógico OLTP

##### aluno

| Campo | Tipo | Chave | Restrição |
|---|---|---|---|
| id_aluno | INTEGER | PK | AUTO INCREMENT |
| nome | VARCHAR(100) | — | NOT NULL |
| email | VARCHAR(100) | — | UNIQUE |
| cpf | VARCHAR(14) | — | UNIQUE |
| data_nascimento | DATE | — | — |
| data_cadastro | DATE | — | DEFAULT CURRENT_DATE |

##### curso

| Campo | Tipo | Chave | Restrição |
|---|---|---|---|
| id_curso | INTEGER | PK | AUTO INCREMENT |
| nome_curso | VARCHAR(100) | — | NOT NULL |
| descricao | TEXT | — | — |
| preco | DECIMAL(10,2) | — | NOT NULL |
| carga_horaria | INTEGER | — | NOT NULL |
| data_criacao | DATE | — | DEFAULT CURRENT_DATE |

##### matricula

| Campo | Tipo | Chave | Restrição |
|---|---|---|---|
| id_matricula | INTEGER | PK | AUTO INCREMENT |
| id_aluno | INTEGER | FK → aluno | NOT NULL |
| data_matricula | DATE | — | NOT NULL |
| status | VARCHAR(30) | — | DEFAULT 'Ativa' |
| valor_total | DECIMAL(10,2) | — | — |

##### item_matricula

| Campo | Tipo | Chave | Restrição |
|---|---|---|---|
| id_item_matricula | INTEGER | PK | AUTO INCREMENT |
| id_matricula | INTEGER | FK → matricula | NOT NULL |
| id_curso | INTEGER | FK → curso | NOT NULL |
| preco_momento | DECIMAL(10,2) | — | NOT NULL |
| data_inicio_prevista | DATE | — | — |

##### pagamento

| Campo | Tipo | Chave | Restrição |
|---|---|---|---|
| id_pagamento | INTEGER | PK | AUTO INCREMENT |
| id_matricula | INTEGER | FK → matricula | NOT NULL, UNIQUE |
| forma_pagamento | VARCHAR(50) | — | — |
| valor_pago | DECIMAL(10,2) | — | — |
| data_pagamento | DATE | — | — |
| status_pagamento | VARCHAR(30) | — | — |

> **Nota:** `id_matricula` em `pagamento` é UNIQUE para garantir o relacionamento 1:1.

---

### 4.2 Camada DW — Raciocínio

#### Por que Star Schema?

- **Simplicidade de consulta** — JOINs diretos entre fato e dimensões, sem cascatas
- **Performance analítica** — Otimizado para agregações (SUM, AVG, COUNT, GROUP BY)
- **Padrão de mercado** — Modelo dimensional de Kimball, amplamente usado em Data Warehouses

#### Decisões de Design DW

| Decisão | Raciocínio |
|---|---|
| `dim_tempo` como dimensão separada | Permite análises temporais ricas (mês, trimestre, dia da semana) sem cálculos em runtime |
| `dim_status` como dimensão | Evita strings repetidas na fato; permite futuras expansões (descrições, agrupamentos) |
| Surrogate keys (SK) nas dimensões | Desacopla o DW do OLTP; permite versionamento futuro (SCD) |
| Métricas na `fato_matricula` | `valor_total`, `qtd_cursos` pré-calculados para performance |

---

#### 4.2.1 Modelo Conceitual DW

```
                    ┌───────────┐
                    │ dim_tempo  │
                    └─────┬─────┘
                          │
┌───────────┐    ┌────────┴────────┐    ┌───────────┐
│ dim_aluno  │───│ fato_matricula   │───│ dim_curso  │
└───────────┘    └────────┬────────┘    └───────────┘
                          │
                    ┌─────┴─────┐
                    │ dim_status │
                    └───────────┘
```

**Granularidade da fato:** Uma linha por matrícula (nível de matrícula).

---

#### 4.2.2 Modelo Lógico DW

##### dim_aluno

| Campo | Tipo | Chave | Descrição |
|---|---|---|---|
| sk_aluno | INTEGER | PK | Surrogate key |
| nk_aluno | INTEGER | NK | Natural key (id_aluno do OLTP) |
| nome | VARCHAR(100) | — | Nome do aluno |
| email | VARCHAR(100) | — | Email do aluno |
| data_nascimento | DATE | — | Data de nascimento |
| data_carga | TIMESTAMP | — | Data/hora da carga ETL |

##### dim_curso

| Campo | Tipo | Chave | Descrição |
|---|---|---|---|
| sk_curso | INTEGER | PK | Surrogate key |
| nk_curso | INTEGER | NK | Natural key (id_curso do OLTP) |
| nome_curso | VARCHAR(100) | — | Nome do curso |
| carga_horaria | INTEGER | — | Carga horária |
| preco_catalogo | DECIMAL(10,2) | — | Preço atual do catálogo |
| data_carga | TIMESTAMP | — | Data/hora da carga ETL |

##### dim_tempo

| Campo | Tipo | Chave | Descrição |
|---|---|---|---|
| sk_tempo | INTEGER | PK | Surrogate key |
| data_completa | DATE | — | Data completa (YYYY-MM-DD) |
| ano | INTEGER | — | Ano (ex: 2026) |
| mes | INTEGER | — | Mês (1-12) |
| dia | INTEGER | — | Dia do mês |
| trimestre | INTEGER | — | Trimestre (1-4) |
| nome_mes | VARCHAR(20) | — | Nome do mês (Janeiro, Fevereiro...) |
| dia_semana | VARCHAR(20) | — | Dia da semana (Segunda, Terça...) |

##### dim_status

| Campo | Tipo | Chave | Descrição |
|---|---|---|---|
| sk_status | INTEGER | PK | Surrogate key |
| codigo_status | VARCHAR(30) | — | Código (Ativa, Trancada, Concluída) |
| descricao_status | VARCHAR(100) | — | Descrição longa do status |

##### fato_matricula

| Campo | Tipo | Chave | Descrição |
|---|---|---|---|
| sk_matricula | INTEGER | PK | Surrogate key da fato |
| nk_matricula | INTEGER | — | Natural key (id_matricula do OLTP) |
| sk_aluno | INTEGER | FK → dim_aluno | Referência à dimensão aluno |
| sk_curso | INTEGER | FK → dim_curso | Referência à dimensão curso |
| sk_tempo | INTEGER | FK → dim_tempo | Referência à dimensão tempo |
| sk_status | INTEGER | FK → dim_status | Referência à dimensão status |
| valor_total | DECIMAL(10,2) | — | Valor total da matrícula |
| qtd_cursos | INTEGER | — | Quantidade de cursos na matrícula |
| valor_medio_curso | DECIMAL(10,2) | — | Ticket médio por curso |

---

## 5. Riscos e Roadmap

### 5.1 Roadmap Faseado

| Fase | Escopo | Entregáveis |
|---|---|---|
| **Fase 1 — Modelagem** | Documentação dos 3 modelos (conceitual, lógico, físico) para OLTP e DW | Docs completos em `docs/modelagem/` |
| **Fase 2 — OLTP** | Implementar modelos SQLAlchemy + criar tabelas no PG | Modelos em `models/oltp/`, schema criado |
| **Fase 3 — Schemas Pydantic** | Criar schemas de validação e transformação | Schemas em `schemas/` |
| **Fase 4 — DW** | Implementar modelos SQLAlchemy do Star Schema | Modelos em `models/dw/`, schema criado |
| **Fase 5 — ETL** | Pipeline Python (Extract → Pydantic Transform → Load) | Script em `etl/load_fato_matricula.py` |
| **Fase 6 — Seed & Validação** | Popular OLTP com dados sintéticos (Faker) e validar ETL | Script `seed_data.py`, queries de validação |
| **Fase 7 — Camada Semântica** | Criar Views Analíticas em SQL para responder às perguntas de negócio | Scripts SQL na pasta `docs/kpis/` |

### 5.2 Riscos Técnicos

| Risco | Impacto | Mitigação |
|---|---|---|
| Tier gratuito do Render pode ter limitações de conexão | Médio | Usar connection pooling no SQLAlchemy |
| Surrogate keys no DW desalinhadas com OLTP | Baixo | Manter natural keys (NK) em todas as dimensões |
| `dim_tempo` precisa de range pré-definido | Baixo | Gerar 5 anos de datas (2024-2029) no seed |

---

## 6. Frentes de Desenvolvimento (Step-by-Step)

> Cada frente será desenvolvida e documentada sequencialmente.

### Frente 1: Modelagem OLTP
1. Documentar raciocínio da 2NF
2. Criar modelo conceitual (entidades e relacionamentos)
3. Criar modelo lógico (tabelas, tipos, chaves)
4. Criar modelo físico (DDL SQL para PostgreSQL)

### Frente 2: Modelagem DW
1. Documentar raciocínio do Star Schema
2. Definir granularidade da tabela fato
3. Criar modelo conceitual (fato + dimensões)
4. Criar modelo lógico (campos, SKs, NKs)
5. Criar modelo físico (DDL SQL para PostgreSQL)

### Frente 3: Implementação OLTP
1. Configurar conexão PostgreSQL (database.py)
2. Implementar modelos SQLAlchemy para schema `oltp`
3. Criar tabelas no banco

### Frente 4: Implementação DW
1. Implementar modelos SQLAlchemy para schema `dw`
2. Criar tabelas no banco

### Frente 5: Schemas Pydantic
1. Criar schemas de validação para entidades OLTP (aluno, curso, matrícula)
2. Criar schema de transformação para `fato_matricula` (com `@computed_field` e `@field_validator`)
3. Documentar regras de validação e transformação

### Frente 6: ETL + Seed
1. Criar script de seed usando Faker para popular OLTP com dados realistas
2. Implementar pipeline ETL: Extract (SQLAlchemy) → Transform (Pydantic) → Load (SQLAlchemy)
3. Validar dados no DW com queries analíticas
