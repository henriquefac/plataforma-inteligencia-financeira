import pandas as pd
from typing import Optional, Literal
from collections import defaultdict

from app.domain.data_artifact import DataArtifact, DataStatus
from app.service.metrics.base import Metric
from app.service.metrics.evolucao_temporal import criar_evolucao_temporal

from app.service.filter import FilterService, FilterParams


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
    a partir dos dados enriquecidos.
    
    Fluxo:
        1. Recebe DataArtifact e carrega o DataFrame enriquecido
        2. Calcula métricas, agrupando por grupo de visualização
        3. Calcula evolução temporal para métricas selecionadas
    """

    def __init__(self, filter_service: FilterService = None):
        self.filter_service = filter_service
        self.metrics: list[Metric] = list(METRICS_REGISTRY)

    # -------------------------
    # COMPUTAR MÉTRICAS
    # -------------------------
    def compute(
        self,
        data_artifact: DataArtifact,
        filter_params: FilterParams = None,
    ) -> dict:
        """
        Calcula todas as métricas registradas, agrupadas por
        grupo de visualização.
        
        Retorno organizado por grupo para facilitar a renderização
        de gráficos separados no dashboard.
        """
        df = data_artifact.load_enriched()

        if self.filter_service and filter_params:
            print("Usando filtros")
            params = filter_params.to_service_dict()
            print(params)
            df = self.filter_service.apply(df, params)
        

        # Agrupar resultados por grupo de visualização
        grupos: dict[str, dict] = defaultdict(dict)

        for metric in self.metrics:
            if metric.verify_columns_required(df):
                grupos[metric.group][metric.name] = metric(df)
            else:
                grupos[metric.group][metric.name] = None

        return {
            "ingestion_id": data_artifact.ingestion_id,
            "total_registros": len(df),
            "metricas": dict(grupos),
        }

    # -------------------------
    # EVOLUÇÃO TEMPORAL
    # -------------------------
    def compute_temporal(
        self,
        data_artifact: DataArtifact,
        metric_names: list[str],
        freq: Literal["W", "M", "Q", "Y"] = "M",
        mode: Literal["pontual", "acumulativo"] = "pontual",
        filter_params: FilterParams = None,
    ) -> dict:
        """
        Calcula a evolução temporal para uma lista de métricas,
        agrupando os resultados por grupo de visualização.
        
        Args:
            data_artifact: Artefato com os dados enriquecidos.
            metric_names: Lista de nomes das métricas desejadas.
                          Ex: ["receita_total", "receita_real"]
            freq: Frequência de agrupamento ("W", "M", "Q", "Y").
            mode: "pontual" ou "acumulativo".
            filter_params: Critérios de filtro.
        Returns:
            Dicionário com evolução temporal agrupada por grupo.
            Cada grupo contém as séries temporais das métricas solicitadas.
        """
        df = data_artifact.load_enriched()

        if self.filter_service and filter_params:
            df = self.filter_service.apply(df, filter_params.to_service_dict())

        # Resolver as métricas solicitadas
        metrics_to_compute = []
        for name in metric_names:
            metric = self._get_metric_by_name(name)
            metrics_to_compute.append(metric)

        # Calcular evolução temporal e agrupar por grupo
        grupos: dict[str, list[dict]] = defaultdict(list)

        for metric in metrics_to_compute:
            if not metric.verify_columns_required(df):
                grupos[metric.group].append({
                    "metric_name": metric.name,
                    "datas": [],
                    "valores": [],
                    "freq": freq,
                    "mode": mode,
                    "error": f"Colunas necessárias ausentes: {metric.required_columns}",
                })
                continue

            resultado = criar_evolucao_temporal(
                df=df,
                metrica=metric,
                date_column="data",
                freq=freq,
                mode=mode,
            )
            grupos[metric.group].append(resultado)

        return {
            "ingestion_id": data_artifact.ingestion_id,
            "total_registros": len(df),
            "freq": freq,
            "mode": mode,
            "evolucao": dict(grupos),
        }

    # -------------------------
    # UTILITÁRIOS
    # -------------------------
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

    def list_metrics(self) -> list[dict]:
        """Lista todas as métricas registradas com seus grupos."""
        return [
            {"name": m.name, "group": m.group}
            for m in self.metrics
        ]

    def list_groups(self) -> dict[str, list[str]]:
        """Lista os grupos e suas métricas."""
        grupos: dict[str, list[str]] = defaultdict(list)
        for m in self.metrics:
            grupos[m.group].append(m.name)
        return dict(grupos)

