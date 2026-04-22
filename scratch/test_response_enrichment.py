import os
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path para importar o app
sys.path.append(str(Path(__file__).parent.parent))

from app.core.llm.client import llm_client
from app.core.config import settingsInst as Settings

def test_response_enrichment():
    print("--- Testando Enriquecimento da Resposta com Nome do Modelo ---")
    Settings.LLM_PROVIDER = "openrouter"
    
    # Simula sucesso com o primeiro modelo
    Settings.OPENROUTER_FALLBACK_MODELS = [
        "meta-llama/llama-3.3-70b-instruct:free"
    ]
    
    llm = llm_client._init_llm()
    
    try:
        response = llm.complete("Teste rápido.")
        print(f"Modelo detectado na resposta: {response.additional_kwargs.get('model_name')}")
    except Exception as e:
        print(f"Erro: {e}")

    print("\n--- Testando Fallback para Ollama ---")
    # Força erro total no OpenRouter
    Settings.OPENROUTER_FALLBACK_MODELS = ["invalid/model"]
    llm = llm_client._init_llm()
    
    try:
        response = llm.complete("Teste fallback.")
        print(f"Modelo detectado na resposta (Ollama): {response.additional_kwargs.get('model_name')}")
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    test_response_enrichment()
