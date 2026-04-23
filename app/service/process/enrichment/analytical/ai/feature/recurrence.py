from . import BaseFeature
from app.core.llm import llm_client
from pandas import DataFrame
import json

from app.service.process.enrichment.analytical.ai.prompts.retry_prompt import (
    generate_retry_prompt
)

from app.service.process.enrichment.analytical.ai.prompts.recurrence_prompt import (
    build_recurrence_classification_prompt,
    build_recurrence_discovery_prompt
)

from app.service.process.enrichment.analytical.ai.schema.recurrence_schema import (
    RecurrenceSchema,
    validate_schema
)


class RecurrenceFeature(BaseFeature):

    feature_name = "recorrencia"

    # -----------------------
    # 🔹 DISCOVERY COM RETRY
    # -----------------------
    def discover_values(self, df: DataFrame, max_retries=3):

        descs = df["descricao"].dropna().unique()[:50]
        prompt_base = build_recurrence_discovery_prompt(descs)

        last_error = None
        last_output = None

        for attempt in range(max_retries):

            if last_error:
                prompt = generate_retry_prompt(
                    last_error,
                    last_output,
                    prompt_base
                )
            else:
                prompt = prompt_base

            response = llm_client.get_llm(task="enrichment").complete(prompt)
            last_output = response.text

            try:
                # 🔹 parse
                raw = json.loads(response.text)

                # 🔹 valida schema
                schema = RecurrenceSchema(**raw)

                # 🔹 valida regras
                validate_schema(schema)

                return schema.recorrencia

            except Exception as e:
                last_error = str(e)
                print(f"[retry {attempt+1}] erro: {last_error}")

        raise ValueError("Falha ao gerar valores de recorrência")

    # -----------------------
    # 🔹 CLASSIFICAÇÃO
    # -----------------------
    def classify(self, text, values):

        text = str(text).lower()

        # 🔹 1. regra simples (rápida)
        for v in values:
            if v in text:
                return v

        # 🔹 2. fallback LLM
        prompt = build_recurrence_classification_prompt(text, values)
        
        response = llm_client.get_llm(task="enrichment").complete(prompt)

        result = response.text.strip().lower()

        if result in values:
            return result

        return "desconhecido"

    # -----------------------
    # 🔹 APPLY COM CACHE
    # -----------------------
    def apply(self, df: DataFrame, values) -> DataFrame:
        df = df.copy()
        cache = {}

        def classify_cached(text):

            key = str(text).lower()

            if key in cache:
                return cache[key]

            result = self.classify(key, values)

            cache[key] = result
            return result

        df[self.feature_name] = df["descricao"].apply(classify_cached)

        return df