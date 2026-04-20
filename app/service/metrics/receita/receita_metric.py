import pandas as pd

from app.service.metrics.base import Metric


class ReceitaTotalMetric(Metric):
    """Receita potencial (total): soma de todos os valores, independente de status."""
    
    @property
    def name(self) -> str:
        return "receita_total"

    @property
    def group(self) -> str:
        return "receita"
    
    @property
    def required_columns(self) -> list[str]:
        return ["valor"]
    
    def calculate(self, df: pd.DataFrame) -> float:
        return float(df["valor"].sum())


class ReceitaRealMetric(Metric):
    """Receita real: soma dos valores apenas dos registros com status 'pago'."""
    
    @property
    def name(self) -> str:
        return "receita_real"

    @property
    def group(self) -> str:
        return "receita"
    
    @property
    def required_columns(self) -> list[str]:
        return ["valor", "status"]
    
    def calculate(self, df: pd.DataFrame) -> float:
        pagos = df[df["status"] == "pago"]
        return float(pagos["valor"].sum())


class ReceitaInadimplenteMetric(Metric):
    """Receita inadimplente: soma dos valores dos registros marcados como inadimplentes."""
    
    @property
    def name(self) -> str:
        return "receita_inadimplente"

    @property
    def group(self) -> str:
        return "receita"
    
    @property
    def required_columns(self) -> list[str]:
        return ["valor", "is_inadimplente"]
    
    def calculate(self, df: pd.DataFrame) -> float:
        inadimplentes = df[df["is_inadimplente"] == True]
        return float(inadimplentes["valor"].sum())