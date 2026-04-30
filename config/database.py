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

# Carrega as variáveis de ambiente do arquivo .env (caso exista)
load_dotenv()

# Recupera a URL de conexão com o banco de dados
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("A variável de ambiente DATABASE_URL não foi encontrada. Verifique seu arquivo .env.")

