import pandas as pd
from typing import Callable, Union, Literal

from app.service.metrics.base import Metric


def criar_evolucao_temporal(
    df: pd.DataFrame,
    metrica: Union[Metric, Callable[[pd.DataFrame], float]],
    date_column: str = "data",
    freq: Literal["W", "M", "Q", "Y"] = "M",
    mode: Literal["pontual", "acumulativo"] = "pontual",
) -> dict:
    """
    Calcula a evolução temporal de uma métrica sobre o DataFrame.
    
    O DataFrame já deve chegar filtrado. Esta função apenas agrupa por período
    e aplica a métrica em cada grupo.
    
    Args:
        df: DataFrame já filtrado com os registros de interesse.
        metrica: Instância de Metric (callable) ou qualquer função df → float.
        date_column: Nome da coluna de data no DataFrame.
        freq: Frequência do agrupamento temporal:
            - "W" = semanal
            - "M" = mensal
            - "Q" = trimestral
            - "Y" = anual
        mode: Modo de cálculo:
            - "pontual" = valor calculado isoladamente para cada período
            - "acumulativo" = valores acumulados incrementalmente ao longo do tempo
    
    Returns:
        Dicionário com:
            - "datas": lista de datetime (início de cada período) — eixo X
            - "valores": lista de float (valor da métrica) — eixo Y
            - "freq": frequência usada
            - "mode": modo usado
            - "metric_name": nome da métrica (se Metric) ou "custom"
    """
    if date_column not in df.columns:
        return {
            "datas": [],
            "valores": [],
            "freq": freq,
            "mode": mode,
            "metric_name": _get_metric_name(metrica),
        }
    
    df_temp = df.copy()
    df_temp[date_column] = pd.to_datetime(df_temp[date_column], errors="coerce")
    
    # Remover registros sem data válida
    df_temp = df_temp.dropna(subset=[date_column])
    
    if df_temp.empty:
        return {
            "datas": [],
            "valores": [],
            "freq": freq,
            "mode": mode,
            "metric_name": _get_metric_name(metrica),
        }
    
    # Agrupar por período
    df_temp["_periodo"] = df_temp[date_column].dt.to_period(freq)
    
    resultados = []
    for periodo, grupo in df_temp.groupby("_periodo", sort=True):
        valor = metrica(grupo)
        resultados.append({
            "periodo": periodo,
            "valor": valor,
        })
    
    resultado_df = pd.DataFrame(resultados)
    
    # Acumulativo: cumsum sobre os valores
    if mode == "acumulativo":
        resultado_df["valor"] = resultado_df["valor"].cumsum()
    
    # Converter períodos para datetime (início do período)
    datas = resultado_df["periodo"].apply(lambda p: p.start_time).tolist()
    valores = resultado_df["valor"].tolist()
    
    return {
        "datas": datas,
        "valores": valores,
        "freq": freq,
        "mode": mode,
        "metric_name": _get_metric_name(metrica),
    }


def _get_metric_name(metrica: Union[Metric, Callable]) -> str:
    """Extrai o nome da métrica, se disponível."""
    if isinstance(metrica, Metric):
        return metrica.name
    return getattr(metrica, "__name__", "custom")
