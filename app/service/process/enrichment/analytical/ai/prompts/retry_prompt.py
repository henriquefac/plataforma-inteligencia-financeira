def generate_retry_prompt(last_error, last_output, prompt_base):
    return f"""
Você gerou uma resposta inválida.

ERRO:
{last_error}

RESPOSTA ANTERIOR:
{last_output}

Corrija mantendo o formato JSON.

{prompt_base}
"""