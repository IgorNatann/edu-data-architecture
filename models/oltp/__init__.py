from .aluno import Aluno
from .curso import Curso
from .matricula import Matricula
from .item_matricula import ItemMatricula
from .pagamento import Pagamento

# Facilitar a importacao em massa
__all__ = ["Aluno", "Curso", "Matricula", "ItemMatricula", "Pagamento"]
