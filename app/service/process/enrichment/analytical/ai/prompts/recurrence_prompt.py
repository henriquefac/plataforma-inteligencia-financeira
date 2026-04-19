from . import schema_to_example
from app.service.process.enrichment.analytical.ai.schema.recurrence_schema import RecurrenceSchema

def build_recurrence_discovery_prompt(descriptions: list[str]) -> str:

    desc_str = ",\n - ".join(descriptions[:50])
    example = schema_to_example(RecurrenceSchema)
    
    return f"""
Você é um analista financeiro.

Sua tarefa é identificar tipos de recorrência em transações.

Recorrência = presença de periodicidade.

Exemplos:
- mensal
- anual
- semanal
- unico

REGRAS:
- máximo 6 valores
- usar "_" ao invés de espaço
- valores curtos
- não inventar termos irrelevantes
- retornar APENAS JSON válido

DESCRIÇÕES:
- {desc_str}

FORMATO:
{example}
"""


def build_recurrence_classification_prompt(description: str, values: list[str]) -> str:
    
    values_str = "\n - ".join(values)

    return f"""
Você é um classificador de transações financeiras.

Sua tarefa é classificar a recorrência da transação.

RECORRÊNCIA = indica se há periodicidade (mensal, anual, etc)

VALORES POSSÍVEIS:
- {values_str}

REGRAS:
- escolha apenas UM valor da lista
- se não houver indicação clara, responda "desconhecido"
- não invente novos valores
- responda apenas o valor (sem explicação)

DESCRIÇÃO:
{description}
"""