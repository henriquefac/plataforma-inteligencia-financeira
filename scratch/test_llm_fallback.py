import os
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path para importar o app
sys.path.append(str(Path(__file__).parent.parent))

from app.core.llm.client import llm_client
from app.core.config import settingsInst as Settings
from llama_index.core.llms import ChatMessage

def test_openrouter():
    print("--- Testando OpenRouter ---")
    Settings.LLM_PROVIDER = "openrouter"
    
    llm = llm_client._init_llm()
    print(f"LLM instanciado: {type(llm)}")
    
    try:
        response = llm.complete("Olá, quem é você?")
        print(f"Resposta: {response.text}")
    except Exception as e:
        print(f"Erro ao chamar OpenRouter: {e}")

def test_fallback():
    print("\n--- Testando Fallback (Forçando erro no OpenRouter) ---")
    Settings.LLM_PROVIDER = "openrouter"
    # Salva a chave original
    original_key = Settings.OPENROUTER_API_KEY
    # Coloca uma chave inválida para forçar erro
    Settings.OPENROUTER_API_KEY = "sk-invalid-key"
    
    llm = llm_client._init_llm()
    
    try:
        print("Chamando LLM (deve falhar no OpenRouter e ir para Ollama)...")
        response = llm.complete("Qual o sentido da vida?")
        print(f"Resposta (via fallback?): {response.text}")
    except Exception as e:
        print(f"Erro total: {e}")
    finally:
        # Restaura a chave
        Settings.OPENROUTER_API_KEY = original_key

if __name__ == "__main__":
    # Verifica se a chave está carregada
    print(f"Chave OpenRouter configurada: {'Sim' if Settings.OPENROUTER_API_KEY else 'Não'}")
    
    test_openrouter()
    test_fallback()
