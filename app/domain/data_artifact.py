import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from enum import Enum
import uuid
import pandas as pd

from app.core.config import settingsInst
from app.domain.schema import apply_enriched_schema


class DataStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSED = "processed"
    ENRICHED = "enriched"
    ERROR = "error"


@dataclass
class DataArtifact:
    ingestion_id: str
    original_filename: str
    filename: str

    raw_path: Path
    processed_path: Optional[Path] = None
    enriched_path: Optional[Path] = None

    status: DataStatus = DataStatus.UPLOADED

    # -------------------------
    # FACTORY
    # -------------------------
    @classmethod
    def create(cls, original_filename: str) -> "DataArtifact":
        ingestion_id = str(uuid.uuid4())
        safe_name = original_filename.lower().replace(" ", "_")
        filename = f"{ingestion_id}_{safe_name}"

        raw_path = settingsInst.UPLOAD_DIR / filename

        return cls(
            ingestion_id=ingestion_id,
            original_filename=original_filename,
            filename=filename,
            raw_path=raw_path,
        )

    # -------------------------
    # METADATA
    # -------------------------
    def _metadata_path(self) -> Path:
        return settingsInst.METADATA_DIR / f"{self.ingestion_id}.json"

    def _save_metadata(self):
        data = {
            "ingestion_id": self.ingestion_id,
            "original_filename": self.original_filename,
            "filename": self.filename,
            "raw_path": str(self.raw_path),
            "processed_path": str(self.processed_path) if self.processed_path else None,
            "enriched_path": str(self.enriched_path) if self.enriched_path else None,
            "status": self.status,
        }

        with open(self._metadata_path(), "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, ingestion_id: str) -> "DataArtifact":
        path = settingsInst.METADATA_DIR / f"{ingestion_id}.json"

        if not path.exists():
            raise FileNotFoundError(f"Ingestion_id não encontrado: {ingestion_id}")

        with open(path) as f:
            data = json.load(f)


        return cls(
            ingestion_id=data["ingestion_id"],
            original_filename=data["original_filename"],
            filename=data["filename"],
            raw_path=Path(data["raw_path"]),
            processed_path=Path(data["processed_path"]) if data["processed_path"] else None,
            enriched_path=Path(data["enriched_path"]) if data["enriched_path"] else None,
            status=DataStatus(data["status"]),
        )

    # -------------------------
    # IO - WRITE
    # -------------------------
    def save_raw(self, content: bytes):
        with open(self.raw_path, "wb") as f:
            f.write(content)

        self._save_metadata()

    def save_processed(self, df: pd.DataFrame):
        path = self._build_processed_path()
        df.to_csv(path, index=False)
        self.processed_path = path
        self.status = DataStatus.PROCESSED
        self._save_metadata()

    def save_enriched(self, df: pd.DataFrame):
        path = self._build_enriched_path()
        df.to_csv(path, index=False)
        self.enriched_path = path
        self.status = DataStatus.ENRICHED
        self._save_metadata()

    # -------------------------
    # IO - READ
    # -------------------------
    def load_raw(self) -> pd.DataFrame:
        return self._read_file(self.raw_path)

    def load_processed(self) -> pd.DataFrame:
        if not self.processed_path:
            raise ValueError("Dados processados não disponíveis")
        return pd.read_csv(self.processed_path)

    def load_enriched(self) -> pd.DataFrame:
        if not self.enriched_path:
            raise ValueError("Dados enriquecidos não disponíveis")

        df = pd.read_csv(self.enriched_path)
        print(df["is_inadimplente"])
        df = apply_enriched_schema(df)
        print(df["is_inadimplente"])
        return df

    # -------------------------
    # HELPERS
    # -------------------------
    def _read_file(self, path: Path) -> pd.DataFrame:
        if path.suffix == ".csv":
            return pd.read_csv(path)
        elif path.suffix in [".xlsx", ".xls"]:
            return pd.read_excel(path)
        else:
            raise ValueError(f"Formato não suportado: {path.suffix}")

    def _build_processed_path(self) -> Path:
        return settingsInst.PROCESS_DIR / self.filename.replace(".xlsx", ".csv")

    def _build_enriched_path(self) -> Path:
        return settingsInst.ENRICH_DIR / self.filename.replace(".xlsx", ".csv")