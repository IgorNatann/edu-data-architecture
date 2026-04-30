# Backlog do Projeto: Modelagem e Arquitetura de Dados Educacional

Este documento organiza o plano de execução do projeto, dividindo o trabalho detalhado no `PRD.md` em Milestones (Marcos) e Issues (Tarefas) acionáveis. Ele deve ser atualizado conforme o progresso do desenvolvimento.

---

## 📌 Visão Geral das Entregas (Milestones)

- [x] **Milestone 1**: Planejamento e Documentação Inicial (PRD, Modelagem, Backlog)
- [ ] **Milestone 2**: Banco de Dados Operacional (OLTP)
- [ ] **Milestone 3**: Banco de Dados Analítico (DW)
- [ ] **Milestone 4**: Schemas de Validação e Transformação (Pydantic)
- [ ] **Milestone 5**: Geração de Dados (Seed) e Pipeline ETL
- [ ] **Milestone 6**: Disponibilização de Dados (Camada Semântica)

---

## 📝 Issues Detalhadas (Plano de Execução)

### Milestone 2: Banco de Dados Operacional (OLTP)
*Foco: Estabelecer a base transacional 2NF da escola.*

- [x] **Issue #1: Configuração Base do SQLAlchemy**
  - Configurar `config/database.py`.
  - Criar base declarativa e configurar URL de conexão com o PostgreSQL do Render usando variáveis de ambiente.
  - Implementar sessão do banco.

- [ ] **Issue #2: Implementar Modelos OLTP**
  - Criar os modelos em `models/oltp/`:
    - `aluno.py`
    - `curso.py`
    - `matricula.py`
    - `item_matricula.py`
    - `pagamento.py`
  - Garantir que todos usem o schema `oltp` no PostgreSQL.
  - Configurar as *Foreign Keys* e relacionamentos (*relationships* do SQLAlchemy).

- [ ] **Issue #3: Criação das Tabelas OLTP no Banco**
  - Criar um script para inicializar o banco de dados e as tabelas operacionais.
  - Testar a criação executando contra o banco no Render.

---

### Milestone 3: Banco de Dados Analítico (DW)
*Foco: Estabelecer a estrutura Star Schema (Modelagem Kimball) para análises e KPIs.*

- [ ] **Issue #4: Implementar Modelos DW (Star Schema)**
  - Criar os modelos em `models/dw/`:
    - `dim_aluno.py` (SK, NK, campos descritivos)
    - `dim_curso.py` (SK, NK, campos descritivos)
    - `dim_tempo.py` (SK, granularidade de dias/meses/anos)
    - `dim_status.py` (SK, NK)
    - `fato_matricula.py` (SKs e métricas como `valor_total` e `qtd_cursos`)
  - Garantir que todos usem o schema `dw` no PostgreSQL.

- [ ] **Issue #5: Criação das Tabelas DW no Banco**
  - Atualizar o script de inicialização do banco para incluir a criação do schema `dw` e suas tabelas.

---

### Milestone 4: Schemas de Validação e Transformação
*Foco: Construir a camada de validação e transformação dos dados entre OLTP e DW usando Pydantic.*

- [ ] **Issue #6: Criar Schemas de Validação OLTP**
  - Em `schemas/`:
    - `aluno_schema.py`
    - `curso_schema.py`
    - `matricula_schema.py`
  - Incluir regras simples como validação de CPF e tipos corretos.

- [ ] **Issue #7: Criar Schema de Transformação da Fato**
  - Em `schemas/fato_matricula_schema.py`.
  - Configurar o modelo que recebe os dados "crus" do OLTP e gera as métricas calculadas (`valor_total`, `qtd_cursos`, etc.) via `@computed_field` ou métodos customizados para carregar a `fato_matricula`.

---

### Milestone 5: Geração de Dados (Seed) e Pipeline ETL
*Foco: Popular a base com dados realistas e movimentá-los para a camada analítica.*

- [ ] **Issue #8: Script de Geração de Dados (Seed) com Faker**
  - Em `scripts/seed_data.py`.
  - Usar a biblioteca `Faker` para gerar:
    - 50 Alunos.
    - 10 Cursos com preços e cargas horárias variadas.
    - 100 Matrículas distribuídas ao longo de 2 anos (e.g., 2023-2024).
    - Itens de matrícula aleatórios.
    - Pagamentos correspondentes.
  - Inserir tudo no schema `oltp`.
  - Gerar a carga da tabela `dim_tempo` para 5 anos (2020-2025).

- [ ] **Issue #9: Pipeline ETL (Extract, Transform, Load)**
  - Em `etl/load_fato_matricula.py`.
  - **Extract**: Ler as matrículas, alunos e cursos do schema `oltp` usando SQLAlchemy.
  - **Transform**: Passar os dados pelos schemas do Pydantic para validação e cálculo das métricas.
  - **Load**: Inserir os registros transformados na `fato_matricula` no schema `dw`.

- [ ] **Issue #10: Validação Analítica**
  - Rodar consultas SQL básicas contra as tabelas do `dw` para garantir a corretude dos dados inseridos pelo ETL.
  - Documentar algumas *queries* úteis (ex: receita por mês).

---

### Milestone 6: Disponibilização de Dados (Camada Semântica)
*Foco: Encapsular a complexidade do DW em Views analíticas prontas para o consumo do negócio, respondendo diretamente ao Mini-Case.*

- [ ] **Issue #11: Criar Views Analíticas (KPIs)**
  - Na pasta `docs/kpis/`, armazenar os scripts SQL (`receita_mensal.sql`, `desempenho_cursos.sql`, `funil_evasao.sql`).
  - Executar a criação das `CREATE VIEW vw_...` no schema `dw` para entregar o dado mastigado (Camada Semântica).

---

## 🚀 Fluxo de Trabalho (Como usar)
1. **Escolha uma Issue** do Milestone atual.
2. **Execute o código** correspondente.
3. **Marque com um `[x]`** no Backlog quando concluído e testado.
4. **Atualize o `GEMINI.md`**: Sempre edite a seção "Status Atual do Projeto" no arquivo `GEMINI.md` para refletir a Issue finalizada e qual é o novo Próximo Passo.
5. Avance para a próxima Issue!
