import json
from typing import Optional

from app.core.llm import llm_client
from app.service.metrics import MetricsService
from .prompts import build_insights_prompt, build_anomaly_prompt


class InsightsService:
    """
    Serviço de geração de insights automáticos via LLM.
    Usa o MetricsService para calcular estatísticas e envia 
    um resumo ao modelo para análise inteligente.
    """

    def __init__(self):
        self.metrics_service = MetricsService()

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
            start = text.index("```json") + 7
            end = text.index("```", start)
            try:
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
        ingestion_id: str,
        status: Optional[str] = None,
        cliente: Optional[str] = None,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
        recorrencia: Optional[str] = None,
        tipo_servico: Optional[str] = None,
    ) -> dict:
        """
        Gera insights acionáveis via IA a partir dos dados enriquecidos.
        Aceita os mesmos filtros do MetricsService para insights contextualizados.
        """
        # 1. Calcular métricas (com filtros)
        stats = self.metrics_service.compute(
            ingestion_id=ingestion_id,
            status=status,
            cliente=cliente,
            data_inicio=data_inicio,
            data_fim=data_fim,
            recorrencia=recorrencia,
            tipo_servico=tipo_servico,
        )

        # 2. Montar prompt com resumo estatístico
        prompt = build_insights_prompt(stats)

        # 3. Enviar ao LLM
        llm = llm_client.get_llm()
        response = llm.complete(prompt)

        # 4. Parsear resposta
        insights = self._parse_llm_json(response.text)

        return {
            "ingestion_id": ingestion_id,
            "filtros_aplicados": stats.get("filtros_aplicados", {}),
            "total_registros_analisados": stats.get("total_registros_filtrados", 0),
            **insights,
        }

    def detect_anomalies(
        self,
        ingestion_id: str,
        status: Optional[str] = None,
        cliente: Optional[str] = None,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
        recorrencia: Optional[str] = None,
        tipo_servico: Optional[str] = None,
    ) -> dict:
        """
        Detecta padrões e anomalias via IA.
        """
        # 1. Calcular métricas (com filtros)
        stats = self.metrics_service.compute(
            ingestion_id=ingestion_id,
            status=status,
            cliente=cliente,
            data_inicio=data_inicio,
            data_fim=data_fim,
            recorrencia=recorrencia,
            tipo_servico=tipo_servico,
        )

        # 2. Montar prompt de anomalias
        prompt = build_anomaly_prompt(stats)

        # 3. Enviar ao LLM
        llm = llm_client.get_llm()
        response = llm.complete(prompt)

        # 4. Parsear resposta
        result = self._parse_llm_json(response.text)

        return {
            "ingestion_id": ingestion_id,
            "filtros_aplicados": stats.get("filtros_aplicados", {}),
            "total_registros_analisados": stats.get("total_registros_filtrados", 0),
            **result,
        }
