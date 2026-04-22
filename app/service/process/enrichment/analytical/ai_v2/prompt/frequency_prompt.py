def build_frequency_classification_prompt(description: str, values: list[str]) -> str:

    values_str = "\n- ".join(values)

    return f"""
Você é um classificador de transações financeiras.

Sua tarefa é identificar a FREQUÊNCIA de uma transação recorrente.

FREQUÊNCIA = intervalo de repetição (ex: mensal, anual)

VALORES POSSÍVEIS (escolha apenas um):
- {values_str}

REGRAS:
- escolha apenas UM valor da lista
- se não houver indicação clara, responda exatamente: Nao aplicavel
- NÃO invente novos valores
- NÃO explique
- responda apenas uma palavra ou expressão curta

EXEMPLOS:

Descrição: "Assinatura mensal de software"
Resposta: Mensal

Descrição: "Licença anual corporativa"
Resposta: Anual

Descrição: "Contrato recorrente de serviço"
Resposta: Nao aplicavel

#PRECISA POSSUIR ALGUM INDÍCIO DE FREQUÊNCIA

---

DESCRIÇÃO:
{description}

RESPOSTA:
"""