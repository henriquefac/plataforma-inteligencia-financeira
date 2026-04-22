from typing import Any, List, Optional
import logging

from app.core.config import settingsInst as Settings

from openrouter import OpenRouter

from llama_index.core import Settings as LlamaSettings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core.llms import (
    CustomLLM, 
    CompletionResponse, 
    LLMMetadata, 
    ChatMessage, 
    ChatResponse
)

logger = logging.getLogger(__name__)

# Centralizar a conexão com a api do modelo de llm
# Além disso, essa única instancia vai ter toda a configuração já aplicada

class OpenRouterLLM(CustomLLM):
    """Wrapper para a biblioteca openrouter compatível com LlamaIndex com fallback interno entre modelos."""
    api_key: str
    models: List[str]

    def __init__(self, api_key: str, models: List[str], **kwargs):
        super().__init__(api_key=api_key, models=models, **kwargs)

    @property
    def metadata(self) -> LLMMetadata:
        return LLMMetadata(
            model_name=self.models[0] if self.models else "openrouter",
            is_chat_model=True,
        )

    def _complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        last_error = None
        for model in self.models:
            try:
                print(f"🚀 [OpenRouter] Tentando modelo: {model}...")
                with OpenRouter(api_key=self.api_key) as client:
                    response = client.chat.send(
                        model=model,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    print(f"✅ [OpenRouter] Sucesso com modelo: {model}")
                    return CompletionResponse(
                        text=response.choices[0].message.content,
                        additional_kwargs={"model_name": model}
                    )
            except Exception as e:
                print(f"❌ [OpenRouter] Falha no modelo {model}: {e}")
                last_error = e
        
        raise last_error or RuntimeError("Todos os modelos do OpenRouter falharam.")

    def _chat(self, messages: List[ChatMessage], **kwargs: Any) -> ChatResponse:
        msgs = [{"role": m.role.value, "content": m.content} for m in messages]
        last_error = None
        for model in self.models:
            try:
                print(f"🚀 [OpenRouter] Tentando modelo: {model}...")
                with OpenRouter(api_key=self.api_key) as client:
                    response = client.chat.send(
                        model=model,
                        messages=msgs
                    )
                    print(f"✅ [OpenRouter] Sucesso com modelo: {model}")
                    return ChatResponse(
                        message=ChatMessage(
                            role="assistant", 
                            content=response.choices[0].message.content
                        ),
                        additional_kwargs={"model_name": model}
                    )
            except Exception as e:
                print(f"❌ [OpenRouter] Falha no modelo {model}: {e}")
                last_error = e
        
        raise last_error or RuntimeError("Todos os modelos do OpenRouter falharam.")

    def _stream_complete(self, prompt: str, **kwargs: Any):
        raise NotImplementedError("Streaming não implementado.")

    def _stream_chat(self, messages: List[ChatMessage], **kwargs: Any):
        raise NotImplementedError("Streaming não implementado.")

    def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        return self._complete(prompt, **kwargs)

    def chat(self, messages: List[ChatMessage], **kwargs: Any) -> ChatResponse:
        return self._chat(messages, **kwargs)

    def stream_complete(self, prompt: str, **kwargs: Any):
        return self._stream_complete(prompt, **kwargs)

    def stream_chat(self, messages: List[ChatMessage], **kwargs: Any):
        return self._stream_chat(messages, **kwargs)

class FallbackLLM(CustomLLM):
    """LLM que tenta um provedor primário e usa um fallback em caso de erro."""
    primary: Any
    fallback: Any

    def __init__(self, primary: Any, fallback: Any, **kwargs):
        super().__init__(primary=primary, fallback=fallback, **kwargs)

    @property
    def metadata(self) -> LLMMetadata:
        return self.primary.metadata

    def _complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        try:
            res = self.primary.complete(prompt, **kwargs)
            # Garantir que o model_name esteja presente
            if "model_name" not in res.additional_kwargs:
                res.additional_kwargs["model_name"] = self.primary.metadata.model_name
            return res
        except Exception as e:
            print(f"⚠️ [LLM] Falha total no provedor primário, usando fallback (Ollama/Local)...")
            res = self.fallback.complete(prompt, **kwargs)
            # Adicionar model_name do fallback
            if "model_name" not in res.additional_kwargs:
                res.additional_kwargs["model_name"] = f"ollama/{self.fallback.model}"
            return res

    def _chat(self, messages: List[ChatMessage], **kwargs: Any) -> ChatResponse:
        try:
            res = self.primary.chat(messages, **kwargs)
            if "model_name" not in res.additional_kwargs:
                res.additional_kwargs["model_name"] = self.primary.metadata.model_name
            return res
        except Exception as e:
            print(f"⚠️ [LLM] Falha total no provedor primário, usando fallback (Ollama/Local)...")
            res = self.fallback.chat(messages, **kwargs)
            if "model_name" not in res.additional_kwargs:
                res.additional_kwargs["model_name"] = f"ollama/{self.fallback.model}"
            return res

    def _stream_complete(self, prompt: str, **kwargs: Any):
        try:
            return self.primary.stream_complete(prompt, **kwargs)
        except Exception as e:
            logger.warning(f"Erro no streaming do LLM primário, usando fallback: {e}")
            return self.fallback.stream_complete(prompt, **kwargs)

    def _stream_chat(self, messages: List[ChatMessage], **kwargs: Any):
        try:
            return self.primary.stream_chat(messages, **kwargs)
        except Exception as e:
            logger.warning(f"Erro no streaming do LLM primário, usando fallback: {e}")
            return self.fallback.stream_chat(messages, **kwargs)

    def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        return self._complete(prompt, **kwargs)

    def chat(self, messages: List[ChatMessage], **kwargs: Any) -> ChatResponse:
        return self._chat(messages, **kwargs)

    def stream_complete(self, prompt: str, **kwargs: Any):
        return self._stream_complete(prompt, **kwargs)

    def stream_chat(self, messages: List[ChatMessage], **kwargs: Any):
        return self._stream_chat(messages, **kwargs)

class LLMClient:

    def __init__(self):
        self._llm = None
        self._embedding = None
        self._initialized = False

    def _init_llm(self):
        # Ollama sempre como fallback ou provedor principal direto
        ollama_llm = Ollama(
            model=Settings.LLM_MODEL,
            base_url=Settings.LLM_BASE_URL,
            request_timeout=Settings.LLM_TIMEOUT,
        )

        if Settings.LLM_PROVIDER == "ollama":
            print(f"🏠 [LLM] Provedor configurado: Ollama (Modelo: {Settings.LLM_MODEL})")
            return ollama_llm
        
        if Settings.LLM_PROVIDER == "openrouter":
            if not Settings.OPENROUTER_API_KEY:
                print("⚠️ [LLM] OPENROUTER_API_KEY não configurada. Usando Ollama como fallback direto.")
                return ollama_llm
            
            # Lista de modelos para fallback interno
            models = Settings.OPENROUTER_FALLBACK_MODELS
            if not models:
                models = [Settings.OPENROUTER_MODEL]
            
            primary = OpenRouterLLM(
                api_key=Settings.OPENROUTER_API_KEY,
                models=models
            )
            print(f"🌐 [LLM] Provedor configurado: OpenRouter (Multi-model Fallback) + Ollama")
            return FallbackLLM(primary=primary, fallback=ollama_llm)

        raise ValueError(f"LLM provider não suportado: {Settings.LLM_PROVIDER}")

    def _init_embedding(self):
        # Por enquanto mantemos embedding local no Ollama por performance/custo
        return OllamaEmbedding(
            model_name=Settings.EMBEDDING_MODEL,
            base_url=Settings.LLM_BASE_URL,
        )

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