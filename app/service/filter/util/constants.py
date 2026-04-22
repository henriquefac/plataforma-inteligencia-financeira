"""
Constantes usadas pelo FilterService.

- EXCLUDED_COLUMNS: colunas que não devem gerar filtros.
- RANGE_TYPES / TAG_TYPES: mapeamento ColType → estratégia de filtro.
"""

from app.domain.schema import ColType

# Colunas que NÃO devem gerar filtros
EXCLUDED_COLUMNS: set[str] = {"descricao"}

# Quais ColTypes geram Range e quais geram Tag
RANGE_TYPES: set[ColType] = {
    ColType.FLOAT,
    ColType.INT,
    ColType.DATETIME,
}

TAG_TYPES: set[ColType] = {
    ColType.STRING,
    ColType.BOOL,
}
