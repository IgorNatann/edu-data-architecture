"""
Pipeline ETL (Extract → Transform → Load) — Issue #9

Movimenta os dados do schema 'oltp' para o schema 'dw', populando as
dimensoes restantes (dim_aluno, dim_curso, dim_status) e a tabela fato
(fato_matricula).

GRANULARIDADE DA FATO:
    Uma linha por item de matricula (par matricula-curso). Isso permite
    analises diretas por curso na tabela fato, seguindo a modelagem
    dimensional de Kimball. As metricas agregadas (valor_total, qtd_cursos,
    valor_medio_curso) sao replicadas em cada linha da mesma matricula,
    funcionando como "metricas de contexto" do cabecalho.

PRE-REQUISITOS:
    1. O script de seed (Issue #8) deve ter sido executado previamente.
    2. A dim_tempo ja deve estar populada no schema 'dw'.

IDEMPOTENCIA:
    O pipeline limpa as tabelas do DW (exceto dim_tempo) antes de inserir,
    podendo ser executado multiplas vezes com seguranca.

EXECUCAO:
    poetry run python etl/load_fato_matricula.py
"""

import sys
import os

# Ajuste de path para importar modulos do projeto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import joinedload

from config.database import SessionLocal
from models.oltp import Aluno, Curso, Matricula, ItemMatricula
from models.dw import DimAluno, DimCurso, DimStatus, DimTempo, FatoMatricula
from schemas.fato_matricula_schema import FatoMatriculaTransform, FatoMatriculaSchema


# ============================================================================
# DESCRICOES AMIGAVEIS DOS STATUS (para a dim_status)
# ============================================================================

DESCRICOES_STATUS = {
    "Ativa":     "Matricula ativa com acesso regular aos cursos",
    "Concluída": "Matricula concluida com todos os cursos finalizados",
    "Trancada":  "Matricula temporariamente suspensa pelo aluno",
    "Cancelada": "Matricula cancelada e encerrada definitivamente",
}


# ============================================================================
# FASE 1: EXTRACT (Extracao dos dados do OLTP)
# ============================================================================

def extract(session):
    """
    Extrai todas as matriculas do schema OLTP com seus relacionamentos
    carregados em memoria (eager loading) para evitar queries N+1.

    O 'joinedload' instrui o SQLAlchemy a fazer JOINs na mesma query,
    trazendo Aluno, Itens e Cursos de cada matricula de uma so vez.

    Relacionamentos carregados:
    - Matricula → Aluno (dados cadastrais)
    - Matricula → Itens → Curso (detalhes de cada curso da matricula)

    Args:
        session: Sessao SQLAlchemy ativa.

    Returns:
        Lista de objetos Matricula com relationships carregados.
    """
    print("\n  [EXTRACT] Lendo dados do schema OLTP...")

    matriculas = (
        session.query(Matricula)
        .options(
            joinedload(Matricula.aluno),
            joinedload(Matricula.itens).joinedload(ItemMatricula.curso),
        )
        .all()
    )

    # Coleta estatisticas para log
    alunos_distintos = len({m.id_aluno for m in matriculas})
    cursos_distintos = len({
        item.id_curso
        for m in matriculas
        for item in m.itens
    })
    total_itens = sum(len(m.itens) for m in matriculas)

    print(f"             Matriculas extraidas:   {len(matriculas)}")
    print(f"             Alunos distintos:        {alunos_distintos}")
    print(f"             Cursos distintos:        {cursos_distintos}")
    print(f"             Total de itens:          {total_itens}")

    return matriculas


# ============================================================================
# FASE 2: LOAD DIMENSOES (Carga das tabelas dimensionais)
# ============================================================================

