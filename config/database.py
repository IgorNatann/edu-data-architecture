"""
Configuração Central do Banco de Dados

Este arquivo é o 'coração' da nossa comunicação com o banco de dados. 
O desenvolvimento foi dividido logicamente em três etapas para garantir 
segurança, modularidade e controle transacional.

---
PASSO 1: CARREGAMENTO SEGURO (Gerenciamento de Credenciais)
O Problema: Precisamos conectar ao banco sem expor senhas no código-fonte.
O Raciocínio: Utilizamos 'python-dotenv' para carregar a variável DATABASE_URL
a partir de um arquivo .env externo, garantindo que o código fique seguro
mesmo quando versionado no GitHub.
---
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Carrega as variáveis de ambiente do arquivo .env (caso exista)
load_dotenv()

# Recupera a URL de conexão com o banco de dados
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("A variável de ambiente DATABASE_URL não foi encontrada. Verifique seu arquivo .env.")

"""
---
PASSO 2: O MOTOR (Engine) E A BASE DECLARATIVA
O Problema: O Python precisa de um 'tradutor' para conversar com o PostgreSQL 
usando a URL carregada. Também precisamos de um padrão para que nossas 
classes Python (Modelos) sejam entendidas como Tabelas do banco.
O Raciocínio: 
1. O 'create_engine' gerencia o pool de conexões (abrir e fechar portas de comunicação com o BD).
2. A 'declarative_base' serve como uma 'fôrma' ou classe mãe. Quando os modelos 
(ex: Aluno, Curso) herdarem dessa Base, o SQLAlchemy automaticamente mapeará 
esses modelos para o banco de dados.
---
"""

# Cria o motor (engine) de conexão com o banco
# pool_pre_ping=True verifica se a conexão ainda está viva antes de usá-la, útil em ambientes cloud
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Cria a classe Base da qual todos os nossos modelos (tabelas) irão herdar
Base = declarative_base()

"""
---
PASSO 3: O GERENCIADOR DE SESSÕES (Session)
O Problema: Temos a Engine para conectar, mas como executar consultas reais 
(INSERT, SELECT) de forma isolada, garantindo que se algo der errado possamos 
cancelar a operação (rollback)?
O Raciocínio: O 'sessionmaker' cria uma fábrica de sessões. Cada vez que 
precisarmos fazer uma operação no banco (ex: no nosso pipeline ETL), instanciamos 
uma nova sessão, realizamos a transação, e depois a fechamos.
---
"""

# Cria a fábrica de sessões (SessionLocal) vinculada à nossa engine
# autocommit=False: Nós mesmos decidimos quando "salvar" (dar o commit) manualmente.
# autoflush=False: Evita que o SQLAlchemy envie instruções pro banco prematuramente.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
