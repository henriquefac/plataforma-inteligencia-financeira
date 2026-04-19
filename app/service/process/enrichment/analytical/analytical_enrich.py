import pandas as pd
from .ai import feature

class AnalyticalEnrich:
    """
    Pipeline de enriquecimento de dados tabulares a partir do campo
    'descricao', usando llm para extrair valores para features determinadas.
    Uso de IA
    """

    # Pipeline declarativo (facilita manutenção e futuras extensões)
    PIPELINE = [
        "_enrich_recurrence_feature",
        #"_enrich_service_type_feature",
    ]


    def run(self, df:pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        for step in self.PIPELINE:
            print(f"Paso da pipleine: {step}")
            df = getattr(self, step)(df)

        return df

    def _enrich_recurrence_feature(self, df: pd.DataFrame) -> pd.DataFrame:
        if "descricao" not in df.columns:
            return df
        df["descricao"] = df["descricao"].astype(str).str.lower()

        recurrence = feature.RecurrenceFeature()

        # encontrar posíveis valores
        values = recurrence.discover_values(df)

        # aplicar classificação dos itens para os valores encontrados
        df_ = recurrence.apply(df, values)

        return df_

    def _enrich_service_type_feature(self, df: pd.DataFrame) -> pd.DataFrame:
        if "descricao" not in df.columns:
            return df
        df["descricao"] = df["descricao"].astype(str).str.lower()

        service_type = feature.ServiceTypeFeature()

        # econtrar possíveis valores
        values = service_type.discover_values(df)

        # aplicar classificação dos itens para os valores encontrados
        df_ = service_type.apply(df, values)

        return df_