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

    # Diretório para índices vetoriais (RAG)
    INDEX_DIR: Path = create_path("data/indices")


    # LLM
    LLM_PROVIDER: Literal["ollama", "openai", "openrouter"] = "openrouter"
    
    # Provedores específicos por tarefa
    ENRICHMENT_LLM_PROVIDER: Literal["ollama", "openai", "openrouter"] = "ollama"
    INSIGHTS_LLM_PROVIDER: Literal["ollama", "openai", "openrouter"] = "openrouter"
    RAG_LLM_PROVIDER: Literal["ollama", "openai", "openrouter"] = "openrouter"

    LLM_BASE_URL: str = "http://localhost:11434"
    LLM_MODEL: str = "mistral"
    EMBEDDING_MODEL: str = "nomic-embed-text"
    LLM_TIMEOUT: float = 360.0  # Timeout em segundos para requisições ao LLM

    # OpenRouter
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "meta-llama/llama-3.3-70b-instruct:free"
    OPENROUTER_FALLBACK_MODELS: list[str] = [
        "meta-llama/llama-3.3-70b-instruct:free",
        "nvidia/nemotron-3-super-120b-a12b:free"
        "google/gemma-3-27b-it:free"
        "google/gemma-3-12b-it:free",
        "google/gemma-2-9b-it:free",
        "openrouter/free"
    ]

    # RAG
    VECTOR_STORE: Literal["faiss", "json"] = "json"

    # Teste / Desenvolvimento
    # Se True, apaga todos os dados gerados (raw, clean, enrich, etc.)
    # ao encerrar a API. Útil para testes.
    CLEAR_DATA_ON_SHUTDOWN: bool = False


settingsInst = Settings()