def load_dim_aluno(session, matriculas):
    """
    Popula a dimensao dim_aluno a partir dos alunos distintos encontrados
    nas matriculas extraidas.

    Para cada aluno, cria um registro na dim_aluno contendo:
    - nk_aluno: ID original do OLTP (Natural Key) para rastreabilidade.
    - nome, email, data_nascimento: Atributos descritivos para analises.

    Args:
        session: Sessao SQLAlchemy ativa.
        matriculas: Lista de Matricula com relationship 'aluno' carregado.

    Returns:
        dict: Mapeamento {nk_aluno (int) → sk_aluno (int)} para resolver FKs na fato.
    """
    print("\n  [LOAD] Carregando dim_aluno...")

    # Coleta alunos distintos (evita duplicatas caso um aluno tenha N matriculas)
    alunos_vistos = {}
    for matricula in matriculas:
        aluno = matricula.aluno
        if aluno.id_aluno not in alunos_vistos:
            alunos_vistos[aluno.id_aluno] = aluno

    # Insere cada aluno unico na dimensao
    for aluno in alunos_vistos.values():
        dim = DimAluno(
            nk_aluno=aluno.id_aluno,
            nome=aluno.nome,
            email=aluno.email,
            data_nascimento=aluno.data_nascimento,
        )
        session.add(dim)

    # Flush gera as Surrogate Keys (sk_aluno) via autoincrement
    session.flush()

    # Constroi o mapa de lookup NK → SK para uso posterior na fato
    lookup = {}
    for dim in session.query(DimAluno).all():
        lookup[dim.nk_aluno] = dim.sk_aluno

    print(f"           {len(lookup)} alunos carregados na dimensao.")
    return lookup


def load_dim_curso(session, matriculas):
    """
    Popula a dimensao dim_curso a partir dos cursos distintos encontrados
    nos itens de matricula extraidos.

    Para cada curso, cria um registro contendo:
    - nk_curso: ID original do OLTP (Natural Key).
    - nome_curso, carga_horaria: Atributos descritivos.
    - preco_catalogo: Preco atual do curso no catalogo (snapshot).

    Args:
        session: Sessao SQLAlchemy ativa.
        matriculas: Lista de Matricula com relationships carregados.

    Returns:
        dict: Mapeamento {nk_curso (int) → sk_curso (int)}.
    """
    print("\n  [LOAD] Carregando dim_curso...")

    # Coleta cursos distintos de todos os itens de todas as matriculas
    cursos_vistos = {}
    for matricula in matriculas:
        for item in matricula.itens:
            curso = item.curso
            if curso.id_curso not in cursos_vistos:
                cursos_vistos[curso.id_curso] = curso

    # Insere cada curso unico na dimensao
    for curso in cursos_vistos.values():
        dim = DimCurso(
            nk_curso=curso.id_curso,
            nome_curso=curso.nome_curso,
            carga_horaria=curso.carga_horaria,
            preco_catalogo=curso.preco,
        )
        session.add(dim)

    session.flush()

    # Constroi o mapa de lookup NK → SK
    lookup = {}
    for dim in session.query(DimCurso).all():
        lookup[dim.nk_curso] = dim.sk_curso

    print(f"           {len(lookup)} cursos carregados na dimensao.")
    return lookup


def load_dim_status(session, matriculas):
    """
    Popula a dimensao dim_status com os status distintos encontrados
    nas matriculas extraidas.

    Cada status recebe uma descricao amigavel (definida em DESCRICOES_STATUS)
    para uso em relatorios e dashboards de BI.

    Args:
        session: Sessao SQLAlchemy ativa.
        matriculas: Lista de Matricula extraidas.

    Returns:
        dict: Mapeamento {codigo_status (str) → sk_status (int)}.
    """
    print("\n  [LOAD] Carregando dim_status...")

    # Coleta status distintos de todas as matriculas
    status_distintos = {m.status for m in matriculas}

    # Insere na dimensao com descricoes amigaveis (ordenado para consistencia)
    for codigo in sorted(status_distintos):
        descricao = DESCRICOES_STATUS.get(codigo, f"Status: {codigo}")
        dim = DimStatus(
            codigo_status=codigo,
            descricao_status=descricao,
        )
        session.add(dim)

    session.flush()

    # Constroi o mapa de lookup codigo → SK
    lookup = {}
    for dim in session.query(DimStatus).all():
        lookup[dim.codigo_status] = dim.sk_status

    print(f"           {len(lookup)} status carregados na dimensao.")
    return lookup


def build_tempo_lookup(session):
    """
    Constroi o mapa de lookup para a dim_tempo (ja populada pelo seed).

    A dim_tempo eh a unica dimensao que NAO eh carregada pelo ETL —
    ela foi gerada artificialmente no seed_data.py (Issue #8) com datas
    de 2020 a 2025.

    Args:
        session: Sessao SQLAlchemy ativa.

    Returns:
        dict: Mapeamento {data_completa (date) → sk_tempo (int)}.
    """
    print("\n  [LOOKUP] Construindo mapa da dim_tempo...")

    lookup = {}
    for dim in session.query(DimTempo).all():
        lookup[dim.data_completa] = dim.sk_tempo

    print(f"            {len(lookup)} datas disponiveis no calendario.")
    return lookup


