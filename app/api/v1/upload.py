from fastapi import APIRouter, UploadFile, HTTPException
from pathlib import Path
import uuid

from app.core.config import settingsInst

router = APIRouter()

EXTENSOES_VALIDAS = (".csv", ".xlsx")
MAX_SIZE = 10 * 1024 * 1024  # 10MB

@router.post("/upload")
async def upload_file(file: UploadFile):
    # Validar nome 
    if not file.filename:
        raise HTTPException(status_code=400, detail="Arquivo sem nome")
    
    filename = file.filename.lower()
    filename = filename.replace(" ", "_")


    if not filename.endswith(EXTENSOES_VALIDAS):
        raise HTTPException(
            status_code=400,
            detail="Formato inválido. Use CSV ou XLSX."
        )

    content = await file.read()
    # 4. Validar tamanho
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Arquivo vazio")

    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="Arquivo muito grande")

    # Gerar nome único (evita sobrescrever)
    unique_name = f"{uuid.uuid4()}_{file.filename}"

    filepath: Path = settingsInst.UPLOAD_DIR / unique_name

    with open(filepath, "wb") as f:
            f.write(content)

    return {
        "message": "Arquivo enviado com sucesso",
        "filename": unique_name,
        "path": str(filepath)
    }