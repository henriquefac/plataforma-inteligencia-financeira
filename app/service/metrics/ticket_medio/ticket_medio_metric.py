import pandas as pd

from app.service.metrics.base import Metric


class TicketMedioMetric(Metric):
    """Ticket médio: média dos valores das transações."""
    
    @property
    def name(self) -> str:
        return "ticket_medio"
    
    @property
    def required_columns(self) -> list[str]:
        return ["valor"]
    
    def calculate(self, df: pd.DataFrame) -> float:
        if len(df) == 0:
            return 0.0
        return float(df["valor"].mean())
