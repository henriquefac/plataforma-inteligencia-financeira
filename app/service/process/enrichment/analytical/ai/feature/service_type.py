from . import BaseFeature
from app.core.llm import llm_client
from pandas import DataFrame
import json

from app.service.process.enrichment.analytical.ai.prompts.retry_prompt import (
    generate_retry_prompt
)

from app.service.process.enrichment.analytical.ai.prompts.service_type_prompt import (
    build_service_type_discovery_prompt,
    build_service_type_classification_prompt
)

from app.service.process.enrichment.analytical.ai.schema.service_type_schema import (
    ServiceTypeSchema,
    validate_schema
)


class ServiceTypeFeature(BaseFeature):

    feature_name = "tipo_servico"

    # -----------------------
    # 🔹 DISCOVERY
    # -----------------------
    def discover_values(self, df:DataFrame, max_retries=3):

        descs = df["descricao"].dropna().unique()[:50]
        prompt_base = build_service_type_discovery_prompt(descs)

        last_error = None
        last_output = None

        for attempt in range(max_retries):

            prompt = (
                generate_retry_prompt(last_error, last_output, prompt_base)
                if last_error else prompt_base
            )

            response = llm_client.get_llm(task="enrichment").complete(prompt)
            last_output = response.text

            try:
                raw = json.loads(response.text)

                schema = ServiceTypeSchema(**raw)

                validate_schema(schema)

                values = list(set([v.lower().strip() for v in schema.tipo_servico]))

                if not values:
                    raise ValueError("Lista vazia")

                return values

            except Exception as e:
                last_error = str(e)
                print(f"[retry {attempt+1}] erro: {last_error}")

        raise ValueError("Falha ao gerar tipo de serviço")

    # -----------------------
    # 🔹 CLASSIFY
    # -----------------------
    def classify(self, text, values):

        text = str(text).lower()

        # 🔹 heurística simples
        for v in values:
            if v in text:
                return v

        # 🔹 fallback LLM
        prompt = build_service_type_classification_prompt(text, values)

        response = llm_client.get_llm(task="enrichment").complete(prompt)

        result = response.text.strip().lower()

        if result in values:
            return result

        return "outros"

    # -----------------------
    # 🔹 APPLY
    # -----------------------
    def apply(self, df:DataFrame, values)->DataFrame:

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