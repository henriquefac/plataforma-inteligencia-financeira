import json
from fastapi import APIRouter, HTTPException
from pathlib import Path

from app.core.config import settingsInst

router = APIRouter()


@router.get("/")
async def list_artifacts():
    """
    Lista todos os artefatos de ingestão (metadados).
    Permite ao frontend saber quais datasets estão disponíveis.
    """
    metadata_dir = settingsInst.METADATA_DIR

    if not metadata_dir.exists():
        return {"artifacts": []}

    artifacts = []
    for file in sorted(metadata_dir.glob("*.json")):
        try:
            with open(file) as f:
                data = json.load(f)
            artifacts.append(data)
        except Exception:
            continue

    return {"artifacts": artifacts, "total": len(artifacts)}


@router.get("/{ingestion_id}")
async def get_artifact(ingestion_id: str):
    """
    Retorna os metadados de uma ingestão específica.
    """
    metadata_path = settingsInst.METADATA_DIR / f"{ingestion_id}.json"

    if not metadata_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Artefato não encontrado: {ingestion_id}"
        )

    try:
        with open(metadata_path) as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
