import json


def build_insights_prompt(context: dict) -> str:
    """
    Prompt para o LLM gerar insights acionáveis a partir 
    da camada determinística (métricas básicas e avançadas).
    """
    context_json = json.dumps(context, indent=2, ensure_ascii=False)

    return f"""Você é um analista financeiro sênior especializado em inteligência de negócios.

Analise os dados da CAMADA DETERMINÍSTICA abaixo e gere insights estratégicos e acionáveis.
Os dados contêm métricas básicas (volume, totais) e avançadas (Pareto, conversão, contribuição, crescimento).

DADOS DA CAMADA DETERMINÍSTICA:
{context_json}

TAREFAS:
1. Analise a eficiência de receita e identifique onde estão as maiores perdas.
2. Avalie a concentração de receita (Pareto) e o risco associado aos principais clientes.
3. Observe tendências de crescimento ou queda na contribuição de clientes e segmentos.
4. Identifique os 3-5 insights mais críticos para a saúde financeira do negócio.

PARA CADA INSIGHT, INDIQUE:
- Título: Nome curto e impactante.
- Observação: O fato matemático observado.
- Impacto: Por que isso é relevante para o negócio (financeiro, operacional, risco).
- Ação: Recomendação concreta do que fazer.
- Severidade: Alta, Média ou Baixa.

FORMATO DE RESPOSTA (JSON):
{{
    "insights": [
        {{
            "titulo": "string",
            "observacao": "string",
            "impacto": "string",
            "acao": "string",
            "severidade": "alta|media|baixa"
        }}
    ]
}}

REGRAS:
- Responda APENAS o JSON.
- Use português brasileiro.
- Seja específico com os números fornecidos.
- Foque em insights estratégicos, evite o óbvio.
"""


def build_anomaly_prompt(context: dict) -> str:
    """
    Prompt para o LLM identificar padrões e anomalias nos dados.
    """
    context_json = json.dumps(context, indent=2, ensure_ascii=False)

    return f"""Você é um especialista em detecção de anomalias e gestão de risco financeiro.

Analise os fatos matemáticos abaixo para identificar padrões anômalos, riscos críticos e oportunidades ocultas.

DADOS DA CAMADA DETERMINÍSTICA:
{context_json}

TAREFAS:
1. Detecte anomalias de valor e comportamento (ex: clientes com queda súbita de contribuição).
2. Identifique riscos de concentração excessiva ou dependência de poucos clientes/segmentos.
3. Analise o risco de inadimplência ponderado por valor em diferentes segmentos.
4. Identifique distorções na taxa de conversão de receita.

FORMATO DE RESPOSTA (JSON):
{{
    "anomalias": [
        {{
            "tipo": "outlier|concentracao|inadimplencia|conversao|queda_contribuicao",
            "descricao": "string",
            "evidencia": "números que comprovam",
            "risco": "alto|medio|baixo",
            "recomendacao": "string"
        }}
    ],
    "padroes": [
        {{
            "tipo": "comportamento|segmentacao|correlacao",
            "descricao": "string",
            "evidencia": "string"
        }}
    ]
}}

REGRAS:
- Responda APENAS o JSON.
- Use português brasileiro.
- Seja técnico e preciso.
- Se não houver anomalias claras, retorne listas vazias.
"""

