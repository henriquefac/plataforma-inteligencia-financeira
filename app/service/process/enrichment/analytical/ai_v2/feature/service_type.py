from app.core.llm import llm_client
from .base import BaseFeature
import pandas as pd
from app.service.process.enrichment.analytical.ai_v2.prompt.service_type_prompt import (
    build_service_type_prompt
)

class ServiceTypeFeature(BaseFeature):
    feature_name = "tipo_servico"

    def classify(self, text: str, values: list[str]) -> str:
        prompt = build_service_type_prompt(text, values)

        response = llm_client.get_llm().complete(prompt=prompt)
        result = response.text.strip()

        values_lower = [v.lower() for v in values]

        if result.lower() in values_lower:
            return values[values_lower.index(result.lower())]

        return "ServicoPontual"

    def apply(self, df: pd.DataFrame, values: list[str]) -> pd.DataFrame:
        df = df.copy()

        unique_descriptions = df["descricao"].dropna().unique()
        mapping = {}

        for desc in unique_descriptions:
            mapping[desc] = self.classify(desc, values)

        df[self.feature_name] = df["descricao"].map(mapping)

        return df