def build_service_type_prompt(description: str, values: list[str]) -> str:
    values_str = "\n- ".join(values)

    return f"""
Classifique o TIPO DE SERVIÇO da transação.

VALORES:
- {values_str}

REGRAS:
- Assinatura de plataforma → Assinatura
- Licença com prazo → Licenca
- Manutenção contínua → ServicoContinuo
- Customização/análise → ServicoPontual
- Mudança de plano → UpgradePlano

- escolha apenas um valor
- não explique
- se não souber, responda ServicoPontual

DESCRIÇÃO:
{description}

RESPOSTA:
"""