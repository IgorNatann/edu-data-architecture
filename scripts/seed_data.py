"""
Script de Geracao de Dados Sinteticos (Seed) — Issue #8

Popula o schema 'oltp' com dados realistas gerados via Faker e cria a
dimensao 'dim_tempo' no schema 'dw'. As demais dimensoes e a tabela fato
serao carregadas pelo pipeline ETL (Issue #9).

VOLUMES GERADOS:
    - 50 Alunos
    - 10 Cursos (lista fixa com nomes realistas)
    - 100 Matriculas (distribuidas entre 2023-2024)
    - ~210 Itens de Matricula (1 a 4 cursos por matricula)
    - 100 Pagamentos (1 por matricula, status correlacionado)
    - ~2.192 registros na dim_tempo (2020-2025)

IDEMPOTENCIA:
    O script limpa todos os dados existentes antes de inserir, respeitando a
    ordem de dependencia das Foreign Keys. Pode ser executado multiplas vezes
    com seguranca.

EXECUCAO:
    poetry run python scripts/seed_data.py
"""

import sys
import os
import random
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

from faker import Faker

# Ajuste de path para importar modulos do projeto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.database import SessionLocal
from models.oltp import Aluno, Curso, Matricula, ItemMatricula, Pagamento
from models.dw import DimTempo

# Inicializa o Faker com locale brasileiro
fake = Faker('pt_BR')

# Semente fixa para reprodutibilidade dos dados gerados
SEED = 42
Faker.seed(SEED)
random.seed(SEED)

# ============================================================================
# CONSTANTES DE CONFIGURACAO
# ============================================================================

# Lista fixa de 10 cursos realistas do setor educacional de dados
CURSOS_CATALOGO = [
    {
        "nome_curso": "Python para Dados",
        "descricao": "Fundamentos de Python aplicados a analise e manipulacao de dados.",
        "preco": Decimal("497.00"),
        "carga_horaria": 60,
    },
    {
        "nome_curso": "SQL Avançado",
        "descricao": "Consultas complexas, CTEs, window functions e otimizacao de queries.",
        "preco": Decimal("397.00"),
        "carga_horaria": 40,
    },
    {
        "nome_curso": "Excel para Negócios",
        "descricao": "Dashboards, tabelas dinamicas e automacao com VBA para o dia a dia corporativo.",
        "preco": Decimal("197.00"),
        "carga_horaria": 30,
    },
    {
        "nome_curso": "Power BI Completo",
        "descricao": "Modelagem de dados, DAX e criacao de relatorios interativos no Power BI.",
        "preco": Decimal("597.00"),
        "carga_horaria": 50,
    },
    {
        "nome_curso": "Estatística Aplicada",
        "descricao": "Probabilidade, testes de hipotese e regressao aplicados a problemas reais.",
        "preco": Decimal("697.00"),
        "carga_horaria": 80,
    },
    {
        "nome_curso": "Machine Learning Fundamentos",
        "descricao": "Algoritmos supervisionados e nao supervisionados com Scikit-Learn.",
        "preco": Decimal("997.00"),
        "carga_horaria": 100,
    },
    {
        "nome_curso": "Engenharia de Dados com Spark",
        "descricao": "Processamento distribuido de grandes volumes de dados com PySpark.",
        "preco": Decimal("1297.00"),
        "carga_horaria": 120,
    },
    {
        "nome_curso": "Análise de Dados com Pandas",
        "descricao": "Limpeza, transformacao e exploracao de dados com a biblioteca Pandas.",
        "preco": Decimal("397.00"),
        "carga_horaria": 45,
    },
    {
        "nome_curso": "Visualização de Dados",
        "descricao": "Principios de design e storytelling com Matplotlib, Seaborn e Plotly.",
        "preco": Decimal("347.00"),
        "carga_horaria": 35,
    },
    {
        "nome_curso": "Banco de Dados Relacional",
        "descricao": "Modelagem conceitual, logica e fisica com foco em PostgreSQL.",
        "preco": Decimal("497.00"),
        "carga_horaria": 55,
    },
]

# Distribuicao de status das matriculas (conforme design aprovado)
DISTRIBUICAO_STATUS_MATRICULA = (
    ["Ativa"] * 40 +
    ["Concluída"] * 20 +
    ["Trancada"] * 25 +
    ["Cancelada"] * 15
)

# Distribuicao de quantidade de cursos por matricula
DISTRIBUICAO_QTD_CURSOS = (
    [1] * 40 +
    [2] * 30 +
    [3] * 20 +
    [4] * 10
)

