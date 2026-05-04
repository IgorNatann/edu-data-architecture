
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.database import engine
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

def test_infrastructure():
    """
    Valida se a conexão com o banco está ativa e se os schemas
    necessários para o projeto (OLTP e DW) estão criados.
    """
    print("\n--- [TEST] Iniciando Validação de Infraestrutura ---")
    
    try:
        with engine.connect() as connection:
            # 1. Teste de Conectividade
            connection.execute(text("SELECT 1"))
            print("OK: Conexão com o servidor PostgreSQL.")

            # 2. Verificação de Schemas
            schemas = [os.getenv("SCHEMA_OLTP", "oltp"), os.getenv("SCHEMA_DW", "dw")]
            
            for schema in schemas:
                connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
                connection.commit() 
                print(f"OK: Schema '{schema}' verificado/criado.")

            print("--- [TEST] Infraestrutura Validada com Sucesso ---\n")
            return True
            
    except Exception as e:
        print(f"FAIL: Erro na validação de infraestrutura: {e}")
        return False

if __name__ == "__main__":
    test_infrastructure()
