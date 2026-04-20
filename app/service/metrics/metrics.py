import pandas as pd
from typing import Optional, Literal

from app.domain.data_artifact import DataArtifact, DataStatus
from app.service.metrics.base import Metric
from app.service.metrics.evolucao_temporal import criar_evolucao_temporal

# Métricas concretas
from app.service.metrics.receita.receita_metric import (
    ReceitaTotalMetric,
    ReceitaRealMetric,
    ReceitaInadimplenteMetric,
)
from app.service.metrics.ticket_medio.ticket_medio_metric import TicketMedioMetric
from app.service.metrics.inadimplencia.inadimplencia_metric import TaxaInadimplenciaMetric


# Registro das métricas disponíveis
METRICS_REGISTRY: list[Metric] = [
    ReceitaTotalMetric(),
    ReceitaRealMetric(),
    ReceitaInadimplenteMetric(),
    TicketMedioMetric(),
    TaxaInadimplenciaMetric(),
]


class MetricsService:
    """
    Serviço responsável por calcular métricas financeiras
    a partir dos dados enriquecidos, com suporte a filtros dinâmicos.
    
    Fluxo:
        1. Carrega o DataFrame enriquecido
        2. Aplica filtros dinâmicos (reduz registros, preserva colunas)
        3. Calcula métricas sobre o DataFrame filtrado
    """

    def __init__(self):
        self.metrics: list[Metric] = list(METRICS_REGISTRY)

    # -------------------------
    # FILTROS
    # -------------------------
    def _apply_filters(
        self,
        df: pd.DataFrame,
        status: Optional[list[str]] = None,
        cliente: Optional[str] = None,
        data: Optional[str] = None,
        recorrencia: Optional[list[str]] = None,
        tipo_servico: Optional[list[str]] = None,
    ) -> pd.DataFrame:
        """
        Aplica filtros dinâmicos ao DataFrame.
        
        - status, recorrencia, tipo_servico: aceitam lista de valores (OR)
        - cliente: busca parcial (texto)
        - data: filtra a partir desta data (>=)
        """
        filtered = df.copy()

        if status:
            status_lower = [s.lower() for s in status]
            filtered = filtered[filtered["status"].isin(status_lower)]

        if cliente:
            filtered = filtered[
                filtered["cliente"].str.contains(cliente.lower(), na=False)
            ]

        if data:
            dt = pd.to_datetime(data, errors="coerce")
            if pd.notna(dt):
                filtered = filtered[filtered["data"] >= dt]

        if recorrencia:
            if "recorrencia" in filtered.columns:
                rec_lower = [r.lower() for r in recorrencia]
                filtered = filtered[
                    filtered["recorrencia"].str.lower().isin(rec_lower)
                ]

        if tipo_servico:
            if "tipo_servico" in filtered.columns:
                ts_lower = [t.lower() for t in tipo_servico]
                filtered = filtered[
                    filtered["tipo_servico"].str.lower().isin(ts_lower)
                ]

        return filtered

    # -------------------------
    # CARREGAR DADOS
    # -------------------------
    def _load_enriched(self, ingestion_id: str) -> pd.DataFrame:
        """Carrega os dados enriquecidos de uma ingestão."""
        artifact = DataArtifact.load(ingestion_id)

        if artifact.status != DataStatus.ENRICHED:
            raise ValueError(
                f"Dados não estão enriquecidos (status: {artifact.status}). "
                f"Execute o pipeline completo antes de calcular métricas."
            )

        df = artifact.load_enriched()
        return df

    # -------------------------
    # COMPUTAR MÉTRICAS
    # -------------------------
    def compute(
        self,
        data_artifact: DataArtifact,
    ) -> dict:
        """
        Calcula todas as métricas registradas sobre o DataFrame filtrado.
        
        Cada métrica é executada apenas se suas colunas necessárias
        estiverem presentes no DataFrame. Caso contrário, retorna None.
        """

        df = data_artifact.load_enriched()

        # Calcular cada métrica registrada
        resultados = {}
        for metric in self.metrics:
            if metric.verify_columns_required(df):
                resultados[metric.name] = metric(df)
            else:
                resultados[metric.name] = None

        return {
            "ingestion_id": data_artifact.ingestion_id,
            "metricas": resultados,
        }

    # -------------------------
    # EVOLUÇÃO TEMPORAL
    # -------------------------
    def compute_temporal(
        self,
        ingestion_id: str,
        metric_name: str,
        freq: Literal["W", "M", "Q", "Y"] = "M",
        mode: Literal["pontual", "acumulativo"] = "pontual",
        status: Optional[list[str]] = None,
        cliente: Optional[str] = None,
        data: Optional[str] = None,
        recorrencia: Optional[list[str]] = None,
        tipo_servico: Optional[list[str]] = None,
    ) -> dict:
        """
        Calcula a evolução temporal de uma métrica específica.
        
        Args:
            metric_name: Nome da métrica registrada (ex: "receita_total", "ticket_medio")
            freq: Frequência de agrupamento ("W", "M", "Q", "Y")
            mode: "pontual" (valor por período) ou "acumulativo" (cumsum)
        
        Returns:
            Dicionário com vetores "datas" e "valores" prontos para gráficos.
        """
        # Encontrar a métrica pelo nome
        metric = self._get_metric_by_name(metric_name)

        df = self._load_enriched(ingestion_id)

        df = self._apply_filters(
            df,
            status=status,
            cliente=cliente,
            data=data,
            recorrencia=recorrencia,
            tipo_servico=tipo_servico,
        )

        resultado = criar_evolucao_temporal(
            df=df,
            metrica=metric,
            date_column="data",
            freq=freq,
            mode=mode,
        )

        return {
            "ingestion_id": ingestion_id,
            "total_registros_filtrados": len(df),
            **resultado,
        }

    def _get_metric_by_name(self, name: str) -> Metric:
        """Busca uma métrica registrada pelo nome."""
        for metric in self.metrics:
            if metric.name == name:
                return metric
        
        available = [m.name for m in self.metrics]
        raise ValueError(
            f"Métrica '{name}' não encontrada. "
            f"Métricas disponíveis: {available}"
        )

    def list_metrics(self) -> list[str]:
        """Lista os nomes de todas as métricas registradas."""
        return [m.name for m in self.metrics]
