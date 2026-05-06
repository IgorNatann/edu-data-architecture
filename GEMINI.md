# GEMINI.md

## Projeto: Modelagem de Dados para Iniciantes (Setor Educacional)

Este projeto tem como objetivo criar uma modelagem de dados simples, clara e bem documentada para um sistema de gestão educacional, ideal para quem está começando na área de dados.

O foco principal é aprender a transformar processos educacionais em uma estrutura de banco de dados organizada.

---

## Objetivo do Projeto

Criar uma arquitetura de dados end-to-end (focada em resolver um Mini-Case de negócio da Diretoria) contendo:

- Entendimento do problema de negócio (Receita, Ticket Médio e Evasão)
- Criação da Camada Operacional (OLTP em 2NF) simulando o transacional
- Geração de dados sintéticos realistas (Seed via Faker)
- Pipeline ETL (Python + Pydantic para validação)
- Criação da Camada Analítica (DW em Star Schema - Kimball)
- Criação da Camada Semântica (Views Analíticas em SQL) para entregar o dado pronto para consumo de BI

---

## Contexto do Projeto

O projeto será baseado em um sistema simples de gestão de cursos.

Uma escola deseja controlar:

- Alunos
- Cursos
- Matrículas
- Itens de Matrícula (Cursos incluídos em uma matrícula)
- Pagamentos

---

## Regras de Negócio

1. Um aluno pode realizar várias matrículas ao longo do tempo.
2. Uma matrícula pertence a apenas um aluno.
3. Uma matrícula pode englobar um ou mais cursos (ex: pacotes promocionais).
4. Um curso pode estar associado a várias matrículas de diferentes alunos.
5. Cada matrícula possui um registro de pagamento para controle financeiro.
6. Cada item de matrícula deve registrar o preço do curso no momento da inscrição.

---

## Entidades Principais

### Aluno

Representa um estudante matriculado na instituição.

Campos sugeridos:

- id_aluno
- nome
- email
- cpf
- data_nascimento
- data_cadastro

### Curso

Representa uma formação ou disciplina oferecida pela escola.

Campos sugeridos:

- id_curso
- nome_curso
- descricao
- preco
- carga_horaria
- data_criacao

### Matrícula

Representa o vínculo formal de um aluno com a instituição em um determinado momento.

Campos sugeridos:

- id_matricula
- id_aluno
- data_matricula
- status (Ativa, Trancada, Concluída)
- valor_total

### Item da Matrícula

Representa os cursos específicos incluídos em uma matrícula.

Campos sugeridos:

- id_item_matricula
- id_matricula
- id_curso
- preco_momento (preço aplicado na venda)
- data_inicio_prevista

### Pagamento

Representa a quitação financeira de uma matrícula.

Campos sugeridos:

- id_pagamento
- id_matricula
- forma_pagamento
- valor_pago
- data_pagamento
- status_pagamento

---

## Relacionamentos

### Aluno e Matrícula

- Um aluno pode ter muitas matrículas.
- Uma matrícula pertence a um aluno.
- Relacionamento: 1:N

### Matrícula e Item da Matrícula

- Uma matrícula pode ter muitos itens.
- Um item pertence a uma matrícula.
- Relacionamento: 1:N

### Curso e Item da Matrícula

- Um curso pode aparecer em muitos itens de matrícula.
- Um item de matrícula está relacionado a um curso.
- Relacionamento: 1:N

### Matrícula e Pagamento

- Uma matrícula possui um registro de pagamento.
- Um pagamento pertence a uma matrícula.
- Relacionamento: 1:1

---

## Modelo Conceitual

Entidades:

- Aluno
- Curso
- Matrícula
- Item da Matrícula
- Pagamento

Relacionamentos:

- Aluno realiza Matrícula
- Matrícula possui Item da Matrícula
- Curso compõe Item da Matrícula
- Matrícula possui Pagamento

---

## Modelo Lógico

### aluno

| Campo | Tipo | Chave |
|---|---|---|
| id_aluno | inteiro | PK |
| nome | texto |  |
| email | texto |  |
| cpf | texto |  |
| data_nascimento | data |  |
| data_cadastro | data |  |

