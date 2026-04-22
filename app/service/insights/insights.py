import json
from typing import Optional

from app.core.llm import llm_client
from app.service.metrics import MetricsService
from app.service.filter import FilterParams
from app.domain.data_artifact import DataArtifact
from .deterministic_layer import DeterministicInsightsService
from .prompts import build_insights_prompt, build_anomaly_prompt


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

        # Tenta encontrar primeiro { e último }
        first_brace = text.find("{")
        last_brace = text.rfind("}")
        if first_brace != -1 and last_brace != -1:
            try:
                return json.loads(text[first_brace:last_brace + 1])
            except json.JSONDecodeError:
                pass

        # Fallback: retorna como texto
        return {"raw_response": text}

    def generate_insights(
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

        # 3. Enviar ao LLM
        llm = llm_client.get_llm()
        response = llm.complete(prompt)

        # 4. Parsear resposta
        insights = self._parse_llm_json(response.text)
        
        # Retorna apenas o conteúdo de insights
        return insights

    def detect_anomalies(
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

        # 3. Enviar ao LLM
        llm = llm_client.get_llm()
        response = llm.complete(prompt)

        # 4. Parsear resposta
        result = self._parse_llm_json(response.text)
        
        # Retorna apenas anomalias e padrões
        return result

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
