import asyncio
import json
import logging

# Configura logging para ver os warnings de retry
logging.basicConfig(level=logging.INFO)

# Importações locais simuladas ou reais
import sys
import os
sys.path.append("/home/henri/Documents/project/vicio_vaga/application/backend")

from app.service.insights.insights import InsightsService
from app.service.insights.models import InsightResponse, AnomalyResponse

async def test_validation_logic():
    service = InsightsService()
    
    # 1. Teste: Resposta válida com campos extras (Keywords novos)
    raw_data = {
        "insights": [
            {
                "titulo": "Insight 1",
                "observacao": "Fato 1",
                "impacto": "Impacto 1",
                "acao": "Acao 1",
                "severidade": "alta",
                "keyword_novo": "valor extra que deve ser removido"
            }
        ],
        "metadados_aleatorios": "deve sumir"
    }
    
    sanitized = await service._validate_and_sanitize(raw_data, InsightResponse)
    print("\n--- Teste 1: Keywords novos ---")
    print(f"Original keys: {raw_data.keys()}")
    print(f"Sanitized keys: {sanitized.keys()}")
    print(f"Insight keys: {sanitized['insights'][0].keys()}")
    assert "metadados_aleatorios" not in sanitized
    assert "keyword_novo" not in sanitized["insights"][0]
    
    # 2. Teste: Extração de JSON de texto sujo
    dirty_text = "Aqui está o seu JSON: ```json\n" + json.dumps(raw_data) + "\n```\nEspero que ajude!"
    parsed = service._parse_llm_json(dirty_text)
    print("\n--- Teste 2: Extração de JSON sujo ---")
    assert parsed["insights"][0]["titulo"] == "Insight 1"
    print("Sucesso na extração!")

    # 3. Teste: Resposta malformada (deve lançar erro para gatilhar retry)
    bad_text = "Isso não é um JSON { incompleto"
    print("\n--- Teste 3: JSON malformado ---")
    try:
        service._parse_llm_json(bad_text)
    except ValueError as e:
        print(f"Erro esperado capturado: {e}")

if __name__ == "__main__":
    asyncio.run(test_validation_logic())
