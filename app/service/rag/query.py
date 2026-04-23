import logging
from typing import List, Optional
import pandas as pd

from llama_index.core import get_response_synthesizer, ChatPromptTemplate
from llama_index.core.llms import ChatMessage
from llama_index.core.vector_stores import MetadataFilters, ExactMatchFilter
from llama_index.core.schema import NodeWithScore

from app.core.llm import llm_client
from app.core.cache import backend_cache
from app.core.chromadb.db import chroma_db
from app.domain.data_artifact import DataArtifact
from app.service.metrics.metrics import METRICS_REGISTRY

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Você é um assistente de análise financeira que responde perguntas
sobre transações de uma base de dados empresarial.

REGRAS:
- Responda sempre em português brasileiro
- Seja preciso e cite dados específicos quando possível
- Se não encontrar informação suficiente, diga claramente
- Formate valores monetários como R$ X.XXX,XX
- Cite os clientes e transações relevantes na resposta
- Use as métricas ROBUSTAS fornecidas abaixo para fundamentar sua resposta. Elas foram calculadas 
  diretamente dos registros originais que coincidem com a sua busca.
"""


class RAGQueryEngine:
    """
    Motor de consultas em linguagem natural sobre transações 
    financeiras usando RAG. As métricas são calculadas recuperando os registros 
    originais do DataArtifact para maior precisão.
    """

    def __init__(self):
        pass

    def _calculate_robust_metrics(self, ingestion_id: str, retrieved_ids: List[str]) -> str:
        """
        Recupera os registros originais do DataArtifact e calcula métricas completas.
        """
        try:
            # 1. Carregar DataFrame original enriquecido
            artifact = DataArtifact.load(ingestion_id)
            df_full = artifact.load_enriched()
            
            # 2. Filtrar pelos IDs recuperados na busca vetorial
            # Convertemos para string para garantir match com metadados do Chroma
            df_subset = df_full[df_full['id'].astype(str).isin(retrieved_ids)]
            
            if df_subset.empty:
                return "Nenhuma métrica robusta pôde ser calculada (registros não encontrados no dataframe)."

            # 3. Calcular métricas usando o registro oficial (METRICS_REGISTRY)
            results = {}
            for metric in METRICS_REGISTRY:
                if metric.verify_columns_required(df_subset):
                    results[metric.name] = metric.calculate(df_subset)

            # 4. Formatar resumo para o prompt
            summary = [
                "### Métricas Robustas dos Registros Selecionados:",
                f"- **Total de Registros Analisados**: {len(df_subset)}",
                f"- **Receita Total**: R$ {results.get('receita_total', 0):,.2f}",
                f"- **Receita Real (Paga)**: R$ {results.get('receita_real', 0):,.2f}",
                f"- **Receita Inadimplente**: R$ {results.get('receita_inadimplente', 0):,.2f}",
                f"- **Ticket Médio**: R$ {results.get('ticket_medio', 0):,.2f}",
                f"- **Taxa de Inadimplência**: {results.get('taxa_inadimplencia', 0):.2f}%",
            ]
            
            # Adicionar contagens de status e clientes se disponíveis no subset
            if 'status' in df_subset.columns:
                status_dist = df_subset['status'].value_counts().to_dict()
                summary.append(f"- **Distribuição de Status**: {status_dist}")
            
            if 'cliente' in df_subset.columns:
                clientes_unicos = df_subset['cliente'].nunique()
                summary.append(f"- **Clientes Únicos**: {clientes_unicos}")

            return "\n".join(summary)

        except Exception as e:
            logger.error(f"Erro ao calcular métricas robustas: {e}")
            return f"Erro ao processar métricas oficiais: {str(e)}"

    @backend_cache(ttl=3600)
    async def query(self, ingestion_id: str, question: str) -> dict:
        """
        Executa consulta RAG com métricas robustas extraídas do DataArtifact.
        """
        logger.info(f"🔍 Consulta RAG Robusta: {ingestion_id}")

        # 1. Obter índice e configurar filtros
        index = chroma_db.get_index()
        filters = MetadataFilters(filters=[
            ExactMatchFilter(key="ingestion_id", value=ingestion_id)
        ])

        # 2. Recuperar nodes
        retriever = index.as_retriever(similarity_top_k=15, filters=filters)
        nodes = await retriever.aretrieve(question)

        if not nodes:
            return {
                "ingestion_id": ingestion_id,
                "pergunta": question,
                "resposta": "Não foram encontrados registros para esta consulta.",
                "fontes": [],
                "total_fontes": 0
            }

        # 3. Extrair IDs e calcular métricas ROBUSTAS via DataArtifact
        retrieved_ids = [str(n.node.metadata.get("id")) for n in nodes if "id" in n.node.metadata]
        metrics_context = self._calculate_robust_metrics(ingestion_id, retrieved_ids)
        
        # 4. Sintetizar resposta
        full_system_prompt = f"{SYSTEM_PROMPT}\n\n{metrics_context}"
        
        # get_response_synthesizer não aceita system_prompt. Usamos templates para isso.
        qa_msgs = [
            ChatMessage(role="system", content=full_system_prompt),
            ChatMessage(
                role="user", 
                content=(
                    "Informações de contexto:\n"
                    "---------------------\n"
                    "{context_str}\n"
                    "---------------------\n"
                    "Pergunta: {query_str}\n"
                    "Resposta: "
                )
            ),
        ]
        text_qa_template = ChatPromptTemplate(qa_msgs)

        refine_msgs = [
            ChatMessage(role="system", content=full_system_prompt),
            ChatMessage(
                role="user", 
                content=(
                    "A pergunta original é: {query_str}\n"
                    "Já temos uma resposta parcial: {existing_answer}\n"
                    "Temos a oportunidade de refinar a resposta existente "
                    "(somente se necessário) com mais contexto abaixo.\n"
                    "------------\n"
                    "{context_msg}\n"
                    "------------\n"
                    "Dada a nova informação, refine a resposta original para melhor responder à pergunta. "
                    "Se o contexto não for útil, retorne a resposta original.\n"
                    "Resposta Refinada: "
                )
            ),
        ]
        refine_template = ChatPromptTemplate(refine_msgs)
        
        synthesizer = get_response_synthesizer(
            llm=llm_client.get_llm(task="rag"),
            text_qa_template=text_qa_template,
            refine_template=refine_template,
            use_async=True
        )
        
        response = await synthesizer.asynthesize(question, nodes)

        # 5. Fontes
        sources = []
        for node in nodes:
            sources.append({
                "texto": node.node.text[:400],
                "score": round(float(node.score), 4) if node.score else None,
                "metadata": node.node.metadata,
            })

        return {
            "ingestion_id": ingestion_id,
            "pergunta": question,
            "resposta": str(response),
            "fontes": sources,
            "total_fontes": len(sources),
            "metricas_robustas": metrics_context
        }
