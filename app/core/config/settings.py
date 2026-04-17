from typing import Literal, Any
from pydantic import AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Annotated
from pydantic import BeforeValidator

from pathlib import Path
from app import BASEDIR


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",") if i.strip()]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)

def create_path(path: str)-> Path:
    return BASEDIR / path

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    # Ambiente
    # Provavelmente não vou usar
    # ENVIRONMENT: Literal["local", "prod"] = "local" 

    # App
    PROJECT_NAME: str = "financial-insights"
    API_V1_STR: str = "src/app/api/v1"

    # Local para armazenar os arquivos
    UPLOAD_DIR: Path = create_path("data/raw")
    PROCESS_DIR: Path = create_path("data/clean")
    ENRICH_DIR: Path = create_path("data/enrich")

    # CORS
    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    # LLM
    LLM_PROVIDER: Literal["ollama", "openai"] = "ollama"
    LLM_MODEL: str = "llama3"
    EMBEDDING_MODEL: str = "nomic-embed-text"

    # RAG
    VECTOR_STORE: Literal["faiss", "json"] = "json"


settingsInst = Settings()