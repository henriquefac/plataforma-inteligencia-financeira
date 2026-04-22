import pandas as pd

from app.service.metrics.base import Metric


class TicketMedioMetric(Metric):
    """Ticket médio: média dos valores das transações."""
    
    @property
    def name(self) -> str:
        return "ticket_medio"

    @property
    def group(self) -> str:
        return "ticket"
    
    @property
    def required_columns(self) -> list[str]:
        return ["valor"]
    
    def calculate(self, df: pd.DataFrame) -> float:
        if len(df) == 0:
            return 0.0
        val = df["valor"].mean()
        return float(val) if pd.notna(val) else 0.0
    
class TicketMedioPago(Metric):
    """Ticket médio em relação aos registros cujo estatus é pago"""

    @property
    def name(self) -> str:
        return "ticket_medio_pago"
    @property
    def group(self) -> str:
        return "ticket"
    
    @property
    def required_columns(self) -> list[str]:
        return ["valor", "status"]
    
    def calculate(self, df: pd.DataFrame) -> float:
        if len(df) == 0:
            return 0.0
        val = df[df["status"] == "pago"]["valor"].sum()
        return float(val) if pd.notna(val) else 0.0


class TicketMedioPendente(Metric):
    """Ticket médio em relação aos registros cujo estatus é pendente"""

    @property
    def name(self) -> str:
        return "ticket_medio_pendente"
    
    @property
    def group(self) -> str:
        return "ticket"

    @property
    def required_columns(self) -> list[str]:
        return ["valor", "status"]
    
    def calculate(self, df: pd.DataFrame) -> float:
        if len(df) == 0:
            return 0.0
        val = df[df["status"] == "pendente"]["valor"].sum()
        return float(val) if pd.notna(val) else 0.0

class TicketMedioInadimplente(Metric):
    """Ticket médio em relação aos registros cujo estatus é estrasado"""

    @property
    def name(self) -> str:
        return "ticket_medio_inadimplente"
    
    @property
    def group(self) -> str:
        return "ticket"
    
    @property
    def required_columns(self) -> list[str]:
        return ["valor", "status"]
    
    def calculate(self, df: pd.DataFrame) -> float:
        if len(df) == 0:
            return 0.0
        val = df[df["status"] == "atrasado"]["valor"].sum()
        return float(val) if pd.notna(val) else 0.0
