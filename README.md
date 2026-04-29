# Modelagem e Arquitetura de Dados Educacional

Este projeto tem como objetivo criar uma arquitetura de dados completa para um sistema de gestão educacional (escola/cursos). O foco principal é demonstrar na prática a modelagem e transformação de processos educacionais em uma estrutura de banco de dados robusta, separando a carga operacional (OLTP) da carga analítica (DW).

## 🚀 Objetivo do Projeto

Construir uma arquitetura em duas camadas dentro do PostgreSQL:
1. **Camada Operacional (OLTP em 2NF)**: Responsável por gerenciar o dia-a-dia transacional (Alunos, Cursos, Matrículas, Pagamentos).
2. **Camada Analítica (DW em Star Schema - Metodologia Kimball)**: Estrutura dimensional projetada para consultas rápidas, KPIs e relatórios gerenciais (Tabela Fato e Dimensões).
3. **Pipeline ETL**: Script que extrai dados do OLTP, aplica validações e transformações (via Pydantic) e carrega os resultados no DW.
4. **Seed de Dados**: Script que gera massa de dados sintéticos realistas utilizando a biblioteca Faker.

## 🛠 Stack Tecnológico

- **Banco de Dados**: PostgreSQL (Schemas lógicos separados)
- **Linguagem Principal**: Python 3
- **ORM**: SQLAlchemy
- **Validação de Dados**: Pydantic
- **Geração de Dados Sintéticos**: Faker
- **Gerenciamento de Dependências e Ambiente**: Poetry
- **Variáveis de Ambiente**: python-dotenv

## 📂 Estrutura do Projeto

O planejamento e a arquitetura do projeto estão inteiramente documentados. Para entender como o projeto é construído, acesse os arquivos na pasta `docs/`:

- **[PRD (Product Requirements Document)](docs/PRD.md)**: Visão completa do produto, regras de negócio e arquitetura detalhada.
- **[Backlog](docs/BACKLOG.md)**: Plano de execução passo a passo dividido em Milestones e Issues.

*(As pastas de código `config/`, `models/`, `schemas/`, e `etl/` estão sendo construídas de acordo com os marcos do Backlog).*

## 🚦 Como Iniciar

Se quiser rodar o projeto localmente e acompanhar a evolução:

1. Clone o repositório:
   ```bash
   git clone <url-do-repositorio>
   cd edu-data-architecture
   ```

2. Instale as dependências usando o [Poetry](https://python-poetry.org/):
   ```bash
   poetry install
   ```

3. Ative o ambiente virtual do Poetry:
   ```bash
   poetry shell
   ```

4. Acompanhe a evolução e as próximas etapas lendo o arquivo `docs/BACKLOG.md`.
