import pandas as pd

from app.service.metrics.base import Metric


class TaxaInadimplenciaMetric(Metric):
    """Taxa de inadimplência: proporção de registros inadimplentes sobre o total.
    
    Retorna um valor entre 0 e 100 (percentual).
    """
    
    @property
    def name(self) -> str:
        return "taxa_inadimplencia"

    @property
    def group(self) -> str:
        return "taxa"
    
    @property
    def required_columns(self) -> list[str]:
        return ["is_inadimplente"]
    
    def calculate(self, df: pd.DataFrame) -> float:
        total = len(df)
        if total == 0:
            return 0.0
        qtd_inadimplentes = int(df["is_inadimplente"].sum())
        return round((qtd_inadimplentes / total) * 100, 2)