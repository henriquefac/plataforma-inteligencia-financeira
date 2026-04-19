from typing import Literal
from pydantic import AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Annotated
from pydantic import BeforeValidator

from pathlib import Path
from app import BASEDIR

from .validators import (
    parse_cors, parse_extensoes, 
    parse_list_str, parse_max_size, 
    validate_colunas, validate_status)

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
    API_V1_STR: str = "app/api/v1"

    # extensões válidas
    ALLOWED_EXTENSIONS: Annotated[
        list[str],
        BeforeValidator(parse_extensoes)
    ] = [".csv", ".xlsx", "xls"]

    # tamanho máximo do arquivo
    MAX_UPLOAD_SIZE: Annotated[
        int,
        BeforeValidator(parse_max_size)
    ] = 10 * 1024 * 1024  # 10MB

    # estrutura esperada da planilha
    COLUNAS: Annotated[
        list[str],
        BeforeValidator(parse_list_str),
        BeforeValidator(validate_colunas),
    ] = ["valor", "status", "cliente", "descricao", "data"]

    STATUS_VALIDOS: Annotated[
        list[str],
        BeforeValidator(parse_list_str),
        BeforeValidator(validate_status),
    ] = ["pago", "pendente", "atrasado"]

    TIPOS_CLIENTES: Annotated[
        list[str],
        BeforeValidator(parse_list_str),
    ] = ["empresa", "loja", "startup"]

    # diretórios
    UPLOAD_DIR: Path = create_path("data/raw")
    PROCESS_DIR: Path = create_path("data/clean")
    ENRICH_DIR: Path = create_path("data/enrich")
    METADATA_DIR: Path = create_path("data/metadata")

    # CORS
    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str,
        BeforeValidator(parse_cors)
    ] = []

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
    LLM_BASE_URL: str = "http://localhost:11434"
    LLM_MODEL: str = "mistral"
    EMBEDDING_MODEL: str = "nomic-embed-text"

    # RAG
    VECTOR_STORE: Literal["faiss", "json"] = "json"


settingsInst = Settings()