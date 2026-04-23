import functools
import hashlib
import time
import asyncio
from typing import Any, Dict, Optional, Callable, TypeVar

T = TypeVar("T")

class SimpleCache:
    """
    Cache simples em memória com TTL (Time To Live).
    Suporta funções síncronas e assíncronas.
    """
    def __init__(self):
        # Estrutura: {key: {"value": result, "expiry": timestamp}}
        self._cache: Dict[str, Dict[str, Any]] = {}

    def _make_key(self, func: Callable, args: tuple, kwargs: dict) -> str:
        # Tenta criar uma chave estável baseada nos argumentos
        # Para objetos complexos (como DataArtifact ou FilterParams), 
        # tentamos extrair identificadores únicos ou converter para dict.
        
        def serialize(obj):
            if hasattr(obj, "ingestion_id"):
                return obj.ingestion_id
            if hasattr(obj, "to_dict"):
                return obj.to_dict()
            if hasattr(obj, "to_service_dict"):
                return obj.to_service_dict()
            return str(obj)

        key_parts = [
            func.__module__,
            func.__name__,
            tuple(serialize(a) for a in args),
            {k: serialize(v) for k, v in kwargs.items()}
        ]
        key_str = str(key_parts)
        return hashlib.md5(key_str.encode()).hexdigest()

    def __call__(self, ttl: int = 300):
        """
        Decorador de cache.
        ttl: Tempo de vida em segundos (default 5 minutos).
        """
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            if asyncio.iscoroutinefunction(func):
                @functools.wraps(func)
                async def async_wrapper(*args, **kwargs):
                    key = self._make_key(func, args, kwargs)
                    now = time.time()
                    
                    if key in self._cache:
                        entry = self._cache[key]
                        if now < entry["expiry"]:
                            return entry["value"]
                    
                    result = await func(*args, **kwargs)
                    self._cache[key] = {
                        "value": result,
                        "expiry": now + ttl
                    }
                    return result
                return async_wrapper
            else:
                @functools.wraps(func)
                def sync_wrapper(*args, **kwargs):
                    key = self._make_key(func, args, kwargs)
                    now = time.time()
                    
                    if key in self._cache:
                        entry = self._cache[key]
                        if now < entry["expiry"]:
                            return entry["value"]
                    
                    result = func(*args, **kwargs)
                    self._cache[key] = {
                        "value": result,
                        "expiry": now + ttl
                    }
                    return result
                return sync_wrapper
        return decorator

    def clear(self):
        """Limpa todo o cache."""
        self._cache.clear()

# Instância global de cache
backend_cache = SimpleCache()