# Correlacao status matricula -> status pagamento (com ruido)
CORRELACAO_PAGAMENTO = {
    "Ativa":     [("Pago", 90), ("Pendente", 10)],
    "Concluída": [("Pago", 100)],
    "Trancada":  [("Pago", 70), ("Pendente", 30)],
    "Cancelada": [("Estornado", 80), ("Pendente", 20)],
}

# Formas de pagamento disponiveis
FORMAS_PAGAMENTO = ["PIX", "Cartão de Crédito", "Boleto"]

# Nomes de meses e dias da semana em portugues para dim_tempo
NOMES_MESES = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]

DIAS_SEMANA = [
    "Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira",
    "Sexta-feira", "Sábado", "Domingo"
]


# ============================================================================
# FUNCOES DE GERACAO DE DADOS
# ============================================================================

def gerar_alunos(session, n=50):
    """
    Gera N alunos com dados brasileiros realistas.

    Regras:
    - Email derivado do nome para parecer organico.
    - CPF gerado pelo provider nativo do Faker pt_BR.
    - Data de nascimento entre 1980 e 2005.
    - Data de cadastro entre 2022 e 2024.

    Args:
        session: Sessao SQLAlchemy ativa.
        n: Quantidade de alunos a gerar (default: 50).

    Returns:
        Lista de objetos Aluno adicionados a sessao.
    """
    alunos = []
    emails_usados = set()
    cpfs_usados = set()

    for _ in range(n):
        nome = fake.name()

        # Gera email unico derivado do nome
        nome_parts = nome.lower().split()
        base_email = f"{nome_parts[0]}.{nome_parts[-1]}"
        # Remove acentos simples para email
        base_email = (base_email
                      .replace("á", "a").replace("ã", "a").replace("â", "a").replace("à", "a")
                      .replace("é", "e").replace("ê", "e")
                      .replace("í", "i")
                      .replace("ó", "o").replace("õ", "o").replace("ô", "o")
                      .replace("ú", "u").replace("ü", "u")
                      .replace("ç", "c"))
        dominio = random.choice(["gmail.com", "outlook.com", "hotmail.com", "yahoo.com.br"])
        email = f"{base_email}@{dominio}"

        # Garante unicidade do email
        contador = 1
        email_original = email
        while email in emails_usados:
            email = f"{base_email}{contador}@{dominio}"
            contador += 1
        emails_usados.add(email)

        # Garante unicidade do CPF
        cpf = fake.cpf()
        while cpf in cpfs_usados:
            cpf = fake.cpf()
        cpfs_usados.add(cpf)

        aluno = Aluno(
            nome=nome,
            email=email,
            cpf=cpf,
            data_nascimento=fake.date_of_birth(minimum_age=21, maximum_age=46),
            data_cadastro=fake.date_between(
                start_date=date(2022, 1, 1),
                end_date=date(2024, 12, 31)
            ),
        )
        alunos.append(aluno)
        session.add(aluno)

    # Flush para gerar os IDs antes de retornar
    session.flush()
    print(f"  Gerando Alunos...          [OK] {len(alunos)} alunos criados.")
    return alunos


def gerar_cursos(session):
    """
    Gera os 10 cursos a partir do catalogo fixo definido em CURSOS_CATALOGO.

    Regras:
    - Nomes e precos fixos para garantir consistencia entre execucoes.
    - Data de criacao entre 2021 e 2023.

    Args:
        session: Sessao SQLAlchemy ativa.

    Returns:
        Lista de objetos Curso adicionados a sessao.
    """
    cursos = []

    for dados_curso in CURSOS_CATALOGO:
        curso = Curso(
            nome_curso=dados_curso["nome_curso"],
            descricao=dados_curso["descricao"],
            preco=dados_curso["preco"],
            carga_horaria=dados_curso["carga_horaria"],
            data_criacao=fake.date_between(
                start_date=date(2021, 1, 1),
                end_date=date(2023, 6, 30)
            ),
        )
        cursos.append(curso)
        session.add(curso)

    session.flush()
    print(f"  Gerando Cursos...          [OK] {len(cursos)} cursos criados.")
    return cursos


def _sortear_status_pagamento(status_matricula):
    """
    Sorteia o status do pagamento com base na correlacao definida
    com o status da matricula.

    Args:
        status_matricula: Status da matricula (Ativa, Concluida, Trancada, Cancelada).

    Returns:
        String com o status do pagamento sorteado.
    """
    opcoes = CORRELACAO_PAGAMENTO[status_matricula]
    populacao = [status for status, _ in opcoes]
    pesos = [peso for _, peso in opcoes]
    return random.choices(populacao, weights=pesos, k=1)[0]


