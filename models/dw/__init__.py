from .dim_aluno import DimAluno
from .dim_curso import DimCurso
from .dim_status import DimStatus
from .dim_tempo import DimTempo
from .fato_matricula import FatoMatricula

# Exportacao facilitada para o DW
__all__ = ["DimAluno", "DimCurso", "DimStatus", "DimTempo", "FatoMatricula"]
