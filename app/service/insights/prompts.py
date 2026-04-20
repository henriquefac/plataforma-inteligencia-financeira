import json


def build_insights_prompt(stats_summary: dict) -> str:
    """
    Prompt para o LLM gerar insights acionáveis a partir 
    de um resumo estatístico dos dados financeiros.
    """
    stats_json = json.dumps(stats_summary, indent=2, ensure_ascii=False)

    return f"""Você é um analista financeiro sênior.

Analise os dados estatísticos abaixo de uma base de transações financeiras e gere insights acionáveis.

DADOS ESTATÍSTICOS:
{stats_json}

TAREFAS:
1. Identifique os 3-5 insights mais relevantes
2. Para cada insight, indique:
   - O que foi observado (fato)
   - Por que é relevante (impacto)
   - O que pode ser feito (ação recomendada)

FORMATO DE RESPOSTA (JSON):
{{
    "insights": [
        {{
            "titulo": "título curto do insight",
            "observacao": "o que foi observado nos dados",
            "impacto": "por que isso é relevante",
            "acao": "ação recomendada",
            "severidade": "alta|media|baixa"
        }}
    ]
}}

REGRAS:
- Responda APENAS o JSON, sem texto adicional
- Use português brasileiro
- Seja específico com números dos dados
- Foque em insights acionáveis, não óbvios
"""


def build_anomaly_prompt(stats_summary: dict) -> str:
    """
    Prompt para o LLM identificar padrões e anomalias nos dados.
    """
    stats_json = json.dumps(stats_summary, indent=2, ensure_ascii=False)

    return f"""Você é um especialista em detecção de anomalias financeiras.

Analise os dados estatísticos abaixo e identifique padrões anômalos, riscos e oportunidades.

DADOS ESTATÍSTICOS:
{stats_json}

TAREFAS:
1. Identifique anomalias nos valores (outliers, concentrações)
2. Detecte padrões temporais (sazonalidade, tendências)
3. Avalie concentração de risco por cliente
4. Identifique padrões de inadimplência

FORMATO DE RESPOSTA (JSON):
{{
    "anomalias": [
        {{
            "tipo": "outlier|sazonalidade|concentracao|tendencia|inadimplencia",
            "descricao": "descrição detalhada da anomalia",
            "evidencia": "dados que sustentam a observação",
            "risco": "alto|medio|baixo",
            "recomendacao": "ação sugerida"
        }}
    ],
    "padroes": [
        {{
            "tipo": "sazonalidade|tendencia|correlacao",
            "descricao": "descrição do padrão identificado",
            "evidencia": "dados que sustentam"
        }}
    ]
}}

REGRAS:
- Responda APENAS o JSON, sem texto adicional
- Use português brasileiro
- Seja específico com números
- Se não houver anomalias claras, retorne listas vazias
"""
