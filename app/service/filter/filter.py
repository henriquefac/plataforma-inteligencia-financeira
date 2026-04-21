"""
FilterService — Serviço de filtragem para o dashboard.

Responsabilidades:
  1. Descobrir automaticamente os filtros disponíveis a partir do
     DataFrame enriquecido (colunas × tipos).
  2. Expor metadados de cada filtro para o frontend:
     - "range"  → slider (min, max) para valores contínuos e datas
     - "tag"    → lista de valores únicos para colunas categóricas
  3. Aplicar parâmetros de filtragem sobre o DataFrame e devolver
     apenas os registros de interesse.

Colunas excluídas da filtragem:
  - "descricao" (texto livre, não filtrável via slider/tag)
"""

import logging
from typing import Any, Optional

from app.domain import DataArtifact
import pandas as pd

from app.domain.schema import ENRICHED_SCHEMA, ColType
from app.service.filter.util import (
    RangeFilterMeta,
    TagFilterMeta,
    FilterMeta,
    EXCLUDED_COLUMNS,
    RANGE_TYPES,
    TAG_TYPES,
)

logger = logging.getLogger(__name__)


class FilterService:
    """
    Serviço de filtragem para o dashboard.

    Uso típico:
        service = FilterService()

        # 1. Descobre filtros a partir dos dados
        available = service.discover_filters(df)

        # 2. Aplica parâmetros vindos do frontend
        filtered_df = service.apply(df, params)
    """

    # ── Descoberta de filtros ──────────────────

    def discover_filters(self, data: DataArtifact) -> list[dict]:
        """
        Analisa o DataFrame e retorna a lista de filtros disponíveis
        com seus metadados (tipo, min/max ou valores).

        Apenas colunas presentes tanto no schema (`ENRICHED_SCHEMA`)
        quanto no DataFrame são consideradas. Colunas em
        `EXCLUDED_COLUMNS` são ignoradas.

        Returns:
            Lista de dicts, cada um descrevendo um filtro.
            Ex:
                [
                    {"column": "valor", "filter_type": "range",
                     "kind": "number", "min": 0.0, "max": 5000.0},
                    {"column": "status", "filter_type": "tag",
                     "values": ["pago", "pendente", "atrasado"]},
                    {"column": "data", "filter_type": "range",
                     "kind": "date", "min": "2024-01-01", "max": "2024-12-31"},
                ]
        """
        df = data.load_enriched()
        filters: list[FilterMeta] = []

        for col_name, col_type in ENRICHED_SCHEMA.items():
            if col_name in EXCLUDED_COLUMNS:
                continue
            if col_name not in df.columns:
                continue

            meta = self._build_filter_meta(df, col_name, col_type)
            if meta is not None:
                filters.append(meta)

        return [f.to_dict() for f in filters]

    # ── Aplicação de filtros ───────────────────

    def apply(
        self,
        df: pd.DataFrame,
        params: dict[str, Any],
    ) -> pd.DataFrame:
        """
        Filtra o DataFrame com base nos parâmetros recebidos.

        Args:
            df: DataFrame enriquecido completo.
            params: Dicionário de parâmetros de filtragem.
                Formato esperado:
                {
                    "valor": {"min": 100, "max": 5000},
                    "data":  {"min": "2024-01-01", "max": "2024-06-30"},
                    "status": ["pago", "pendente"],
                    "is_pago": [true],
                }

                - Para filtros range: dict com "min" e/ou "max".
                - Para filtros tag:   lista de valores selecionados.

        Returns:
            DataFrame filtrado contendo apenas os registros que
            satisfazem TODOS os filtros (interseção / AND).
        """
        if not params:
            return df

        mask = pd.Series(True, index=df.index)

        for col_name, criteria in params.items():
            if col_name in EXCLUDED_COLUMNS:
                logger.warning(
                    "Coluna '%s' está excluída dos filtros. Ignorando.",
                    col_name,
                )
                continue

            if col_name not in df.columns:
                logger.warning(
                    "Coluna '%s' não encontrada no DataFrame. Ignorando.",
                    col_name,
                )
                continue

            col_type = ENRICHED_SCHEMA.get(col_name)
            if col_type is None:
                logger.warning(
                    "Coluna '%s' não registrada no schema. Ignorando.",
                    col_name,
                )
                continue

            col_mask = self._apply_single_filter(df, col_name, col_type, criteria)
            mask &= col_mask

        filtered = df.loc[mask].copy()
        logger.info(
            "Filtro aplicado: %d → %d registros (%d removidos).",
            len(df), len(filtered), len(df) - len(filtered),
        )
        return filtered

    # ─────────────────────────────────────────
    # INTERNOS
    # ─────────────────────────────────────────

    def _build_filter_meta(
        self,
        df: pd.DataFrame,
        col_name: str,
        col_type: ColType,
    ) -> Optional[FilterMeta]:
        """Constrói o metadado de filtro para uma coluna."""

        if col_type in RANGE_TYPES:
            return self._build_range_meta(df, col_name, col_type)

        if col_type in TAG_TYPES:
            return self._build_tag_meta(df, col_name)

        return None

    def _build_range_meta(
        self,
        df: pd.DataFrame,
        col_name: str,
        col_type: ColType,
    ) -> Optional[RangeFilterMeta]:
        """Cria metadado de filtro range (slider)."""
        series = df[col_name].dropna()
        if series.empty:
            return None

        kind = "date" if col_type == ColType.DATETIME else "number"
        return RangeFilterMeta(
            column=col_name,
            kind=kind,
            min_value=series.min(),
            max_value=series.max(),
        )

    def _build_tag_meta(
        self,
        df: pd.DataFrame,
        col_name: str,
    ) -> Optional[TagFilterMeta]:
        """Cria metadado de filtro tag (seleção múltipla)."""
        unique_values = df[col_name].dropna().unique().tolist()
        if not unique_values:
            return None

        return TagFilterMeta(
            column=col_name,
            values=sorted(unique_values, key=str),
        )

    def _apply_single_filter(
        self,
        df: pd.DataFrame,
        col_name: str,
        col_type: ColType,
        criteria: Any,
    ) -> pd.Series:
        """
        Gera uma máscara booleana para um único filtro.

        Se criteria for dict → filtro range (min/max).
        Se criteria for list → filtro tag (valores selecionados).
        """
        if isinstance(criteria, dict):
            return self._apply_range_filter(df, col_name, col_type, criteria)
        elif isinstance(criteria, list):
            return self._apply_tag_filter(df, col_name, criteria)
        else:
            logger.warning(
                "Formato de filtro inválido para '%s': %s. Ignorando.",
                col_name, type(criteria).__name__,
            )
            return pd.Series(True, index=df.index)

    def _apply_range_filter(
        self,
        df: pd.DataFrame,
        col_name: str,
        col_type: ColType,
        criteria: dict,
    ) -> pd.Series:
        """Aplica filtro de faixa (min/max)."""
        mask = pd.Series(True, index=df.index)

        val_min = criteria.get("min")
        val_max = criteria.get("max")

        # Converter datas se necessário
        if col_type == ColType.DATETIME:
            if val_min is not None:
                val_min = pd.to_datetime(val_min, errors="coerce")
            if val_max is not None:
                val_max = pd.to_datetime(val_max, errors="coerce")

        if val_min is not None:
            mask &= df[col_name] >= val_min

        if val_max is not None:
            mask &= df[col_name] <= val_max

        return mask

    def _apply_tag_filter(
        self,
        df: pd.DataFrame,
        col_name: str,
        values: list,
    ) -> pd.Series:
        """Aplica filtro de seleção múltipla (isin)."""
        if not values:
            return pd.Series(True, index=df.index)
        return df[col_name].isin(values)