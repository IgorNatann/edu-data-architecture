"""
Script de Criacao das Views Analiticas (Camada Semantica) — Issue #11

Le os arquivos SQL da pasta 'docs/kpis/' e executa cada um contra o banco,
criando as Views no schema 'dw'. As views encapsulam a complexidade do
Star Schema e entregam metricas prontas para consumo de BI.

VIEWS CRIADAS:
    - dw.vw_receita_mensal     (Receita e Ticket Medio por mes)
    - dw.vw_desempenho_cursos  (Ranking e eficiencia dos cursos)
    - dw.vw_funil_evasao       (Taxa de evasao e receita em risco)

EXECUCAO:
    poetry run python scripts/create_views.py

IDEMPOTENCIA:
    Usa 'CREATE OR REPLACE VIEW', portanto pode ser executado multiplas
    vezes com seguranca.
"""

import sys
import os
import glob

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import text
from config.database import engine


def main():
    print("\n" + "=" * 60)
    print("  [VIEWS] Criando Views Analiticas (Camada Semantica)")
    print("=" * 60)

    # Localiza todos os .sql na pasta docs/kpis/
    pasta_kpis = os.path.join(os.path.dirname(__file__), '..', 'docs', 'kpis')
    pasta_kpis = os.path.abspath(pasta_kpis)
    arquivos_sql = sorted(glob.glob(os.path.join(pasta_kpis, '*.sql')))

    if not arquivos_sql:
        print(f"\n  [ERRO] Nenhum arquivo .sql encontrado em: {pasta_kpis}")
        return 1

    print(f"\n  Arquivos encontrados: {len(arquivos_sql)}")

    with engine.connect() as conn:
        for arquivo in arquivos_sql:
            nome = os.path.basename(arquivo)
            print(f"\n  Executando: {nome}...")

            try:
                with open(arquivo, 'r', encoding='utf-8') as f:
                    sql = f.read()

                conn.execute(text(sql))
                conn.commit()
                print(f"  [OK] {nome} — View criada com sucesso.")

            except Exception as e:
                print(f"  [ERRO] {nome} — {e}")
                return 1

    print("\n" + "=" * 60)
    print("  [VIEWS] Todas as views foram criadas com sucesso!")
    print("=" * 60)

    # Verifica as views criadas
    with engine.connect() as conn:
        resultado = conn.execute(text("""
            SELECT table_name
            FROM information_schema.views
            WHERE table_schema = 'dw'
            ORDER BY table_name
        """))
        views = resultado.fetchall()

        print(f"\n  Views ativas no schema 'dw':")
        for row in views:
            print(f"    - dw.{row[0]}")

    print("\n" + "=" * 60 + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
