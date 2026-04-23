from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from app.service.filter import FilterService
from app.domain import DataArtifact

router = APIRouter()
filter_service = FilterService()

class FilterRequest(BaseModel):
    """Corpo da requisição para descoberta de filtros."""
    ingestion_id: str = Field(..., description="ID da ingestão")


@router.post("/")
def get_filters(request: FilterRequest):
    """
    Descobre os filtros disponíveis para uma ingestão específica.

    Retorna uma lista de filtros com seus metadados (tipo, min/max ou valores).
    """
    try:
        data = DataArtifact.load(request.ingestion_id)
        filters = filter_service.discover_filters(data)
        return {"filters": filters}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))