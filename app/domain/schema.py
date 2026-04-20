"""
Schema centralizado do dataset enriquecido.

Define todas as colunas possíveis que o DataFrame pode conter após o
pipeline de enriquecimento (estrutural + analítico), junto com seus
tipos de dados esperados.

A função `apply_enriched_schema()` deve ser usada sempre que um
DataFrame enriquecido for carregado de disco (CSV), para garantir
que os tipos estejam corretos — especialmente booleanos e datas,
que o `pd.read_csv` interpreta como strings.
"""

import logging
from enum import Enum

import pandas as pd

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# TIPOS SUPORTADOS
# ─────────────────────────────────────────────

class ColType(str, Enum):
    """Tipos de dados suportados pelo sistema."""
    STRING = "string"
    FLOAT = "float64"
    INT = "Int64"             # Nullable integer (suporta NaN)
    BOOL = "boolean"          # Nullable boolean (suporta NaN)
    DATETIME = "datetime64"


# ─────────────────────────────────────────────
# SCHEMA DO DATASET ENRIQUECIDO
# ─────────────────────────────────────────────
# Cada entrada mapeia nome_coluna → ColType.
# Colunas presentes no DataFrame mas AUSENTES aqui
# serão preservadas sem conversão.
#
# IMPORTANTE: Se novas colunas forem adicionadas nos
# pipelines de enriquecimento, elas DEVEM ser registradas
# aqui para garantir consistência de tipos.
# ─────────────────────────────────────────────

ENRICHED_SCHEMA: dict[str, ColType] = {
    # ── Colunas originais (input do usuário) ──
    "cliente":    ColType.STRING,
    "valor":      ColType.FLOAT,
    "status":     ColType.STRING,
    "descricao":  ColType.STRING,
    "data":       ColType.DATETIME,

    # ── Enriquecimento estrutural: datetime ──
    "ano":        ColType.INT,
    "mes":        ColType.INT,
    "dia":        ColType.INT,
    "dia_semana": ColType.INT,

    # ── Enriquecimento estrutural: flags de status ──
    "is_pago":          ColType.BOOL,
    "is_inadimplente":  ColType.BOOL,

    # ── Enriquecimento estrutural: tipo de cliente ──
    # (default de settings.TIPOS_CLIENTES)
    # Se TIPOS_CLIENTES mudar no .env, atualize aqui também.
    "empresa":  ColType.BOOL,
    "loja":     ColType.BOOL,
    "startup":  ColType.BOOL,

    # ── Enriquecimento estrutural: financeiro ──
    "receita_potencial":      ColType.FLOAT,
    "receita_real":           ColType.FLOAT,
    "qtd_transacoes_cliente": ColType.INT,
    "valor_medio_cliente":    ColType.FLOAT,

    # ── Enriquecimento analítico (IA) ──
    "recorrencia":  ColType.STRING,
    "frequencia":   ColType.STRING,
    "tipo_servico": ColType.STRING,
}


# ─────────────────────────────────────────────
# CONVERSÃO
# ─────────────────────────────────────────────

def _convert_column(series: pd.Series, col_type: ColType) -> pd.Series:
    """
    Converte uma Series para o tipo especificado.
    Retorna a série original em caso de falha na conversão.
    """
    try:
        if col_type == ColType.DATETIME:
            return pd.to_datetime(series, errors="coerce")

        if col_type == ColType.BOOL:
            # pd.read_csv pode ler booleanos como:
            # - Python bool (True/False) — quando o CSV tem True/False
            # - string ("True"/"False") — em alguns casos
            # - numérico (1/0, 1.0/0.0) — quando salvo como int/float
            # O mapping precisa cobrir TODOS esses casos.
            mapping = {
                # Strings
                "true": True, "True": True, "TRUE": True,
                "false": False, "False": False, "FALSE": False,
                "1": True, "0": False,
                "1.0": True, "0.0": False,
                # Tipos nativos (pd.read_csv já converte para estes)
                True: True, False: False,
                1: True, 0: False,
                1.0: True, 0.0: False,
            }
            converted = series.map(mapping)
            return converted.astype("boolean")

        if col_type == ColType.FLOAT:
            return pd.to_numeric(series, errors="coerce").astype("float64")

        if col_type == ColType.INT:
            # Primeiro converte para numérico, depois para Int64 nullable
            return pd.to_numeric(series, errors="coerce").astype("Int64")

        if col_type == ColType.STRING:
            return series.astype("string")

    except Exception as e:
        logger.warning(
            "Falha ao converter coluna para tipo %s: %s. "
            "Mantendo tipo original.",
            col_type.value, e,
        )
        return series

    return series


# ─────────────────────────────────────────────
# FUNÇÃO PRINCIPAL
# ─────────────────────────────────────────────

def apply_enriched_schema(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica o ENRICHED_SCHEMA ao DataFrame, convertendo as colunas
    presentes para os tipos corretos.

    - Apenas converte colunas que EXISTEM no DataFrame.
    - Colunas ausentes no schema são preservadas sem alteração.
    - Erros de conversão são logados como warning, sem interromper.

    Args:
        df: DataFrame carregado de CSV (tipos possivelmente incorretos).

    Returns:
        DataFrame com os tipos corrigidos conforme o schema.
    """
    df = df.copy()

    converted_count = 0

    for col_name, col_type in ENRICHED_SCHEMA.items():
        if col_name not in df.columns:
            continue

        original_dtype = df[col_name].dtype
        df[col_name] = _convert_column(df[col_name], col_type)
        new_dtype = df[col_name].dtype

        if str(original_dtype) != str(new_dtype):
            converted_count += 1
            logger.debug(
                "Coluna '%s': %s → %s",
                col_name, original_dtype, new_dtype,
            )

    if converted_count > 0:
        logger.info(
            "Schema aplicado: %d coluna(s) convertida(s).", converted_count
        )

    return df
