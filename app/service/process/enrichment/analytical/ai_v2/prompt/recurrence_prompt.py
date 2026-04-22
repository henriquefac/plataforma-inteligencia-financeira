def build_recurrence_classification_prompt(description: str, values: list[str]) -> str:

    values_str = "\n- ".join(values)

    return f"""
Você é um classificador de transações financeiras.

Sua tarefa é classificar se uma transação aparenta ter natureza recorrente ou não.

RECORRÊNCIA = indica se há repetição ao longo do tempo (ex: mensal, anual, contrato contínuo)

VALORES POSSÍVEIS (escolha apenas um):
- {values_str}

REGRAS:
- escolha apenas UM valor da lista
- se não houver indicação clara, responda exatamente: desconhecido
- NÃO invente novos valores
- NÃO explique
- responda apenas uma palavra

EXEMPLOS:

Descrição: "Assinatura mensal de software"
Resposta: Recorrente

Descrição: "Pagamento único por serviço"
Resposta: Unico

Descrição: "Serviço técnico"
Resposta: desconhecido

DESCRIÇÃO:
{description}
"""