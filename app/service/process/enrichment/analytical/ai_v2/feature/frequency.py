from app.core.llm import llm_client
from .base import BaseFeature
import pandas as pd
from app.service.process.enrichment.analytical.ai_v2.prompt.frequency_prompt import (
    build_frequency_classification_prompt
)

class FrequencyFeature(BaseFeature):
    feature_name = "frequencia"

    def classify(self, text: str, values: list[str]) -> str:
        prompt = build_frequency_classification_prompt(text, values)

        response = llm_client.get_llm().complete(
            prompt=prompt
        )

        result = response.text.strip()

        # 🔒 garantir consistência
        values_lower = [v.lower() for v in values]

        if result.lower() in values_lower:
            return values[values_lower.index(result.lower())]

        return "Nao aplicavel"

    def apply(self, df: pd.DataFrame, values: list[str]) -> pd.DataFrame:
        df = df.copy()

        if "descricao" not in df.columns:
            raise ValueError("DataFrame precisa ter coluna 'descricao'")

        if "recorrencia" not in df.columns:
            raise ValueError("FrequencyFeature requer coluna 'recorrencia'")

        # só recorrentes
        mask = df["recorrencia"] == "Recorrente"

        unique_descriptions = df.loc[mask, "descricao"].dropna().unique()

        mapping = {}

        for desc in unique_descriptions:
            mapping[desc] = self.classify(desc, values)

        # aplica apenas onde é recorrente
        df[self.feature_name] = "Nao aplicavel"
        df.loc[mask, self.feature_name] = df.loc[mask, "descricao"].map(mapping)

        return df