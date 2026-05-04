
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
