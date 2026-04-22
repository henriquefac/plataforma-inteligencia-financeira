from app.core.llm import llm_client
from app.service.process.enrichment.analytical.ai_v2.prompt.recurrence_prompt import (
    build_recurrence_classification_prompt
)
from .base import BaseFeature
import pandas as pd
from app.domain.feature_registry import FEATURE_VALUES


class RecurrenceFeature(BaseFeature):
    feature_name = "recorrencia"

    def classify(self, text: str, values: list[str]) -> str:
        prompt = build_recurrence_classification_prompt(text, values)

        response = llm_client.get_llm().complete(
            prompt
        ).text

        result = response.strip()

        values_lower = [v.lower() for v in values]

        if result.lower() in values_lower:
            # retorna no formato original
            return values[values_lower.index(result.lower())]

        return "desconhecido"

    def apply(self, df: pd.DataFrame, values: list[str]) -> pd.DataFrame:
        df = df.copy()
        if "descricao" not in df.columns:
            raise ValueError("DataFrame precisa ter coluna 'descricao'")

        unique_descriptions = df["descricao"].dropna().unique()

        mapping = {}

        for desc in unique_descriptions:
            mapping[desc] = self.classify(desc, values)

        df[self.feature_name] = df["descricao"].map(mapping)

        return df