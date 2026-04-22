import os
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path para importar o app
sys.path.append(str(Path(__file__).parent.parent))

from app.core.llm.client import llm_client
from app.core.config import settingsInst as Settings

def test_multi_model_fallback():
    print("--- Testando Multi-Model Fallback no OpenRouter ---")
    Settings.LLM_PROVIDER = "openrouter"
    
    # Vamos colocar modelos inválidos primeiro e um válido no final (ou forçar erro em todos)
    Settings.OPENROUTER_FALLBACK_MODELS = [
        "invalid/model-1:free",
        "invalid/model-2:free",
        "meta-llama/llama-3.3-70b-instruct:free"
    ]
    
    llm = llm_client._init_llm()
    
    try:
        print("Chamando LLM (deve tentar 2 inválidos antes de conseguir o Llama)...")
        response = llm.complete("Olá!")
        print(f"Resposta final: {response.text}")
    except Exception as e:
        print(f"Erro no teste: {e}")

if __name__ == "__main__":
    test_multi_model_fallback()
