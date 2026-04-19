from fastapi import UploadFile, HTTPException
from pathlib import Path

from app.core.config import settingsInst
from app.domain.data_artifact import DataArtifact


class IngestService:

    def __init__(self):
        self.upload_dir: Path = settingsInst.UPLOAD_DIR

    async def ingest(self, file: UploadFile) -> DataArtifact:
        if not file.filename:
            raise HTTPException(400, "Arquivo sem nome")

        filename = file.filename.lower().replace(" ", "_")

        if Path(filename).suffix not in settingsInst.ALLOWED_EXTENSIONS:
            raise HTTPException(400, "Formato inválido")

        data = DataArtifact.create(file.filename)

        content = await file.read()

        if len(content) == 0:
            raise HTTPException(400, "Arquivo vazio")

        if len(content) > settingsInst.MAX_UPLOAD_SIZE:
            raise HTTPException(400, "Arquivo muito grande")

        try:
            data.save_raw(content)
        except Exception:
            # nada de armazenar erro no objeto
            raise HTTPException(500, "Erro ao salvar arquivo")

        return data