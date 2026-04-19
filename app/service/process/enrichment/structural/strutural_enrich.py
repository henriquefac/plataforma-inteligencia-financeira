import pandas as pd
from app.core.config import settingsInst


class StructuralEnrich:
    """
    Pipeline de enriquecimento estrutural de dados tabulares.
    Sem uso de IA.
    """

    # Pipeline declarativo (facilita manutenção e futuras extensões)
    PIPELINE = [
        "_enrich_datetime",
        "_enrich_status_flags",
        "_enrich_client_type",
        "_enrich_financials",
        "_enrich_cliente",
    ]

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        for step in self.PIPELINE:
            df = getattr(self, step)(df)

        return df

    def _enrich_datetime(self, df: pd.DataFrame) -> pd.DataFrame:
        if "data" not in df.columns:
            return df

        df["data"] = pd.to_datetime(df["data"], errors="coerce")

        df["ano"] = df["data"].dt.year
        df["mes"] = df["data"].dt.month
        df["dia"] = df["data"].dt.day
        df["dia_semana"] = df["data"].dt.dayofweek

        return df

    def _enrich_status_flags(self, df: pd.DataFrame) -> pd.DataFrame:
        if "status" not in df.columns:
            return df

        df["status"] = df["status"].astype(str).str.lower()

        df["is_pago"] = df["status"] == "pago"
        df["is_inadimplente"] = df["status"].isin(["inadimplente", "atrasado"])

        return df

    def _enrich_client_type(self, df: pd.DataFrame) -> pd.DataFrame:
        if "cliente" not in df.columns:
            return df

        list_cliente_type = settingsInst.TIPOS_CLIENTES

        cliente_col = df["cliente"].astype(str).str.lower()

        for tipo in list_cliente_type:
            df[tipo] = cliente_col.str.contains(
                rf"\b{tipo}\b", na=False
            )

        return df

    def _enrich_financials(self, df: pd.DataFrame) -> pd.DataFrame:
        if "valor" not in df.columns:
            return df

        df["valor"] = pd.to_numeric(df["valor"], errors="coerce")

        df["receita_potencial"] = df["valor"]

        df["receita_real"] = df["valor"].where(
            df.get("is_pago", False),
            0
        )

        return df

    def _enrich_cliente(self, df: pd.DataFrame) -> pd.DataFrame:
        if "cliente" not in df.columns or "valor" not in df.columns:
            return df

        df["qtd_transacoes_cliente"] = df.groupby("cliente")["cliente"].transform("count")
        df["valor_medio_cliente"] = df.groupby("cliente")["valor"].transform("mean")

        return df