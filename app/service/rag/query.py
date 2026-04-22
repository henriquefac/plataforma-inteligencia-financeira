from app.core.llm import llm_client
from .indexer import RAGIndexer


SYSTEM_PROMPT = """Você é um assistente de análise financeira que responde perguntas
sobre transações de uma base de dados empresarial.

REGRAS:
- Responda sempre em português brasileiro
- Seja preciso e cite dados específicos quando possível
- Se não encontrar informação suficiente, diga claramente
- Formate valores monetários como R$ X.XXX,XX
- Cite os clientes e transações relevantes na resposta
"""


class RAGQueryEngine:
    """
    Motor de consultas em linguagem natural sobre transações 
    financeiras usando RAG (Retrieval-Augmented Generation).
    """

    def __init__(self):
        self.indexer = RAGIndexer()

    def query(self, ingestion_id: str, question: str) -> dict:
        """
        Executa uma consulta em linguagem natural sobre os dados 
        de uma ingestão específica.
        
        1. Carrega (ou constrói) o índice vetorial
        2. Cria query engine com contexto em português
        3. Executa a consulta
        4. Retorna resposta + fontes relevantes
        """
        # 1. Obter índice (lazy: constrói se não existir)
        index = self.indexer.get_or_build_index(ingestion_id)

        # 2. Criar query engine
        query_engine = index.as_query_engine(
            llm=llm_client.get_llm(),
            similarity_top_k=10,
            system_prompt=SYSTEM_PROMPT,
        )

        # 3. Executar consulta
        response = query_engine.query(question)

        # 4. Extrair fontes
        sources = []
        if response.source_nodes:
            for node in response.source_nodes:
                sources.append({
                    "texto": node.node.text[:300],
                    "score": round(float(node.score), 4) if node.score else None,
                    "metadata": node.node.metadata,
                })

        return {
            "ingestion_id": ingestion_id,
            "pergunta": question,
            "resposta": str(response),
            "fontes": sources,
            "total_fontes": len(sources),
        }
