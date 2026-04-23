from typing import Any, List, Optional
import logging
import time
import requests
import httpx
import asyncio

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
                with httpx.Client(timeout=Settings.LLM_TIMEOUT) as client:
                    response = client.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": model,
                            "messages": [{"role": "user", "content": prompt}]
                        }
                    )
                    response.raise_for_status()
                    data = response.json()
                    print(f"✅ [OpenRouter] Sucesso com modelo: {model}")
                    return CompletionResponse(
                        text=data["choices"][0]["message"]["content"],
                        additional_kwargs={"model_name": model}
                    )
            except Exception as e:
                print(f"❌ [OpenRouter] Falha no modelo {model}: {e}")
                last_error = e
        
        raise last_error or RuntimeError("Todos os modelos do OpenRouter falharam.")

    async def _acomplete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        last_error = None
        for model in self.models:
            try:
                print(f"🚀 [OpenRouter] Tentando modelo (async): {model}...")
                async with httpx.AsyncClient(timeout=Settings.LLM_TIMEOUT) as client:
                    response = await client.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": model,
                            "messages": [{"role": "user", "content": prompt}]
                        }
                    )
                    response.raise_for_status()
                    data = response.json()
                    print(f"✅ [OpenRouter] Sucesso com modelo (async): {model}")
                    return CompletionResponse(
                        text=data["choices"][0]["message"]["content"],
                        additional_kwargs={"model_name": model}
                    )
            except Exception as e:
                print(f"❌ [OpenRouter] Falha no modelo {model} (async): {e}")
                last_error = e
        
        raise last_error or RuntimeError("Todos os modelos do OpenRouter falharam.")

    def _chat(self, messages: List[ChatMessage], **kwargs: Any) -> ChatResponse:
        msgs = [{"role": m.role.value, "content": m.content} for m in messages]
        last_error = None
        for model in self.models:
            try:
                print(f"🚀 [OpenRouter] Tentando modelo (chat): {model}...")
                with httpx.Client(timeout=Settings.LLM_TIMEOUT) as client:
                    response = client.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": model,
                            "messages": msgs
                        }
                    )
                    response.raise_for_status()
                    data = response.json()
                    print(f"✅ [OpenRouter] Sucesso com modelo: {model}")
                    return ChatResponse(
                        message=ChatMessage(
                            role="assistant", 
                            content=data["choices"][0]["message"]["content"]
                        ),
                        additional_kwargs={"model_name": model}
                    )
            except Exception as e:
                print(f"❌ [OpenRouter] Falha no modelo {model}: {e}")
                last_error = e
        
        raise last_error or RuntimeError("Todos os modelos do OpenRouter falharam.")

    async def _achat(self, messages: List[ChatMessage], **kwargs: Any) -> ChatResponse:
        msgs = [{"role": m.role.value, "content": m.content} for m in messages]
        last_error = None
        for model in self.models:
            try:
                print(f"🚀 [OpenRouter] Tentando modelo (achat): {model}...")
                async with httpx.AsyncClient(timeout=Settings.LLM_TIMEOUT) as client:
                    response = await client.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": model,
                            "messages": msgs
                        }
                    )
                    response.raise_for_status()
                    data = response.json()
                    print(f"✅ [OpenRouter] Sucesso com modelo (async): {model}")
                    return ChatResponse(
                        message=ChatMessage(
                            role="assistant", 
                            content=data["choices"][0]["message"]["content"]
                        ),
                        additional_kwargs={"model_name": model}
                    )
            except Exception as e:
                print(f"❌ [OpenRouter] Falha no modelo {model} (async): {e}")
                last_error = e
        
        raise last_error or RuntimeError("Todos os modelos do OpenRouter falharam.")

    def _stream_complete(self, prompt: str, **kwargs: Any):
        raise NotImplementedError("Streaming não implementado.")

    def _stream_chat(self, messages: List[ChatMessage], **kwargs: Any):
        raise NotImplementedError("Streaming não implementado.")

    def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        return self._complete(prompt, **kwargs)

    async def acomplete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        return await self._acomplete(prompt, **kwargs)

    def chat(self, messages: List[ChatMessage], **kwargs: Any) -> ChatResponse:
        return self._chat(messages, **kwargs)

    async def achat(self, messages: List[ChatMessage], **kwargs: Any) -> ChatResponse:
        return await self._achat(messages, **kwargs)

    def stream_complete(self, prompt: str, **kwargs: Any):
        return self._stream_complete(prompt, **kwargs)

    def stream_chat(self, messages: List[ChatMessage], **kwargs: Any):
        return self._stream_chat(messages, **kwargs)

