import json
import logging
import asyncio
from typing import Optional

logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO) # User already added this, but getLogger is better

from app.core.llm import llm_client
from app.service.metrics import MetricsService
from app.service.filter import FilterParams
from app.core.cache import backend_cache
from app.domain.data_artifact import DataArtifact
from .deterministic_layer import DeterministicInsightsService
from .prompts import build_insights_prompt, build_anomaly_prompt
from .models import InsightResponse, AnomalyResponse

MAX_RETRIES = 3


class InsightsService:
    """
    Serviço de geração de insights automáticos via IA.
    Opera em duas camadas:
    1. Determinística: Cálculos matemáticos e estatísticos avançados.
    2. Não Determinística: Análise consultiva via LLM baseada nos fatos da camada 1.
    """

    def __init__(self):
        from app.service.filter import FilterService
        self.filter_service = FilterService()
        self.metrics_service = MetricsService(filter_service=self.filter_service)
        self.deterministic_service = DeterministicInsightsService()

    def _parse_llm_json(self, text: str) -> dict:
        """Tenta extrair JSON da resposta do LLM."""
        text = text.strip()

        # Tenta parsing direto
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Tenta extrair JSON de bloco markdown ```json ... ```
        if "```json" in text:
            try:
                start = text.index("```json") + 7
                end = text.index("```", start)
                return json.loads(text[start:end].strip())
            except (json.JSONDecodeError, ValueError):
                pass
        
        # Tenta extrair de bloco markdown genérico ``` ... ```
        if "```" in text:
            try:
                start = text.index("```") + 3
                end = text.index("```", start)
                content = text[start:end].strip()
                # Se o conteúdo começar com {, tenta parsear
                if content.startswith("{"):
                    return json.loads(content)
            except (json.JSONDecodeError, ValueError):
                pass

        # Tenta encontrar primeiro { e último }
        first_brace = text.find("{")
        last_brace = text.rfind("}")
        if first_brace != -1 and last_brace != -1:
            try:
                return json.loads(text[first_brace:last_brace + 1])
            except json.JSONDecodeError:
                pass

        # Se falhou em tudo, lança erro para gatilhar o retry
        raise ValueError(f"Não foi possível extrair um JSON válido da resposta: {text[:100]}...")

    async def _validate_and_sanitize(self, data: dict, model_class) -> dict:
        """
        Valida e limpa os dados usando o modelo Pydantic.
        Keywords novos serão cortados (extra='ignore').
        """
        try:
            validated = model_class(**data)
            return validated.model_dump()
        except Exception as e:
            raise ValueError(f"Validação de schema falhou: {e}")

    @backend_cache(ttl=3600)
    async def generate_insights(
        self,
        data_artifact: DataArtifact,
        filter_params: Optional[FilterParams] = None,
    ) -> dict:
        """
        Gera insights acionáveis via IA a partir dos dados enriquecidos.
        Usa a camada determinística para fornecer contexto rico ao LLM.
        """

        # 1. Calcular métricas básicas e avançadas (Camada Determinística)
        stats = self.metrics_service.compute(data_artifact, filter_params)
        
        df = data_artifact.load_enriched()
        df = self.metrics_service._apply_filters(df, filter_params)
        deterministic_insights = self.deterministic_service.calculate(df)

        # 2. Montar prompt com contexto completo
        full_context = {
            "metricas_basicas": stats["metricas"],
            "metricas_avancadas": deterministic_insights,
            "total_registros_analisados": len(df)
        }
        
        prompt = build_insights_prompt(full_context)

        # 3. Enviar ao LLM com Retry Loop
        last_error = None
        for attempt in range(MAX_RETRIES):
            try:
                llm = llm_client.get_llm(task="insights")
                response = await llm.acomplete(prompt)

                # 4. Parsear e Validar resposta
                insights_raw = self._parse_llm_json(response.text)
                insights = await self._validate_and_sanitize(insights_raw, InsightResponse)
                
                return insights
            except Exception as e:
                last_error = e
                logger.warning(f"⚠️ [Insights] Falha na tentativa {attempt + 1}/{MAX_RETRIES}: {e}")
                if attempt < MAX_RETRIES - 1:
                    # Pequeno delay antes de tentar de novo
                    await asyncio.sleep(1)
        
        # Se chegou aqui, todas as tentativas falharam
        raise last_error or RuntimeError("Falha ao gerar insights após múltiplas tentativas.")

    @backend_cache(ttl=3600)
    async def detect_anomalies(
        self,
        data_artifact: DataArtifact,
        filter_params: Optional[FilterParams] = None,
    ) -> dict:
        """
        Detecta padrões e anomalias via IA.
        """
        # 1. Calcular contexto (Camada Determinística)
        stats = self.metrics_service.compute(data_artifact, filter_params)
        df = data_artifact.load_enriched()
        df = self.metrics_service._apply_filters(df, filter_params)
        deterministic_insights = self.deterministic_service.calculate(df)

        full_context = {
            "metricas_basicas": stats["metricas"],
            "metricas_avancadas": deterministic_insights,
            "total_registros_analisados": len(df)
        }

        # 2. Montar prompt de anomalias
        prompt = build_anomaly_prompt(full_context)

        # 3. Enviar ao LLM com Retry Loop
        last_error = None
        for attempt in range(MAX_RETRIES):
            try:
                llm = llm_client.get_llm(task="insights")
                response = await llm.acomplete(prompt)

                # 4. Parsear e Validar resposta
                result_raw = self._parse_llm_json(response.text)
                result = await self._validate_and_sanitize(result_raw, AnomalyResponse)
                
                return result
            except Exception as e:
                last_error = e
                logger.warning(f"⚠️ [Anomalias] Falha na tentativa {attempt + 1}/{MAX_RETRIES}: {e}")
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(1)

        raise last_error or RuntimeError("Falha ao detectar anomalias após múltiplas tentativas.")

    def get_deterministic_metrics(
        self,
        data_artifact: DataArtifact,
        filter_params: Optional[FilterParams] = None,
    ) -> dict:
        """
        Retorna as métricas da camada determinística usadas para os insights.
        """
        stats = self.metrics_service.compute(data_artifact, filter_params)
        df = data_artifact.load_enriched()
        df = self.metrics_service._apply_filters(df, filter_params)
        deterministic_insights = self.deterministic_service.calculate(df)

        return {
            "metricas_basicas": stats["metricas"],
            "metricas_avancadas": deterministic_insights,
            "total_registros_analisados": len(df)
        }