# ============================================================================
# FASE 3: TRANSFORM + LOAD FATO (Transformacao Pydantic e Carga)
# ============================================================================

def transform_and_load(session, matriculas, sk_aluno, sk_curso, sk_tempo, sk_status):
    """
    Transforma os dados brutos do OLTP e carrega a tabela fato.

    Para cada ITEM de cada MATRICULA:
    1. Instancia o FatoMatriculaTransform (Pydantic) que calcula as metricas
       agregadas (valor_total, qtd_cursos, valor_medio_curso) a partir de
       todos os precos dos itens da matricula.
    2. Resolve as Surrogate Keys (SKs) via lookup dicts.
    3. Valida o registro final com FatoMatriculaSchema.
    4. Insere na fato_matricula.

    GRANULARIDADE: Uma linha por item de matricula (par matricula-curso).
    As metricas agregadas sao replicadas em cada linha da mesma matricula,
    seguindo o padrao de "metricas replicadas" do Kimball para preservar
    o contexto completo da transacao em cada registro.

    Args:
        session: Sessao SQLAlchemy ativa.
        matriculas: Lista de Matricula com relationships carregados.
        sk_aluno: dict {nk_aluno → sk_aluno}
        sk_curso: dict {nk_curso → sk_curso}
        sk_tempo: dict {data_completa → sk_tempo}
        sk_status: dict {codigo_status → sk_status}

    Returns:
        int: Total de registros inseridos na fato.
    """
    print("\n  [TRANSFORM + LOAD] Processando fato_matricula...")

    total_inseridos = 0
    erros = 0

    for matricula in matriculas:
        # Coleta todos os precos dos itens desta matricula (para metricas agregadas)
        precos_itens = [item.preco_momento for item in matricula.itens]

        # Resolve a SK de tempo para a data da matricula
        sk_tempo_val = sk_tempo.get(matricula.data_matricula)
        if sk_tempo_val is None:
            print(f"  [AVISO] Data {matricula.data_matricula} nao encontrada na dim_tempo. "
                  f"Matricula {matricula.id_matricula} ignorada.")
            erros += 1
            continue

        # Para cada item da matricula, gera uma linha na fato
        for item in matricula.itens:
            try:
                # --- TRANSFORM (Pydantic) ---
                # O schema recebe a lista completa de precos para calcular metricas agregadas
                transformado = FatoMatriculaTransform(
                    nk_matricula=matricula.id_matricula,
                    nk_aluno=matricula.id_aluno,
                    nk_curso=item.id_curso,
                    data_matricula=matricula.data_matricula,
                    status_matricula=matricula.status,
                    precos_itens=precos_itens,
                )

                # --- RESOLVE SKs ---
                # Converte Natural Keys (IDs do OLTP) em Surrogate Keys (IDs do DW)
                fato_validada = FatoMatriculaSchema(
                    nk_matricula=transformado.nk_matricula,
                    sk_aluno=sk_aluno[transformado.nk_aluno],
                    sk_curso=sk_curso[transformado.nk_curso],
                    sk_tempo=sk_tempo_val,
                    sk_status=sk_status[matricula.status],
                    valor_total=transformado.valor_total,
                    qtd_cursos=transformado.qtd_cursos,
                    valor_medio_curso=transformado.valor_medio_curso,
                )

                # --- LOAD (SQLAlchemy) ---
                fato = FatoMatricula(
                    nk_matricula=fato_validada.nk_matricula,
                    sk_aluno=fato_validada.sk_aluno,
                    sk_curso=fato_validada.sk_curso,
                    sk_tempo=fato_validada.sk_tempo,
                    sk_status=fato_validada.sk_status,
                    valor_total=fato_validada.valor_total,
                    qtd_cursos=fato_validada.qtd_cursos,
                    valor_medio_curso=fato_validada.valor_medio_curso,
                )
                session.add(fato)
                total_inseridos += 1

            except Exception as e:
                print(f"  [ERRO] Falha ao processar item {item.id_item_matricula} "
                      f"da matricula {matricula.id_matricula}: {e}")
                erros += 1

    session.flush()
    print(f"           {total_inseridos} registros inseridos na fato_matricula.")
    if erros > 0:
        print(f"           {erros} registros com erro (ignorados).")

    return total_inseridos


