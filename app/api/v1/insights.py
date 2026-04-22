from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from app.service.insights import InsightsService
from app.service.filter import FilterParams
from app.domain import DataArtifact

router = APIRouter()
insights_service = InsightsService()


# ─────────────────────────────────────────────
# REQUEST MODELS
# ─────────────────────────────────────────────

class InsightsRequest(BaseModel):
    """Corpo da requisição para geração de insights via IA."""
    ingestion_id: str = Field(..., description="ID da ingestão")
    filter_criteria: Optional[FilterParams] = Field(None, description="Critérios de filtro")


# ─────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────

@router.post("/")
async def generate_insights(request: InsightsRequest):
    """
    Gera insights automáticos via IA sobre os dados financeiros.
    Aceita filtros para análise contextualizada.
    """
    try:
        dados = DataArtifact.load(request.ingestion_id)
        
        result = insights_service.generate_insights(
            data_artifact=dados,
            filter_params=request.filter_criteria
        )
        return result

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/anomalies")
async def detect_anomalies(request: InsightsRequest):
    """
    Identifica padrões e anomalias nos dados via IA.
    Aceita filtros para análise contextualizada.
    """
    try:
        dados = DataArtifact.load(request.ingestion_id)
        
        result = insights_service.detect_anomalies(
            data_artifact=dados,
            filter_params=request.filter_criteria
        )
        return result

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