class FallbackLLM(CustomLLM):
    """LLM que tenta um provedor primário e usa um fallback em caso de erro."""
    primary: Any
    fallback: Any
    fallback_count: int = 0
    max_fallbacks: int = 5

    def __init__(self, primary: Any, fallback: Any, **kwargs):
        super().__init__(primary=primary, fallback=fallback, **kwargs)

    @property
    def metadata(self) -> LLMMetadata:
        return self.primary.metadata

    def _complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        if self.fallback_count >= self.max_fallbacks:
            print(f"🔄 [LLM] Limite de falhas atingido ({self.fallback_count}/{self.max_fallbacks}). Usando fallback diretamente.")
            res = self.fallback.complete(prompt, **kwargs)
            if "model_name" not in res.additional_kwargs:
                res.additional_kwargs["model_name"] = f"ollama/{self.fallback.model}"
            return res

        try:
            res = self.primary.complete(prompt, **kwargs)
            # Garantir que o model_name esteja presente
            if "model_name" not in res.additional_kwargs:
                res.additional_kwargs["model_name"] = self.primary.metadata.model_name
            return res
        except Exception as e:
            self.fallback_count += 1
            print(f"⚠️ [LLM] Falha total no provedor primário ({self.fallback_count}/{self.max_fallbacks}), usando fallback (Ollama/Local)...")
            res = self.fallback.complete(prompt, **kwargs)
            # Adicionar model_name do fallback
            if "model_name" not in res.additional_kwargs:
                res.additional_kwargs["model_name"] = f"ollama/{self.fallback.model}"
            return res

    async def _acomplete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        if self.fallback_count >= self.max_fallbacks:
            print(f"🔄 [LLM] Limite de falhas atingido ({self.fallback_count}/{self.max_fallbacks}). Usando fallback (async) diretamente.")
            res = await self.fallback.acomplete(prompt, **kwargs)
            if "model_name" not in res.additional_kwargs:
                res.additional_kwargs["model_name"] = f"ollama/{self.fallback.model}"
            return res

        try:
            res = await self.primary.acomplete(prompt, **kwargs)
            if "model_name" not in res.additional_kwargs:
                res.additional_kwargs["model_name"] = self.primary.metadata.model_name
            return res
        except Exception as e:
            self.fallback_count += 1
            print(f"⚠️ [LLM] Falha total no provedor primário (async) ({self.fallback_count}/{self.max_fallbacks}), usando fallback...")
            res = await self.fallback.acomplete(prompt, **kwargs)
            if "model_name" not in res.additional_kwargs:
                res.additional_kwargs["model_name"] = f"ollama/{self.fallback.model}"
            return res

    def _chat(self, messages: List[ChatMessage], **kwargs: Any) -> ChatResponse:
        if self.fallback_count >= self.max_fallbacks:
            print(f"🔄 [LLM] Limite de falhas atingido ({self.fallback_count}/{self.max_fallbacks}). Usando fallback diretamente.")
            res = self.fallback.chat(messages, **kwargs)
            if "model_name" not in res.additional_kwargs:
                res.additional_kwargs["model_name"] = f"ollama/{self.fallback.model}"
            return res

        try:
            res = self.primary.chat(messages, **kwargs)
            if "model_name" not in res.additional_kwargs:
                res.additional_kwargs["model_name"] = self.primary.metadata.model_name
            return res
        except Exception as e:
            self.fallback_count += 1
            print(f"⚠️ [LLM] Falha total no provedor primário ({self.fallback_count}/{self.max_fallbacks}), usando fallback (Ollama/Local)...")
            res = self.fallback.chat(messages, **kwargs)
            if "model_name" not in res.additional_kwargs:
                res.additional_kwargs["model_name"] = f"ollama/{self.fallback.model}"
            return res

    async def _achat(self, messages: List[ChatMessage], **kwargs: Any) -> ChatResponse:
        if self.fallback_count >= self.max_fallbacks:
            print(f"🔄 [LLM] Limite de falhas atingido ({self.fallback_count}/{self.max_fallbacks}). Usando fallback (async) diretamente.")
            res = await self.fallback.achat(messages, **kwargs)
            if "model_name" not in res.additional_kwargs:
                res.additional_kwargs["model_name"] = f"ollama/{self.fallback.model}"
            return res

        try:
            res = await self.primary.achat(messages, **kwargs)
            if "model_name" not in res.additional_kwargs:
                res.additional_kwargs["model_name"] = self.primary.metadata.model_name
            return res
        except Exception as e:
            self.fallback_count += 1
            print(f"⚠️ [LLM] Falha total no provedor primário (async) ({self.fallback_count}/{self.max_fallbacks}), usando fallback...")
            res = await self.fallback.achat(messages, **kwargs)
            if "model_name" not in res.additional_kwargs:
                res.additional_kwargs["model_name"] = f"ollama/{self.fallback.model}"
            return res

    def _stream_complete(self, prompt: str, **kwargs: Any):
        if self.fallback_count >= self.max_fallbacks:
            return self.fallback.stream_complete(prompt, **kwargs)

        try:
            return self.primary.stream_complete(prompt, **kwargs)
        except Exception as e:
            self.fallback_count += 1
            logger.warning(f"Erro no streaming do LLM primário ({self.fallback_count}/{self.max_fallbacks}), usando fallback: {e}")
            return self.fallback.stream_complete(prompt, **kwargs)

    def _stream_chat(self, messages: List[ChatMessage], **kwargs: Any):
        if self.fallback_count >= self.max_fallbacks:
            return self.fallback.stream_chat(messages, **kwargs)

        try:
            return self.primary.stream_chat(messages, **kwargs)
        except Exception as e:
            self.fallback_count += 1
            logger.warning(f"Erro no streaming do LLM primário ({self.fallback_count}/{self.max_fallbacks}), usando fallback: {e}")
            return self.fallback.stream_chat(messages, **kwargs)

    def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        return self._complete(prompt, **kwargs)

    async def acomplete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        return await self._acomplete(prompt, **kwargs)

    def chat(self, messages: List[ChatMessage], **kwargs: Any) -> ChatResponse:
        return self._chat(messages, **kwargs)

    async def achat(self, messages: List[ChatMessage], **kwargs: Any) -> ChatResponse:
        return await self._achat(messages, **kwargs)

    def stream_complete(self, prompt: str, **kwargs: Any):
        return self._stream_complete(prompt, **kwargs)

    def stream_chat(self, messages: List[ChatMessage], **kwargs: Any):
        return self._stream_chat(messages, **kwargs)

