import logging
import pandas as pd
from typing import Any

from app.core.llm import llm_client
from app.core.cache import backend_cache
from app.domain.data_artifact import DataArtifact

logger = logging.getLogger(__name__)

# Palavras proibidas para o sandbox básico
FORBIDDEN = ["import", "__", "exec", "eval", "open", "os", "sys", "subprocess", "requests", "httpx"]

SYSTEM_PROMPT = """
Você é um assistente de análise de dados especializado em gerar expressões Python/Pandas para consultar transações financeiras.
Gere APENAS uma expressão Python válida usando o DataFrame `df`.

REGRAS:
- Use apenas o DataFrame `df`
- Não use import, não use funções externas, não use print
- Apenas uma expressão (sem múltiplas linhas)
- Retorne SOMENTE o código (sem explicações, sem blocos de código ```python)
- Datas: Use pd.to_datetime se precisar filtrar por datas específicas.
- Strings: Use .str.contains(..., case=False) para buscas parciais.

COLUNAS DISPONÍVEIS:
- cliente (string): Nome do cliente
- valor (float): Valor bruto da transação
- status (string): Status da transação: pago, pendente, atrasado.
- data (datetime): Data prevista de pagamento da transação.
- is_pago (bool): Se a transação foi paga
- is_inadimplente (bool): Se o cliente está em atraso
- receita_real (float): Valor efetivamente recebido
- valor_medio_cliente (float): Ticket médio do cliente
- receita_potencial (float): O valor efetivamente pago + o que era esperado receber (status = 'pendente' ou 'atrasado').
- receita_real (float): O valor efetivamente pago.
- ano, mes, dia (int): Componentes temporais
- empresa (bool): Se o cliente é empresa
- loja (bool): Se o cliente é loja
- startup (bool): Se o cliente é startup
- recorrencia (string): Se o foi observado na descrição da receita recorrencia (provavelmente acontece multiplas vezes) ou unico (acontece apenas uma vez)
- frequencia (string): Se o foi observado na descrição da receita frequencia, mensal, anual, sob demanda, nao aplicavel
- tipo_servico (string): Se o foi observado na descrição do tipo de servico, assinatura, licenca, servico_continuo, servico_pontual, upgrade_plano

Exemplos:
Pergunta: Qual a receita total dos inadimplentes?
Resposta: df[df["is_inadimplente"] == True]["valor"].sum()

Pergunta: Ticket médio por cliente?
Resposta: df.groupby("cliente")["valor"].mean()

Pergunta: Transações do cliente João em 2023?
Resposta: df[(df["cliente"].str.contains("João", case=False)) & (df["ano"] == 2023)]
"""

def is_safe(code: str) -> bool:
    """Verifica se o código contém palavras proibidas."""
    return not any(word in code for word in FORBIDDEN)

def execute_llm_code(df: pd.DataFrame, code: str) -> Any:
    """Executa o código gerado pelo LLM em um ambiente restrito."""
    # Ambiente restrito
    safe_globals = {
        "__builtins__": {},
        "pd": pd,
        "df": df
    }

    # Adicionar funções seguras do pandas se necessário
    # Aqui df já está no local, e pd no global

    try:
        # Avalia a expressão
        # Nota: eval() em Python retorna o resultado da expressão
        result = eval(code, safe_globals, {"df": df})
        return result
    except Exception as e:
        logger.error(f"Erro ao executar código: {e} | Código: {code}")
        raise ValueError(f"Erro ao processar consulta nos dados: {e}")

class RAGQueryEngine:
    """
    Motor de consultas que interpreta perguntas em linguagem natural
    e as converte em expressões Pandas para execução direta sobre os dados.
    """

    @backend_cache(ttl=3600)
    async def query(self, ingestion_id: str, question: str) -> dict:
        """
        Interpreta a pergunta, gera código pandas e executa no DataFrame.
        """
        # 1. Carregar os dados enriquecidos
        artifact = DataArtifact.load(ingestion_id)
        df = artifact.load_enriched()

        # 2. Gerar o código via LLM
        prompt = f"{SYSTEM_PROMPT}\n\nPergunta: {question}\nResposta:"
        
        llm = llm_client.get_llm(task="rag")
        response = await llm.acomplete(prompt)
        code = response.text.strip().replace("```python", "").replace("```", "").strip()

        logger.info(f"LLM Generated Code for question '{question}': {code}")

        # 3. Segurança e Execução
        if not is_safe(code):
            logger.warning(f"Código potencialmente perigoso bloqueado: {code}")
            raise ValueError("A consulta gerada foi bloqueada por motivos de segurança.")

        try:
            result = execute_llm_code(df, code)
            
            # Formatar o resultado
            if isinstance(result, (int, float)):
                # Se for número, formata como string
                formatted_result = f"{result:.2f}"
            elif isinstance(result, pd.Series):
                formatted_result = result.to_dict()
            elif isinstance(result, pd.DataFrame):
                formatted_result = result.head(20).to_dict(orient="records")
            else:
                formatted_result = str(result)

            return {
                "ingestion_id": ingestion_id,
                "pergunta": question,
                "codigo_gerado": code,
                "resposta": formatted_result,
                "status": "success"
            }

        except Exception as e:
            return {
                "ingestion_id": ingestion_id,
                "pergunta": question,
                "codigo_gerado": code,
                "erro": str(e),
                "status": "error"
            }