def _calcular_preco_momento(preco_catalogo):
    """
    Calcula o preco no momento da venda, aplicando desconto em 20% dos casos.

    Regras:
    - 80% das vezes: preco cheio do catalogo.
    - 20% das vezes: desconto aleatorio de 5% a 20%.

    Args:
        preco_catalogo: Preco original do curso no catalogo (Decimal).

    Returns:
        Decimal com o preco aplicado, arredondado para 2 casas.
    """
    if random.random() < 0.2:
        # Aplica desconto de 5% a 20%
        desconto = Decimal(str(random.uniform(0.05, 0.20)))
        preco = preco_catalogo * (1 - desconto)
        return preco.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return preco_catalogo


def gerar_matriculas(session, alunos, cursos, n=100):
    """
    Gera N matriculas com seus respectivos itens e pagamentos.

    Para cada matricula:
    1. Sorteia um aluno e uma data entre 2023-2024.
    2. Sorteia o status conforme distribuicao definida.
    3. Gera 1 a 4 itens de matricula (cursos) conforme distribuicao.
    4. Calcula o valor_total como soma dos preco_momento dos itens.
    5. Gera 1 pagamento com status correlacionado ao status da matricula.

    Args:
        session: Sessao SQLAlchemy ativa.
        alunos: Lista de objetos Aluno ja persistidos.
        cursos: Lista de objetos Curso ja persistidos.
        n: Quantidade de matriculas a gerar (default: 100).

    Returns:
        Lista de objetos Matricula adicionados a sessao.
    """
    matriculas = []
    total_itens = 0
    total_pagamentos = 0

    for _ in range(n):
        aluno = random.choice(alunos)
        status = random.choice(DISTRIBUICAO_STATUS_MATRICULA)
        data_matricula = fake.date_between(
            start_date=date(2023, 1, 1),
            end_date=date(2024, 12, 31)
        )

        matricula = Matricula(
            id_aluno=aluno.id_aluno,
            data_matricula=data_matricula,
            status=status,
            valor_total=Decimal("0.00"),  # Sera recalculado apos gerar itens
        )
        session.add(matricula)
        session.flush()  # Gera o id_matricula para vincular os itens

        # --- Gerar Itens de Matricula ---
        qtd_cursos = random.choice(DISTRIBUICAO_QTD_CURSOS)
        # Garante que nao pedimos mais cursos do que existem
        qtd_cursos = min(qtd_cursos, len(cursos))
        cursos_selecionados = random.sample(cursos, qtd_cursos)

        valor_total_matricula = Decimal("0.00")

        for curso in cursos_selecionados:
            preco_momento = _calcular_preco_momento(curso.preco)
            valor_total_matricula += preco_momento

            item = ItemMatricula(
                id_matricula=matricula.id_matricula,
                id_curso=curso.id_curso,
                preco_momento=preco_momento,
                data_inicio_prevista=data_matricula + timedelta(days=random.randint(7, 30)),
            )
            session.add(item)
            total_itens += 1

        # Atualiza o valor_total da matricula com a soma real dos itens
        matricula.valor_total = valor_total_matricula

        # --- Gerar Pagamento (1 por matricula) ---
        status_pagamento = _sortear_status_pagamento(status)
        eh_pago = status_pagamento in ("Pago", "Estornado")

        pagamento = Pagamento(
            id_matricula=matricula.id_matricula,
            forma_pagamento=random.choice(FORMAS_PAGAMENTO),
            valor_pago=valor_total_matricula if eh_pago else None,
            data_pagamento=(
                data_matricula + timedelta(days=random.randint(0, 5))
                if eh_pago else None
            ),
            status_pagamento=status_pagamento,
        )
        session.add(pagamento)
        total_pagamentos += 1

        matriculas.append(matricula)

    session.flush()
    print(f"  Gerando Matriculas...      [OK] {len(matriculas)} matriculas criadas.")
    print(f"                             [OK] {total_itens} itens de matricula criados.")
    print(f"                             [OK] {total_pagamentos} pagamentos criados.")
    return matriculas


