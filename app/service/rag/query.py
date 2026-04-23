import logging
import pandas as pd
from typing import Any, List

from app.core.llm import llm_client
from app.core.cache import backend_cache
from app.domain.data_artifact import DataArtifact

logger = logging.getLogger(__name__)

# Palavras proibidas para o sandbox básico
FORBIDDEN = ["import", "__", "exec", "eval", "open", "os", "sys", "subprocess", "requests", "httpx"]

ANALYST_PROMPT = """
Você é um analista de dados especializado em extração de informações financeiras via Pandas.
Sua tarefa é gerar as expressões Python/Pandas necessárias para extrair os dados que respondam à pergunta do usuário.

REGRAS:
- Use apenas o DataFrame `df`
- Retorne APENAS as expressões, uma por linha.
- Não use explicações ou blocos de código.
- Gere o mínimo de queries necessárias para uma resposta completa.
- Apenas uma experessão por linha
- A querry pode procurar por padrões no nome do cliente, então use str.contains().
- A querry pode ter como objetivo procurar um registros específico ou mais de um.
- Se tiver que mostrar mais de uma coisa, faça uma querry para cada coisa.
- A querry pode ter como objetivo agrupar dados, então use groupby().
- A querry pode ter como objetivo ordenar dados, então use sort_values().
- A querry pode ter como objetivo limitar dados, então use head() ou tail().

COLUNAS DISPONÍVEIS:
- cliente (string): Nome do cliente
- valor (float): Valor bruto da transação
- status (string): Status da transação: pago, pendente, atrasado.
- data (datetime): Data prevista de pagamento da transação.
- is_pago (bool): Se a transação foi paga
- is_inadimplente (bool): Se o cliente está em atraso
- receita_real (float): O valor efetivamente pago.
- receita_potencial (float): O valor efetivamente pago + o esperado (pendente/atrasado).
- valor_medio_cliente (float): Ticket médio do cliente
- ano, mes, dia (int): Componentes temporais
- empresa, loja, startup (bool): Segmentação do cliente
- recorrencia (string): 'recorrencia' ou 'unico'
- frequencia (string): mensal, anual, sob demanda, nao aplicavel
- tipo_servico (string): assinatura, licenca, servico_continuo, servico_pontual, upgrade_plano

Exemplos de Saída:
df[df["is_inadimplente"] == True]["valor"].sum()
df.groupby("cliente")["valor"].mean().sort_values(ascending=False).head(5)
"""

RESPONSE_PROMPT = """
Você é um consultor financeiro inteligente. Abaixo está a pergunta de um cliente e os dados reais extraídos do banco de dados.
Sua tarefa é responder à pergunta de forma clara, profissional e detalhada, usando APENAS os dados fornecidos.

REGRAS:
- Responda em Português Brasileiro.
- Formate valores monetários (R$ X.XXX,XX).
- Se os dados estiverem vazios ou não permitirem responder, seja honesto.
- Adicione um breve insight se os dados mostrarem algo relevante.

PERGUNTA: {question}

DADOS EXTRAÍDOS:
{context}

RESPOSTA FINAL:
"""

def is_safe(code: str) -> bool:
    """Verifica se o código contém palavras proibidas."""
    return not any(word in code for word in FORBIDDEN)

def execute_llm_code(df: pd.DataFrame, code: str) -> str:
    """Executa o código e retorna uma string formatada 'query -> resultado'."""
    safe_globals = {"__builtins__": {}, "pd": pd, "df": df}
    
    try:
        if not is_safe(code):
            return f"{code} -> BLOQUEADO POR SEGURANÇA"
            
        result = eval(code, safe_globals, {"df": df})
        
        # Formatação amigável para o prompt de resposta
        if isinstance(result, (pd.DataFrame, pd.Series)):
            return f"{code} -> \n{result.to_string()}"
        return f"{code} -> {result}"
        
    except Exception as e:
        return f"{code} -> ERRO: {str(e)}"

class RAGQueryEngine:
    """
    Motor de consultas que atua como um agente:
    1. Analista: Gera queries pandas para extrair fatos.
    2. Executor: Roda as queries no DataFrame.
    3. Consultor: Gera a resposta final baseada nos fatos extraídos.
    """

    @backend_cache(ttl=3600)
    async def query(self, ingestion_id: str, question: str) -> dict:
        # 1. Carregar Dados
        artifact = DataArtifact.load(ingestion_id)
        df = artifact.load_enriched()

        llm = llm_client.get_llm(task="rag")

        # 2. ETAPA 1: Gerar queries (Analista)
        analyst_query = f"{ANALYST_PROMPT}\n\nPergunta: {question}\nQueries:"
        analyst_res = await llm.acomplete(analyst_query)
        
        # Limpar e extrair queries por linha
        raw_queries = analyst_res.text.strip().split("\n")
        queries = [q.strip().replace("```python", "").replace("```", "") for q in raw_queries if q.strip()]
        
        logger.info(f"Queries geradas para '{question}': {queries}")

        # 3. ETAPA 2: Executar queries
        context_parts = []
        for query_code in queries:
            res_str = execute_llm_code(df, query_code)
            context_parts.append(res_str)
        
        context_data = "\n\n".join(context_parts)

        # 4. ETAPA 3: Gerar Resposta Final (Consultor)
        final_prompt = RESPONSE_PROMPT.format(
            question=question,
            context=context_data
        )
        
        final_res = await llm.acomplete(final_prompt)
        resposta_final = final_res.text.strip()

        return {
            "ingestion_id": ingestion_id,
            "pergunta": question,
            "queries_executadas": queries,
            "dados_brutos": context_data,
            "resposta": resposta_final,
            "status": "success"
        }