### curso

| Campo | Tipo | Chave |
|---|---|---|
| id_curso | inteiro | PK |
| nome_curso | texto |  |
| descricao | texto |  |
| preco | decimal |  |
| carga_horaria | inteiro |  |
| data_criacao | data |  |

### matricula

| Campo | Tipo | Chave |
|---|---|---|
| id_matricula | inteiro | PK |
| id_aluno | inteiro | FK |
| data_matricula | data |  |
| status | texto |  |
| valor_total | decimal |  |

### item_matricula

| Campo | Tipo | Chave |
|---|---|---|
| id_item_matricula | inteiro | PK |
| id_matricula | inteiro | FK |
| id_curso | inteiro | FK |
| preco_momento | decimal |  |
| data_inicio_prevista | data |  |

### pagamento

| Campo | Tipo | Chave |
|---|---|---|
| id_pagamento | inteiro | PK |
| id_matricula | inteiro | FK |
| forma_pagamento | texto |  |
| valor_pago | decimal |  |
| data_pagamento | data |  |
| status_pagamento | texto |  |

---

## Modelo Físico em SQL

```sql
CREATE TABLE aluno (
    id_aluno INTEGER PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    cpf VARCHAR(14) UNIQUE,
    data_nascimento DATE,
    data_cadastro DATE DEFAULT CURRENT_DATE
);

CREATE TABLE curso (
    id_curso INTEGER PRIMARY KEY,
    nome_curso VARCHAR(100) NOT NULL,
    descricao TEXT,
    preco DECIMAL(10,2) NOT NULL,
    carga_horaria INTEGER NOT NULL,
    data_criacao DATE DEFAULT CURRENT_DATE
);

CREATE TABLE matricula (
    id_matricula INTEGER PRIMARY KEY,
    id_aluno INTEGER NOT NULL,
    data_matricula DATE NOT NULL,
    status VARCHAR(30) DEFAULT 'Ativa',
    valor_total DECIMAL(10,2),
    FOREIGN KEY (id_aluno) REFERENCES aluno(id_aluno)
);

CREATE TABLE item_matricula (
    id_item_matricula INTEGER PRIMARY KEY,
    id_matricula INTEGER NOT NULL,
    id_curso INTEGER NOT NULL,
    preco_momento DECIMAL(10,2) NOT NULL,
    data_inicio_prevista DATE,
    FOREIGN KEY (id_matricula) REFERENCES matricula(id_matricula),
    FOREIGN KEY (id_curso) REFERENCES curso(id_curso)
);

CREATE TABLE pagamento (
    id_pagamento INTEGER PRIMARY KEY,
    id_matricula INTEGER NOT NULL,
    forma_pagamento VARCHAR(50),
    valor_pago DECIMAL(10,2),
    data_pagamento DATE,
    status_pagamento VARCHAR(30),
    FOREIGN KEY (id_matricula) REFERENCES matricula(id_matricula)
);
```

---

## Status Atual do Projeto (Acompanhamento de Contexto)

> **⚠️ Atenção IA:** Sempre leia esta seção ao iniciar uma nova sessão e atualize-a ao finalizar uma entrega relevante. Isso garante a continuidade do desenvolvimento.

- **Fase Atual:** Milestone 5 - Geração de Dados (Seed) e Pipeline ETL
- **Última Ação Realizada:** Finalizamos a Issue #9 criando o pipeline ETL (`etl/load_fato_matricula.py`) que extrai dados do schema `oltp` via SQLAlchemy (eager loading), carrega as dimensões `dim_aluno`, `dim_curso` e `dim_status` no schema `dw`, transforma os dados via Pydantic (`FatoMatriculaTransform` / `FatoMatriculaSchema`), e insere na `fato_matricula` com granularidade por **item de matrícula** (1 linha por par matrícula-curso, seguindo Kimball).
- **O que está em aberto (Próximo Passo):**
  - [ ] **Issue #10 (Milestone 5):** Validação Analítica — Queries SQL de sanidade contra o DW para garantir a corretude dos dados inseridos pelo ETL.
- **Aviso:** O gerenciamento do ambiente e dependências é feito via **Poetry**.