def gerar_dim_tempo(session, ano_inicio=2020, ano_fim=2025):
    """
    Gera a dimensao de tempo com uma linha para cada dia do periodo.

    Esta dimensao eh gerada artificialmente (sem dependencia do OLTP) para
    evitar calculos de data em tempo de execucao nas queries analiticas.

    Args:
        session: Sessao SQLAlchemy ativa.
        ano_inicio: Ano inicial do calendario (default: 2020).
        ano_fim: Ano final do calendario, inclusivo (default: 2025).

    Returns:
        None
    """
    data_atual = date(ano_inicio, 1, 1)
    data_fim = date(ano_fim, 12, 31)
    contador = 0

    while data_atual <= data_fim:
        dim = DimTempo(
            data_completa=data_atual,
            ano=data_atual.year,
            mes=data_atual.month,
            dia=data_atual.day,
            trimestre=(data_atual.month - 1) // 3 + 1,
            nome_mes=NOMES_MESES[data_atual.month - 1],
            dia_semana=DIAS_SEMANA[data_atual.weekday()],
        )
        session.add(dim)
        data_atual += timedelta(days=1)
        contador += 1

    session.flush()
    print(f"  Gerando dim_tempo...       [OK] {contador} registros de tempo criados.")


# ============================================================================
# LIMPEZA DE DADOS (TRUNCATE SEGURO)
# ============================================================================

def limpar_dados(session):
    """
    Remove todos os dados existentes respeitando a ordem de dependencia
    das Foreign Keys para evitar erros de constraint.

    Ordem de exclusao (reversa das FKs):
    1. oltp.pagamento
    2. oltp.item_matricula
    3. oltp.matricula
    4. oltp.curso
    5. oltp.aluno
    6. dw.dim_tempo
    """
    print("\n  Limpando dados existentes...")
    session.query(Pagamento).delete()
    session.query(ItemMatricula).delete()
    session.query(Matricula).delete()
    session.query(Curso).delete()
    session.query(Aluno).delete()
    session.query(DimTempo).delete()
    session.flush()
    print("  [OK] Dados anteriores removidos com sucesso.\n")


# ============================================================================
# FUNCAO PRINCIPAL (ORQUESTRADOR)
# ============================================================================

def main():
    """
    Funcao principal que orquestra toda a geracao de dados.

    Fluxo:
    1. Abre sessao com o banco de dados.
    2. Limpa dados existentes (idempotencia).
    3. Gera dados OLTP (Alunos -> Cursos -> Matriculas + Itens + Pagamentos).
    4. Persiste dados OLTP.
    5. Gera dim_tempo no DW.
    6. Persiste dim_tempo.
    7. Exibe resumo final.

    Em caso de erro, executa rollback completo da sessao.
    """
    print("\n--- [SEED] Iniciando a geracao de dados sinteticos ---\n")

    session = SessionLocal()

    try:
        # Passo 1: Limpeza (garante idempotencia)
        limpar_dados(session)

        # Passo 2: Geracao dos dados OLTP
        alunos = gerar_alunos(session, n=50)
        cursos = gerar_cursos(session)
        matriculas = gerar_matriculas(session, alunos, cursos, n=100)

        # Passo 3: Commit do OLTP
        session.commit()
        print("\n  [OK] Dados OLTP persistidos com sucesso.\n")

        # Passo 4: Geracao da dim_tempo no DW
        gerar_dim_tempo(session, ano_inicio=2020, ano_fim=2025)

        # Passo 5: Commit do DW
        session.commit()
        print("\n  [OK] dim_tempo persistida com sucesso.")

        # Passo 6: Resumo final
        total_alunos = session.query(Aluno).count()
        total_cursos = session.query(Curso).count()
        total_matriculas = session.query(Matricula).count()
        total_itens = session.query(ItemMatricula).count()
        total_pagamentos = session.query(Pagamento).count()
        total_dim_tempo = session.query(DimTempo).count()

        print("\n--- [SEED] Resumo Final ---")
        print(f"  oltp.aluno:           {total_alunos}")
        print(f"  oltp.curso:           {total_cursos}")
        print(f"  oltp.matricula:       {total_matriculas}")
        print(f"  oltp.item_matricula:  {total_itens}")
        print(f"  oltp.pagamento:       {total_pagamentos}")
        print(f"  dw.dim_tempo:         {total_dim_tempo}")
        print("\n--- [SEED] Seed concluido com sucesso! ---\n")

    except Exception as e:
        session.rollback()
        print(f"\n  [ERRO] Falha durante o seed: {e}")
        print("  [ERRO] Rollback executado. Nenhum dado foi persistido.")
        raise

    finally:
        session.close()


if __name__ == "__main__":
    main()
