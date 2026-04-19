from . import schema_to_example
from app.service.process.enrichment.analytical.ai.schema.service_type_schema import ServiceTypeSchema

def build_service_type_discovery_prompt(descriptions: list[str]) -> str:

    desc_str = "\n- ".join(descriptions[:50])
    example = schema_to_example(ServiceTypeSchema)

    return f"""
Você é um analista financeiro especializado em categorização de transações.

Sua tarefa é identificar os tipos de serviço adquiridos nas transações.

DEFINIÇÃO:
"tipo_servico" = categoria geral do que foi comprado (produto ou serviço principal).

✔ Foque no núcleo da compra (substantivo principal)
✔ Ignore detalhes como marcas, adjetivos ou contexto secundário

EXEMPLOS VÁLIDOS:
- software
- assinatura
- licenca
- plano
- hospedagem
- consultoria

EXEMPLOS INVÁLIDOS:
- software_caro
- plano_premium
- assinatura_mensal_netflix

REGRAS:
- máximo 8 valores
- usar "_" ao invés de espaço
- usar apenas letras minúsculas
- nomes curtos (1 ou 2 palavras no máximo)
- não inventar termos irrelevantes
- evitar duplicidade semântica (ex: "software" e "sistema")
- retornar APENAS JSON válido

DESCRIÇÕES:
- {desc_str}

FORMATO:
{example}
"""


def build_service_type_classification_prompt(description: str, values: list[str]) -> str:

    values_str = "\n- ".join(values)

    return f"""
Você é um classificador de transações financeiras.

Sua tarefa é classificar a descrição em UM tipo de serviço.

DEFINIÇÃO:
"tipo_servico" = o principal item ou serviço adquirido.

VALORES POSSÍVEIS:
- {values_str}

REGRAS:
- escolha apenas UM valor da lista
- NÃO crie novos valores
- se não houver evidência clara na descrição, responda: desconhecido
- baseie-se apenas no texto fornecido
- responda APENAS com o valor (sem explicação)

EXEMPLOS:
Descrição: "pagamento mensal do sistema ERP"
Resposta: software

Descrição: "taxa bancária"
Resposta: desconhecido

DESCRIÇÃO:
{description}
"""