class LLMClient:

    def __init__(self):
        self._llms = {}  # Cache de instâncias por provedor
        self._embedding = None
        self._initialized = False

    def _init_llm(self, provider: str):
        # Ollama sempre como fallback ou provedor principal direto
        ollama_llm = Ollama(
            model=Settings.LLM_MODEL,
            base_url=Settings.LLM_BASE_URL,
            request_timeout=Settings.LLM_TIMEOUT,
        )

        if provider == "ollama":
            print(f"🏠 [LLM] Inicializando Ollama (Modelo: {Settings.LLM_MODEL})")
            return ollama_llm
        
        if provider == "openrouter":
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
            print(f"🌐 [LLM] Inicializando OpenRouter (Multi-model Fallback) + Ollama")
            return FallbackLLM(primary=primary, fallback=ollama_llm)

        raise ValueError(f"LLM provider não suportado: {provider}")

    def _init_embedding(self):
        # Por enquanto mantemos embedding local no Ollama por performance/custo
        return OllamaEmbedding(
            model_name=Settings.EMBEDDING_MODEL,
            base_url=Settings.LLM_BASE_URL,
            embed_batch_size=42, # Otimização: maior lote para processamento
        )

    def get_llm(self, task: str = "general"):
        """
        Retorna a instância do LLM adequada para a tarefa solicitada.
        Tasks: 'enrichment', 'insights', 'rag', 'general'
        """
        # Mapeamento de task para o provider configurado
        provider_map = {
            "enrichment": Settings.ENRICHMENT_LLM_PROVIDER,
            "insights": Settings.INSIGHTS_LLM_PROVIDER,
            "rag": Settings.RAG_LLM_PROVIDER,
            "general": Settings.LLM_PROVIDER
        }
        
        provider = provider_map.get(task, Settings.LLM_PROVIDER)
        
        if provider not in self._llms:
            self._llms[provider] = self._init_llm(provider)
            
        return self._llms[provider]

    def get_embedding(self):
        if self._embedding is None:
            self._embedding = self._init_embedding()
        return self._embedding

    def _wait_for_ollama(self, timeout: int = 120):
        """Aguardar até que o serviço Ollama esteja pronto e o modelo carregado."""
        url = f"{Settings.LLM_BASE_URL}/api/tags"
        start_time = time.time()
        
        print(f"⏳ [Ollama] Aguardando prontidão em {Settings.LLM_BASE_URL} (timeout {timeout}s)...")
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    models_data = response.json().get('models', [])
                    models = [m['name'] for m in models_data]
                    
                    # Verificação flexível do nome do modelo (com ou sem tag)
                    target = Settings.LLM_MODEL.lower()
                    available = [m.lower() for m in models]
                    
                    model_found = any(target in m or m in target for m in available)
                    
                    if model_found:
                        print(f"✅ [Ollama] Serviço pronto e modelo '{Settings.LLM_MODEL}' disponível.")
                        
                        # Warm-up: Forçar carregamento na RAM
                        print(f"🔥 [Ollama] Realizando warm-up do modelo '{Settings.LLM_MODEL}'...")
                        try:
                            requests.post(
                                f"{Settings.LLM_BASE_URL}/api/generate",
                                json={"model": Settings.LLM_MODEL, "prompt": "hi", "stream": False},
                                timeout=Settings.LLM_TIMEOUT
                            )
                            print(f"✨ [Ollama] Warm-up concluído com sucesso.")
                        except Exception as e:
                            print(f"⚠️ [Ollama] Warm-up falhou (mas o serviço está up): {e}")
                            
                        return True
                    else:
                        # Se não achou o modelo principal, tenta ver se o embedding está lá pelo menos
                        embed_target = Settings.EMBEDDING_MODEL.lower()
                        if any(embed_target in m or m in embed_target for m in available):
                            print(f"⚠️ [Ollama] Modelo '{Settings.LLM_MODEL}' ainda não disponível, mas embedding '{Settings.EMBEDDING_MODEL}' pronto.")
                
            except Exception:
                # Silencioso enquanto tenta conectar
                pass
            
            time.sleep(5)
        
        print(f"❌ [Ollama] Timeout ao aguardar o serviço. A aplicação pode apresentar lentidão ou erros no fallback.")
        return False

    # Configura o llama index globalmente
    def initialize(self):
        if not self._initialized:
            # Aguardar Ollama se ele for necessário (como primário ou fallback)
            # Aumentamos o timeout para 120s para dar tempo do container subir e o pull terminar
            self._wait_for_ollama(timeout=120)
            
            LlamaSettings.llm = self.get_llm()
            LlamaSettings.embed_model = self.get_embedding()
            self._initialized = True

# Singleton global
llm_client = LLMClient()