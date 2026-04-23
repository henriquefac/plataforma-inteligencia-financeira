from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Literal

from pydantic import BaseModel, Field
from typing import Literal, Union

from app.service.metrics import MetricsService
from app.service.filter import FilterService, FilterParams
from app.domain import DataArtifact

router = APIRouter()
filter_service = FilterService()
metrics_service = MetricsService(filter_service)


# ─────────────────────────────────────────────
# REQUEST MODELS
# ─────────────────────────────────────────────

# Fomato esperado de filtro:

class MetricsRequest(BaseModel):
    """Corpo da requisição para cálculo de métricas consolidadas."""
    ingestion_id: str = Field(..., description="ID da ingestão")

    filter_criteria: Optional[FilterParams] = Field(None, description="Critérios de filtro")

class TemporalRequest(BaseModel):
    """Corpo da requisição para evolução temporal de métricas."""
    ingestion_id: str = Field(..., description="ID da ingestão")
    filter_criteria: Optional[FilterParams] = Field(None, description="Critérios de filtro")
    metric_names: list[str] = Field(
        ...,
        description=(
            "Lista de nomes das métricas para calcular evolução temporal. "
            "Ex: ['receita_total', 'receita_real'] para um gráfico de receita."
        ),
    )
    freq: Literal["W", "M", "Q", "Y"] = Field(
        "M",
        description="Frequência de agrupamento: W=semanal, M=mensal, Q=trimestral, Y=anual",
    )
    mode: Literal["pontual", "acumulativo"] = Field(
        "pontual",
        description="Modo de cálculo: 'pontual' (valor por período) ou 'acumulativo' (cumsum)",
    )


# ─────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────

@router.post("/")
def get_metrics(request: MetricsRequest):
    """
    Calcula todas as métricas consolidadas de uma ingestão,
    agrupadas por tipo de visualização (receita, ticket, taxa).

    Retorno:
        metricas.receita: {receita_total, receita_real, receita_inadimplente}
        metricas.ticket:  {ticket_medio}
        metricas.taxa:    {taxa_inadimplencia}
    """
    try:
        dados = DataArtifact.load(request.ingestion_id)
        resultado = metrics_service.compute(data_artifact=dados, filter_params=request.filter_criteria)
        return resultado

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/temporal")
def get_temporal(request: TemporalRequest):
    """
    Calcula a evolução temporal para as métricas selecionadas,
    agrupadas por grupo de visualização.

    Envie as métricas que deseja no campo `metric_names`.
    Os resultados são organizados por grupo para facilitar
    a renderização de gráficos separados.

    Exemplo de request:
        {
            "ingestion_id": "abc-123",
            "metric_names": ["receita_total", "receita_real"],
            "freq": "M",
            "mode": "pontual"
        }
    """
    try:
        dados = DataArtifact.load(request.ingestion_id)
        resultado = metrics_service.compute_temporal(
            data_artifact=dados,
            metric_names=request.metric_names,
            freq=request.freq,
            filter_params=request.filter_criteria,
            mode=request.mode,
        )
        return resultado

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/available")
def list_available_metrics():
    """
    Lista todas as métricas disponíveis e seus grupos de visualização.

    Útil para o frontend montar seletores dinâmicos de métricas.
    """
    return {
        "metrics": metrics_service.list_metrics(),
        "groups": metrics_service.list_groups(),
    }
