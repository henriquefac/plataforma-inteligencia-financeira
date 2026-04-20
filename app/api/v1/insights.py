from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.service.insights import InsightsService

router = APIRouter()
insights_service = InsightsService()


@router.post("/{ingestion_id}")
async def generate_insights(
    ingestion_id: str,
    status: Optional[str] = Query(None),
    cliente: Optional[str] = Query(None),
    data_inicio: Optional[str] = Query(None),
    data_fim: Optional[str] = Query(None),
    recorrencia: Optional[str] = Query(None),
    tipo_servico: Optional[str] = Query(None),
):
    """
    Gera insights automáticos via IA sobre os dados financeiros.
    Aceita filtros para análise contextualizada.
    """
    try:
        result = insights_service.generate_insights(
            ingestion_id=ingestion_id,
            status=status,
            cliente=cliente,
            data_inicio=data_inicio,
            data_fim=data_fim,
            recorrencia=recorrencia,
            tipo_servico=tipo_servico,
        )
        return result

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{ingestion_id}/anomalies")
async def detect_anomalies(
    ingestion_id: str,
    status: Optional[str] = Query(None),
    cliente: Optional[str] = Query(None),
    data_inicio: Optional[str] = Query(None),
    data_fim: Optional[str] = Query(None),
    recorrencia: Optional[str] = Query(None),
    tipo_servico: Optional[str] = Query(None),
):
    """
    Identifica padrões e anomalias nos dados via IA.
    Aceita filtros para análise contextualizada.
    """
    try:
        result = insights_service.detect_anomalies(
            ingestion_id=ingestion_id,
            status=status,
            cliente=cliente,
            data_inicio=data_inicio,
            data_fim=data_fim,
            recorrencia=recorrencia,
            tipo_servico=tipo_servico,
        )
        return result

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
