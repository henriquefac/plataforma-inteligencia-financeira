from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from app.service.filter import FilterService, FilterParams
from app.domain import DataArtifact

router = APIRouter()

# servico de filtro
filter_service = FilterService()

class DataRequest(BaseModel):
    ingestion_id: str = Field(..., description="ID de ingestão")
    filter_criteria: Optional[FilterParams] = Field(None, description="Critérios de filtro")


@router.get("/")
async def get_data(request: DataRequest):
    """
    Busca todos os registros do dataframe enriquecido. Os Registros
    sõ filtrados.
    """
    data = DataArtifact.load(request.ingestion_id)

    # Carregar data frame
    df = data.load_enriched()

    # converter critérios de filtragem para dicionário
    params = request.filter_criteria.to_service_dict()
    df = filter_service.apply(df, params)

    return {
        "data":df.to_dict(orient="records")
    }