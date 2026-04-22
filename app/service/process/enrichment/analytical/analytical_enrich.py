import pandas as pd
from .ai_v2 import feature
from app.domain.feature_registry import FEATURE_VALUES


class AnalyticalEnrich:
    """
    Pipeline de enriquecimento de dados tabulares a partir do campo
    'descricao', usando llm para extrair valores para features determinadas.
    Uso de IA
    """

    PIPELINE = [
        "_enrich_recurrence_feature",
        "_enrich_frequency_feature",
        "_enrich_service_type_feature",
    ]

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        for step in self.PIPELINE:
            print(f"Passo da pipeline: {step}")
            df = getattr(self, step)(df)

        return df

    def _enrich_recurrence_feature(self, df: pd.DataFrame) -> pd.DataFrame:
        if "descricao" not in df.columns:
            return df

        df["descricao"] = df["descricao"].astype(str).str.lower()

        recurrence = feature.RecurrenceFeature()
        values = FEATURE_VALUES[recurrence.feature_name]

        df_ = recurrence.apply(df, values)
        return df_

    def _enrich_frequency_feature(self, df: pd.DataFrame) -> pd.DataFrame:
        # depende de recorrencia
        if "descricao" not in df.columns or "recorrencia" not in df.columns:
            return df

        frequency = feature.FrequencyFeature()
        values = FEATURE_VALUES[frequency.feature_name]

        df_ = frequency.apply(df, values)

        return df_
    
    def _enrich_service_type_feature(self, df: pd.DataFrame) -> pd.DataFrame:
        if "descricao" not in df.columns:
            return df

        service = feature.ServiceTypeFeature()
        values = FEATURE_VALUES[service.feature_name]

        df_ = service.apply(
            df, 
            values)
        return df_
    
