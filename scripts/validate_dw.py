"""
Script de Validacao Analitica do Data Warehouse — Issue #10

Executa um conjunto de queries de sanidade contra as tabelas do schema 'dw'
para garantir a corretude e integridade dos dados inseridos pelo pipeline
ETL (Issue #9).

CATEGORIAS DE VALIDACAO:
    1. Contagem e Completude — Verifica se todas as tabelas foram populadas.
    2. Integridade Referencial — Garante que nao existem SKs orfas na fato.
    3. Consistencia de Metricas — Valida calculos de valor_total e qtd_cursos.
    4. Analise de Distribuicao — Exibe distribuicoes para validacao visual.
    5. Queries Uteis — Exemplos prontos de receita por mes, ticket medio, etc.

EXECUCAO:
    poetry run python scripts/validate_dw.py

PRE-REQUISITOS:
    1. O pipeline ETL (Issue #9) deve ter sido executado com sucesso.
    2. O banco de dados deve estar acessivel via DATABASE_URL no .env.
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import text
from config.database import engine


# ============================================================================
# HELPER: EXECUCAO E FORMATACAO DE QUERIES
# ============================================================================

def executar_query(conexao, titulo, sql, mostrar_linhas=True):
    """
    Executa uma query SQL, exibe o titulo e os resultados formatados.

    Args:
        conexao: Conexao SQLAlchemy ativa.
        titulo: Titulo descritivo da validacao.
        sql: Query SQL a executar.
        mostrar_linhas: Se True, exibe todas as linhas. Se False, apenas o titulo.

    Returns:
        Lista de tuplas (rows) retornadas pela query.
    """
    print(f"\n{'-' * 60}")
    print(f"  {titulo}")
    print(f"{'-' * 60}")

    resultado = conexao.execute(text(sql))
    colunas = resultado.keys()
    linhas = resultado.fetchall()

    if not linhas:
        print("  (nenhum resultado)")
        return linhas

    if mostrar_linhas:
        # Calcula largura de cada coluna para alinhamento
        larguras = []
        for i, col in enumerate(colunas):
            max_val = max(len(str(row[i])) for row in linhas)
            larguras.append(max(len(str(col)), max_val))

        # Header
        header = "  " + " | ".join(str(col).ljust(larguras[i]) for i, col in enumerate(colunas))
        separador = "  " + "-+-".join("-" * l for l in larguras)
        print(header)
        print(separador)

        # Rows
        for row in linhas:
            linha_formatada = "  " + " | ".join(str(val).ljust(larguras[i]) for i, val in enumerate(row))
            print(linha_formatada)

    return linhas


def validacao_passou(titulo, condicao):
    """Exibe resultado de uma validacao booleana (PASS/FAIL)."""
    status = "[PASS]" if condicao else "[FAIL]"
    print(f"  {status} -- {titulo}")
    return condicao


# ============================================================================
# 1. CONTAGEM E COMPLETUDE
# ============================================================================

def validar_contagens(conn):
    """
    Verifica se todas as tabelas do DW possuem registros.
    Uma tabela vazia indica falha no ETL ou no seed.
    """
    print("\n" + "=" * 60)
    print("  VALIDACAO 1: CONTAGEM E COMPLETUDE")
    print("=" * 60)

    linhas = executar_query(conn, "Contagem de registros por tabela", """
        SELECT 'dim_aluno' AS tabela, COUNT(*) AS registros FROM dw.dim_aluno
        UNION ALL
        SELECT 'dim_curso', COUNT(*) FROM dw.dim_curso
        UNION ALL
        SELECT 'dim_status', COUNT(*) FROM dw.dim_status
        UNION ALL
        SELECT 'dim_tempo', COUNT(*) FROM dw.dim_tempo
        UNION ALL
        SELECT 'fato_matricula', COUNT(*) FROM dw.fato_matricula
        ORDER BY tabela
    """)

    todas_populadas = all(int(row[1]) > 0 for row in linhas)
    validacao_passou("Todas as tabelas do DW possuem registros", todas_populadas)
    return todas_populadas


# ============================================================================
# 2. INTEGRIDADE REFERENCIAL
# ============================================================================

def validar_integridade_referencial(conn):
    """
    Garante que nao existem Surrogate Keys na fato que nao tenham
    correspondencia nas respectivas tabelas dimensionais.
    SKs orfas indicariam falha no lookup do ETL.
    """
    print("\n" + "=" * 60)
    print("  VALIDACAO 2: INTEGRIDADE REFERENCIAL")
    print("=" * 60)

    tudo_ok = True

    # Verifica cada FK da fato contra sua dimensao
    checks = [
        ("sk_aluno",  "dw.dim_aluno",  "sk_aluno"),
        ("sk_curso",  "dw.dim_curso",  "sk_curso"),
        ("sk_tempo",  "dw.dim_tempo",  "sk_tempo"),
        ("sk_status", "dw.dim_status", "sk_status"),
    ]

    for fk_col, dim_table, dim_pk in checks:
        sql = f"""
            SELECT COUNT(*) AS orfas
            FROM dw.fato_matricula f
            LEFT JOIN {dim_table} d ON f.{fk_col} = d.{dim_pk}
            WHERE d.{dim_pk} IS NULL
        """
        resultado = conn.execute(text(sql))
        orfas = resultado.scalar()
        ok = orfas == 0
        validacao_passou(f"fato.{fk_col} -> {dim_table} (orfas: {orfas})", ok)
        if not ok:
            tudo_ok = False

    return tudo_ok


# ============================================================================
# 3. CONSISTENCIA DE METRICAS
# ============================================================================

def validar_metricas(conn):
    """
    Valida que as metricas calculadas pelo Pydantic durante o ETL sao
    consistentes com os dados de origem:
    - valor_total deve ser > 0 em todos os registros.
    - qtd_cursos deve ser >= 1.
    - valor_medio_curso deve ser valor_total / qtd_cursos.
    """
    print("\n" + "=" * 60)
    print("  VALIDACAO 3: CONSISTENCIA DE METRICAS")
    print("=" * 60)

    tudo_ok = True

    # 3a. Nenhum valor_total zerado ou negativo
    resultado = conn.execute(text("""
        SELECT COUNT(*) FROM dw.fato_matricula
        WHERE valor_total <= 0
    """))
    negativos = resultado.scalar()
    ok = negativos == 0
    validacao_passou(f"Nenhum valor_total <= 0 (encontrados: {negativos})", ok)
    if not ok:
        tudo_ok = False

    # 3b. qtd_cursos >= 1
    resultado = conn.execute(text("""
        SELECT COUNT(*) FROM dw.fato_matricula
        WHERE qtd_cursos < 1
    """))
    invalidos = resultado.scalar()
    ok = invalidos == 0
    validacao_passou(f"Nenhum qtd_cursos < 1 (encontrados: {invalidos})", ok)
    if not ok:
        tudo_ok = False

    # 3c. valor_medio_curso consistente com valor_total / qtd_cursos
    # Tolerancia de R$ 0.02 por arredondamento decimal
    resultado = conn.execute(text("""
        SELECT COUNT(*) FROM dw.fato_matricula
        WHERE ABS(valor_medio_curso - (valor_total / qtd_cursos)) > 0.02
    """))
    inconsistentes = resultado.scalar()
    ok = inconsistentes == 0
    validacao_passou(f"valor_medio_curso = valor_total / qtd_cursos (desvios: {inconsistentes})", ok)
    if not ok:
        tudo_ok = False

    # 3d. Estatisticas gerais das metricas
    executar_query(conn, "Estatisticas descritivas das metricas", """
        SELECT
            COUNT(*)                            AS total_fatos,
            ROUND(MIN(valor_total), 2)          AS min_valor_total,
            ROUND(AVG(valor_total), 2)          AS avg_valor_total,
            ROUND(MAX(valor_total), 2)          AS max_valor_total,
            MIN(qtd_cursos)                     AS min_qtd_cursos,
            ROUND(AVG(qtd_cursos), 1)           AS avg_qtd_cursos,
            MAX(qtd_cursos)                     AS max_qtd_cursos,
            ROUND(MIN(valor_medio_curso), 2)    AS min_ticket,
            ROUND(AVG(valor_medio_curso), 2)    AS avg_ticket,
            ROUND(MAX(valor_medio_curso), 2)    AS max_ticket
        FROM dw.fato_matricula
    """)

    return tudo_ok


# ============================================================================
# 4. ANALISE DE DISTRIBUICAO
# ============================================================================

def validar_distribuicoes(conn):
    """
    Exibe distribuicoes para validacao visual pelo analista.
    Estas queries nao fazem validacao automatica — servem como
    inspecao humana para detectar anomalias nos dados.
    """
    print("\n" + "=" * 60)
    print("  VALIDACAO 4: ANALISE DE DISTRIBUICAO")
    print("=" * 60)

    # 4a. Distribuicao por status
    executar_query(conn, "Distribuicao de matriculas por status", """
        SELECT
            s.codigo_status,
            COUNT(*)            AS quantidade,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) AS percentual
        FROM dw.fato_matricula f
        JOIN dw.dim_status s ON f.sk_status = s.sk_status
        GROUP BY s.codigo_status
        ORDER BY quantidade DESC
    """)

    # 4b. Distribuicao por curso
    executar_query(conn, "Distribuicao de matriculas por curso", """
        SELECT
            c.nome_curso,
            COUNT(*)                    AS matriculas,
            ROUND(SUM(f.valor_total), 2) AS receita_bruta
        FROM dw.fato_matricula f
        JOIN dw.dim_curso c ON f.sk_curso = c.sk_curso
        GROUP BY c.nome_curso
        ORDER BY matriculas DESC
    """)

    # 4c. Distribuicao temporal (por ano-mes)
    executar_query(conn, "Distribuicao temporal (matriculas por mes)", """
        SELECT
            t.ano,
            t.nome_mes,
            t.mes,
            COUNT(*) AS matriculas
        FROM dw.fato_matricula f
        JOIN dw.dim_tempo t ON f.sk_tempo = t.sk_tempo
        GROUP BY t.ano, t.nome_mes, t.mes
        ORDER BY t.ano, t.mes
    """)


# ============================================================================
# 5. QUERIES UTEIS (DOCUMENTACAO ANALITICA)
# ============================================================================

def queries_uteis(conn):
    """
    Conjunto de queries analiticas de exemplo, prontas para uso em
    relatorios e dashboards de BI. Estas sao as queries que serao
    a base das Views da Camada Semantica (Issue #11).
    """
    print("\n" + "=" * 60)
    print("  QUERIES UTEIS (Exemplos Analiticos)")
    print("=" * 60)

    # 5a. Receita mensal
    executar_query(conn, "Receita mensal (agrupada por ano/mes)", """
        SELECT
            t.ano,
            t.nome_mes,
            COUNT(DISTINCT f.nk_matricula)  AS total_matriculas,
            ROUND(SUM(f.valor_total), 2)    AS receita_total,
            ROUND(AVG(f.valor_total), 2)    AS ticket_medio
        FROM dw.fato_matricula f
        JOIN dw.dim_tempo t ON f.sk_tempo = t.sk_tempo
        GROUP BY t.ano, t.nome_mes, t.mes
        ORDER BY t.ano, t.mes
    """)

    # 5b. Top 5 cursos por receita
    executar_query(conn, "Top 5 cursos por receita total", """
        SELECT
            c.nome_curso,
            COUNT(*)                        AS total_inscricoes,
            ROUND(SUM(f.valor_total), 2)    AS receita_total,
            ROUND(AVG(f.valor_medio_curso), 2) AS ticket_medio
        FROM dw.fato_matricula f
        JOIN dw.dim_curso c ON f.sk_curso = c.sk_curso
        GROUP BY c.nome_curso
        ORDER BY receita_total DESC
        LIMIT 5
    """)

    # 5c. Taxa de evasao (Trancada + Cancelada)
    executar_query(conn, "Funil de evasao por status", """
        SELECT
            s.codigo_status,
            s.descricao_status,
            COUNT(DISTINCT f.nk_matricula) AS matriculas,
            ROUND(
                COUNT(DISTINCT f.nk_matricula) * 100.0 /
                (SELECT COUNT(DISTINCT nk_matricula) FROM dw.fato_matricula),
            1) AS percentual
        FROM dw.fato_matricula f
        JOIN dw.dim_status s ON f.sk_status = s.sk_status
        GROUP BY s.codigo_status, s.descricao_status
        ORDER BY matriculas DESC
    """)


# ============================================================================
# FUNCAO PRINCIPAL (ORQUESTRADOR)
# ============================================================================

def main():
    """
    Executa todas as validacoes e exibe o resultado consolidado.
    Retorna exit code 0 se todas as validacoes passaram, 1 caso contrario.
    """
    print("\n" + "=" * 60)
    print("  [VALIDACAO] Iniciando Validacao Analitica do DW")
    print("=" * 60)

    with engine.connect() as conn:
        resultados = []

        # Validacoes automaticas (PASS/FAIL)
        resultados.append(("Contagem e Completude", validar_contagens(conn)))
        resultados.append(("Integridade Referencial", validar_integridade_referencial(conn)))
        resultados.append(("Consistencia de Metricas", validar_metricas(conn)))

        # Validacoes visuais (sem PASS/FAIL)
        validar_distribuicoes(conn)

        # Queries de exemplo
        queries_uteis(conn)

    # Resumo final
    print("\n" + "=" * 60)
    print("  [VALIDACAO] Resumo Final")
    print("=" * 60)

    todas_passaram = True
    for nome, passou in resultados:
        status = "[PASS]" if passou else "[FAIL]"
        print(f"  {status} -- {nome}")
        if not passou:
            todas_passaram = False

    if todas_passaram:
        print("\n  Todas as validacoes passaram com sucesso!")
    else:
        print("\n  ATENCAO: Algumas validacoes falharam. Revise os resultados acima.")

    print("=" * 60 + "\n")

    return 0 if todas_passaram else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
