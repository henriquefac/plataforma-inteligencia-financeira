import logging
import asyncio
from llama_index.core.schema import TextNode

from app.core.llm import llm_client
from app.domain.data_artifact import DataArtifact
from app.core.chromadb.db import chroma_db

logger = logging.getLogger(__name__)

def build_embedding_text(row):
    return f"""
Descrição: {row.get('descricao', 'N/A')}
Cliente: {row.get('cliente', 'N/A')}
Tipo de serviço: {row.get('tipo_servico', 'N/A')}
Recorrência: {row.get('recorrencia', 'N/A')}
Status: {"inadimplente" if row.get('is_inadimplente') else row.get('status', 'N/A')}
Valor: {row.get('receita_real', 0)}
"""

class EmbeddingService:
    def __init__(self):
        # O modelo de embedding é configurado globalmente no LlamaIndex pelo llm_client
        self.embed_model = llm_client.get_embedding()

    async def generate_and_store_embeddings(self, ingestion_id: str):
        """
        Orquestra a geração de nodes e indexação no ChromaDB de forma assíncrona.
        """
        logger.info(f"🚀 [Async] Iniciando processamento de embeddings para a ingestão: {ingestion_id}")
        
        try:
            # 1. Carregar o artefato e os dados enriquecidos (I/O Síncrono, mas rápido)
            artifact = DataArtifact.load(ingestion_id)
            df = artifact.load_enriched()
            
            # 2. Criar Nodes do LlamaIndex (Otimizado: to_dict é mais rápido que iterrows)
            records = df.to_dict('records')
            nodes = [
                TextNode(
                    text=build_embedding_text(row),
                    metadata={
                        "ingestion_id": ingestion_id,
                        "id": str(row.get("id", "N/A")),
                        "cliente": str(row.get("cliente", "N/A")),
                        "status": str(row.get("status", "N/A")),
                        "setor": str(row.get("setor", "Geral"))
                    }
                )
                for row in records
            ]
            
            # 3. Indexar no ChromaDB via cliente unificado
            # Rodamos em thread separada para não bloquear o event loop da API
            logger.info(f"📦 [Async] Enviando {len(nodes)} nodes para indexação (Ollama/Chroma)...")
            await asyncio.to_thread(chroma_db.create_index_from_nodes, nodes)
            
            return {
                "ingestion_id": ingestion_id,
                "count": len(nodes),
                "status": "success",
                "storage": "chromadb"
            }
            
        except Exception as e:
            logger.error(f"❌ [Async] Erro ao gerar/armazenar embeddings: {e}")
            return {
                "ingestion_id": ingestion_id,
                "status": "error",
                "error": str(e)
            }