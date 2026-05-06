"""
Script de Inicializacao do Banco de Dados (DDL)

Responsavel por criar fisicamente os schemas ('oltp' e 'dw') e todas as tabelas
definidas nos modelos SQLAlchemy do projeto no banco PostgreSQL.

PRE-REQUISITOS:
    1. Arquivo .env configurado com a variavel DATABASE_URL apontando para o PostgreSQL.
    2. Dependencias instaladas via Poetry (poetry install).
    3. Os schemas 'oltp' e 'dw' devem existir previamente no banco
       (CREATE SCHEMA IF NOT EXISTS oltp; CREATE SCHEMA IF NOT EXISTS dw;).

EXECUCAO:
    poetry run python scripts/create_tables.py

NOTA DE IDEMPOTENCIA:
    O metodo 'Base.metadata.create_all()' do SQLAlchemy verifica a existencia das tabelas
    antes de cria-las. Portanto, executar este script multiplas vezes eh seguro — tabelas
    ja existentes nao serao recriadas nem terao seus dados apagados.
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.database import engine, Base
from models.oltp import Aluno, Curso, Matricula, ItemMatricula, Pagamento
from models.dw import DimAluno, DimCurso, DimStatus, DimTempo, FatoMatricula

def create_tables():
    print("\n--- [INIT] Iniciando a criacao das tabelas no banco de dados ---")
    
    try:
        # Tenta criar as tabelas (o SQLAlchemy usara os schemas definidos nos modelos)
        Base.metadata.create_all(bind=engine)
        
        print("SUCESSO: Tabelas dos schemas 'oltp' e 'dw' criadas/verificadas com sucesso!")
        print("\nTabelas processadas:")
        for table_name in Base.metadata.tables.keys():
            print(f" - {table_name}")
            
        print("\n--- [FINISH] Processo de inicializacao concluido ---")
        
    except Exception as e:
        print("\nERRO: Falha ao criar as tabelas.")
        print(f"Detalhes do erro: {e}")

if __name__ == "__main__":
    create_tables()