# ============================================================================
# LIMPEZA DE DADOS DO DW (TRUNCATE SEGURO)
# ============================================================================

def limpar_dw(session):
    """
    Remove todos os dados do DW (exceto dim_tempo) respeitando a ordem
    de dependencia das Foreign Keys para evitar erros de constraint.

    A dim_tempo NAO eh limpa pois foi gerada pelo seed (Issue #8) e eh
    independente do pipeline ETL.

    Ordem de exclusao (dependentes primeiro):
    1. dw.fato_matricula (depende de todas as dimensoes)
    2. dw.dim_aluno
    3. dw.dim_curso
    4. dw.dim_status
    """
    print("\n  Limpando dados do DW (exceto dim_tempo)...")
    session.query(FatoMatricula).delete()
    session.query(DimAluno).delete()
    session.query(DimCurso).delete()
    session.query(DimStatus).delete()
    session.flush()
    print("  [OK] Dados anteriores do DW removidos com sucesso.\n")


# ============================================================================
# FUNCAO PRINCIPAL (ORQUESTRADOR)
# ============================================================================

def main():
    """
    Funcao principal que orquestra o pipeline ETL completo.

    Fluxo:
    1. Abre sessao com o banco de dados.
    2. Limpa tabelas do DW (exceto dim_tempo) para garantir idempotencia.
    3. EXTRACT: Le matriculas + relacionamentos do OLTP.
    4. LOAD: Popula dimensoes (dim_aluno, dim_curso, dim_status).
    5. LOOKUP: Constroi mapa da dim_tempo (ja populada pelo seed).
    6. TRANSFORM + LOAD: Processa e insere na fato_matricula.
    7. Commit e exibicao do resumo final.

    Em caso de erro, executa rollback completo da sessao.
    """
    print("\n" + "=" * 60)
    print("  [ETL] Iniciando Pipeline ETL (OLTP → DW)")
    print("=" * 60)

    session = SessionLocal()

    try:
        # Passo 1: Limpeza (garante idempotencia)
        limpar_dw(session)

        # Passo 2: EXTRACT — Le dados do OLTP
        matriculas = extract(session)

        if not matriculas:
            print("\n  [AVISO] Nenhuma matricula encontrada no OLTP.")
            print("  Execute o seed primeiro: poetry run python scripts/seed_data.py")
            return

        # Passo 3: LOAD — Popula as dimensoes do DW
        sk_aluno = load_dim_aluno(session, matriculas)
        sk_curso = load_dim_curso(session, matriculas)
        sk_status = load_dim_status(session, matriculas)

        # Passo 4: LOOKUP — Constroi mapa da dim_tempo (pre-existente)
        sk_tempo = build_tempo_lookup(session)

        # Passo 5: TRANSFORM + LOAD — Processa e insere a fato
        total_fatos = transform_and_load(
            session, matriculas, sk_aluno, sk_curso, sk_tempo, sk_status
        )

        # Passo 6: Commit — Persiste tudo no banco de dados
        session.commit()
        print("\n  [OK] Pipeline ETL concluido e dados persistidos com sucesso.")

        # Passo 7: Resumo final com contagens reais do banco
        total_dim_aluno = session.query(DimAluno).count()
        total_dim_curso = session.query(DimCurso).count()
        total_dim_status = session.query(DimStatus).count()
        total_dim_tempo = session.query(DimTempo).count()
        total_fato = session.query(FatoMatricula).count()

        print("\n" + "=" * 60)
        print("  [ETL] Resumo Final do Data Warehouse")
        print("=" * 60)
        print(f"  dw.dim_aluno:        {total_dim_aluno}")
        print(f"  dw.dim_curso:        {total_dim_curso}")
        print(f"  dw.dim_status:       {total_dim_status}")
        print(f"  dw.dim_tempo:        {total_dim_tempo} (pre-existente)")
        print(f"  dw.fato_matricula:   {total_fato}")
        print("=" * 60)
        print("  [ETL] Pipeline finalizado com sucesso!")
        print("=" * 60 + "\n")

    except Exception as e:
        session.rollback()
        print(f"\n  [ERRO] Falha durante o ETL: {e}")
        print("  [ERRO] Rollback executado. Nenhum dado foi persistido no DW.")
        raise

    finally:
        session.close()


if __name__ == "__main__":
    main()
