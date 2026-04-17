from app.core.config import settingsInst as Settings

from llama_index.core import Settings as LlamaSettings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding


# Centralizar a conexão com a api do modelo de llm
# Além disso, essa única instancia vai ter toda a configuração já aplicada

class LLMClient:

    def __init__(self):
        self._llm = None
        self._embedding = None
        self._initialized = False

    def _init_llm(self):
        if Settings.LLM_PROVIDER == "ollama":
            return Ollama(
                model=Settings.LLM_MODEL,
                request_timeout=120.0,
            )

        raise ValueError(f"LLM provider não suportado: {Settings.LLM_PROVIDER}")

    def _init_embedding(self):
        if Settings.LLM_PROVIDER == "ollama":
            return OllamaEmbedding(
                model_name=Settings.EMBEDDING_MODEL
            )

        raise ValueError(f"Embedding provider não suportado: {Settings.LLM_PROVIDER}")

    def get_llm(self):
        if self._llm is None:
            self._llm = self._init_llm()
        return self._llm

    def get_embedding(self):
        if self._embedding is None:
            self._embedding = self._init_embedding()
        return self._embedding

    # Configura o llama index globalmente
    def initialize(self):
        if not self._initialized:
            LlamaSettings.llm = self.get_llm()
            LlamaSettings.embed_model = self.get_embedding()
            self._initialized = True

# Singleton global
llm_client = LLMClient()