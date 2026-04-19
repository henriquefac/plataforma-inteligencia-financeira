from fastapi import APIRouter, UploadFile, HTTPException


from app.service.ingestion.ingestion import IngestService
from app.service.process.preprocess import PreProcessService

router = APIRouter()

ingest_service = IngestService()
preprocess_service = PreProcessService()


@router.post("/upload")
async def upload_file(file: UploadFile):
    try:
        # 1. ingestão
        data = await ingest_service.ingest(file)

        # 2. preprocessamento
        result = preprocess_service.run(data)

        return {
            "ingestion_id": data.ingestion_id,
            "status": data.status,
            "resumo": {
                "linhas": result["linhas"],
                "invalidos": result["invalidos"]
            }
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))