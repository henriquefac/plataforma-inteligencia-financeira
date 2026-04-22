"""
Modelos de metadados de filtro.

Define as dataclasses que representam os metadados dos filtros
disponíveis para o frontend:
  - RangeFilterMeta → slider (min/max) para numéricos e datas
  - TagFilterMeta   → seleção múltipla para categóricos
"""

from dataclasses import dataclass, field
from typing import Any

from app.domain import MAP_COLL_NAMES
from app.service.filter.util.serializers import serialize


from pydantic import BaseModel, RootModel
from typing import Any, Dict, Union, List


@dataclass
class RangeFilterMeta:
    """
    Metadado de um filtro de faixa (slider).
    Usado para colunas numéricas (float/int) e datas.

    Attributes:
        column: Nome da coluna no DataFrame.
        kind: Subtipo do range — "number" ou "date".
        min_value: Valor mínimo encontrado nos dados.
        max_value: Valor máximo encontrado nos dados.
    """
    column: str
    kind: str  # "number" | "date"
    min_value: Any
    max_value: Any

    def to_dict(self) -> dict:
        return {
            "column": self.column,
            "column_name": MAP_COLL_NAMES.get(self.column, self.column),
            "filter_type": "range",
            "kind": self.kind,
            "min": serialize(self.min_value),
            "max": serialize(self.max_value),
        }


@dataclass
class TagFilterMeta:
    """
    Metadado de um filtro de seleção múltipla (tags).
    Usado para colunas categóricas / com valores limitados.

    Attributes:
        column: Nome da coluna no DataFrame.
        values: Lista de valores únicos possíveis.
    """
    column: str
    values: list[Any] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "column": self.column,
            "column_name": MAP_COLL_NAMES.get(self.column, self.column),
            "filter_type": "tag",
            "values": [serialize(v) for v in self.values],
        }


FilterMeta = RangeFilterMeta | TagFilterMeta


class RangeFilter(BaseModel):
    min: float | str | None = None
    max: float | str | None = None


FilterValue = Union[
    RangeFilter,     # range
    List[Any],       # tag
]

class FilterParams(RootModel[Dict[str, FilterValue]]):

    def to_service_dict(self) -> dict[str, Any]:
        result = {}

        for key, value in self.root.items():
            if isinstance(value, RangeFilter):
                result[key] = value.model_dump(exclude_none=True)
            else:
                result[key] = value

        return result