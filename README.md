# Modelagem e Arquitetura de Dados Educacional

## 🎯 O Desafio de Negócio (Mini-Case)

A Diretoria de uma rede educacional está enfrentando dificuldades para acompanhar a saúde financeira e o engajamento dos alunos. Eles possuem dados transacionais brutos de alunos, matrículas e cursos, mas precisam responder de forma rápida e confiável a três perguntas vitais:

1. **Evolução da Receita:** Qual é o valor total de matrículas geradas mês a mês?
2. **Ticket Médio:** Quais cursos geram o maior ticket médio e receita absoluta?
3. **Funil de Evasão:** Qual é a distribuição do status das matrículas (Ativas vs. Trancadas/Concluídas)?

## 🚀 A Solução e Objetivo do Projeto

Para resolver este problema, este projeto constrói uma **Arquitetura de Dados de ponta a ponta**, saindo do dado transacional bruto até a disponibilização de uma Camada Semântica pronta para o consumo da Diretoria (via ferramentas de BI).

O fluxo técnico construído (dentro do PostgreSQL) consiste em:

1. **Camada Operacional (OLTP em 2NF)**: Simula o sistema base, gerenciando o dia-a-dia transacional. Conta com um script de **Seed (Faker)** para gerar massa de dados sintéticos realista.
2. **Pipeline ETL**: Processo em Python que extrai dados do OLTP, aplica validações/transformações (via Pydantic) e carrega os resultados no DW.
3. **Camada Analítica (DW em Star Schema - Metodologia Kimball)**: Estrutura dimensional projetada para consolidar os dados (Tabela Fato e Dimensões).
4. **Camada Semântica (Views Analíticas)**: O produto final do projeto. Views em SQL que abstraem a complexidade do Star Schema, servindo os KPIs mastigados para responder diretamente às 3 perguntas de negócio da Diretoria.

## 🛠 Stack Tecnológico

- **Banco de Dados**: PostgreSQL (Schemas lógicos separados)
- **Linguagem Principal**: Python 3.12+
- **ORM**: SQLAlchemy
- **Validação de Dados**: Pydantic
- **Geração de Dados Sintéticos**: Faker
- **Gerenciamento de Dependências e Ambiente**: Poetry
- **Variáveis de Ambiente**: python-dotenv

## 📂 Estrutura do Projeto

O planejamento e a arquitetura do projeto estão inteiramente documentados. Para entender como o projeto é construído, acesse os arquivos na pasta `docs/`:

- **[BRD (Business Requirements Document)](docs/BRD.md)**: Levantamento dos requisitos de negócio, métricas, SLAs e o detalhamento do Mini-Case pela ótica da Diretoria.
- **[PRD (Product Requirements Document)](docs/PRD.md)**: A tradução do BRD em requisitos técnicos, arquitetura de dados e modelagem (O "Como vamos construir").
- **[Backlog](docs/BACKLOG.md)**: Plano de execução passo a passo dividido em Milestones e Issues.

*(As pastas de código `config/`, `models/`, `schemas/`, `tests/` e `etl/` estão sendo construídas de acordo com os marcos do Backlog).*

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

4. Configure seu arquivo `.env` baseado no `.env.example`.

5. Valide a conexão com o banco de dados e a infraestrutura de schemas:

   ```bash
   poetry run python tests/test_database.py
   ```

6. Acompanhe a evolução e as próximas etapas lendo o arquivo `docs/BACKLOG.md`.
