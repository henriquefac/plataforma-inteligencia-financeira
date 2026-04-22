import json


def build_insights_prompt(context: dict) -> str:
    """
    Prompt para o LLM gerar insights acionáveis a partir 
    da camada determinística (métricas básicas e avançadas).
    """
    context_json = json.dumps(context, indent=2, ensure_ascii=False)

    return f"""Você é um analista financeiro sênior especializado em inteligência de negócios.

Analise os dados da CAMADA DETERMINÍSTICA abaixo e gere insights estratégicos e acionáveis.
Os dados contêm métricas básicas e avançadas (Pareto, conversão, volatilidade, consistência, contribuição e receita ajustada).

DADOS DA CAMADA DETERMINÍSTICA:
{context_json}

TAREFAS:
1. Analise a eficiência de receita (conversão) e identifique onde estão os maiores gaps de faturamento.
2. Avalie a concentração de receita (Pareto) e o risco de dependência de grandes clientes.
3. Observe a volatilidade e consistência do faturamento mensal para avaliar a previsibilidade do caixa.
4. Analise a receita ajustada pelo risco de inadimplência para uma visão real do faturamento futuro.
5. Identifique os 3-5 insights mais críticos e estratégicos para o negócio.

PARA CADA INSIGHT, INDIQUE:
- Título: Nome curto e impactante.
- Observacao: O fato matemático observado.
- Impacto: Por que isso é relevante (financeiro, operacional, risco).
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
Foque em distorções de conversão, picos de volatilidade, quebras de consistência e riscos de concentração.

DADOS DA CAMADA DETERMINÍSTICA:
{context_json}

TAREFAS:
1. Detecte anomalias de valor e comportamento (ex: clientes com queda súbita de contribuição ou ticket médio anômalo).
2. Identifique riscos de concentração excessiva (Pareto) que podem fragilizar a operação.
3. Analise o impacto da inadimplência e a disparidade entre receita real e ajustada.
4. Identifique padrões de comportamento por segmento ou recorrência que divergem da média.

FORMATO DE RESPOSTA (JSON):
{{
    "anomalias": [
        {{
            "tipo": "outlier|concentracao|inadimplencia|conversao|queda_contribuicao|volatilidade",
            "descricao": "string",
            "evidencia": "números que comprovam",
            "risco": "alto|medio|baixo",
            "recomendacao": "string"
        }}
    ],
    "padroes": [
        {{
            "tipo": "comportamento|segmentacao|correlacao|recorrencia",
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

