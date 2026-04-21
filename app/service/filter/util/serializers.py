"""
Funções de serialização para valores de filtro.

Converte tipos Python/pandas/numpy em tipos JSON-serializáveis
para envio ao frontend.
"""

from typing import Any

import pandas as pd


def serialize(value: Any) -> Any:
    """Converte valores para tipos JSON-serializáveis."""
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if hasattr(value, "item"):  # numpy scalar
        return value.item()
    return value
