import chromadb
from typing import List, Optional
import logging

from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.core.schema import TextNode

from app.core.config import settingsInst
from app.core.llm import llm_client

logger = logging.getLogger(__name__)

class ChromaDB:
    """
    Cliente unificado para o ChromaDB, gerenciando a conexão, 
    coleção e integração com LlamaIndex.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChromaDB, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        try:
            logger.info(f"🔌 Conectando ao ChromaDB em {settingsInst.CHROMA_HOST}:{settingsInst.CHROMA_PORT}...")
            self.client = chromadb.HttpClient(
                host=settingsInst.CHROMA_HOST, 
                port=settingsInst.CHROMA_PORT
            )
            
            # Garante a existência da coleção
            self.collection = self.client.get_or_create_collection(
                name=settingsInst.CHROMA_COLLECTION_NAME
            )
            
            # Configuração do Vector Store e Contextos do LlamaIndex
            self.vector_store = ChromaVectorStore(chroma_collection=self.collection)
            self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
            
            # Inicializa o cliente de LLM para configurar o modelo de embedding global (Settings)
            llm_client.initialize()
            
            self._initialized = True
            logger.info(f"✅ ChromaDB inicializado com sucesso. Coleção: {settingsInst.CHROMA_COLLECTION_NAME}")
        except Exception as e:
            logger.error(f"❌ Falha ao inicializar ChromaDB: {e}")
            raise

    def create_index_from_nodes(self, nodes: List[TextNode]) -> VectorStoreIndex:
        """
        Indexa uma lista de nodes na coleção do Chroma e retorna o objeto VectorStoreIndex.
        """
        logger.info(f"📦 Indexando {len(nodes)} nodes no ChromaDB...")
        return VectorStoreIndex(
            nodes,
            storage_context=self.storage_context,
            show_progress=True
        )

    def get_index(self) -> VectorStoreIndex:
        """
        Recupera o índice a partir da coleção existente para operações de query.
        """
        return VectorStoreIndex.from_vector_store(
            self.vector_store,
            storage_context=self.storage_context
        )

    def clear_collection(self):
        """
        Limpa todos os dados da coleção atual.
        """
        logger.warning(f"🧹 Limpando coleção {settingsInst.CHROMA_COLLECTION_NAME}...")
        try:
            self.client.delete_collection(settingsInst.CHROMA_COLLECTION_NAME)
            self.collection = self.client.get_or_create_collection(
                name=settingsInst.CHROMA_COLLECTION_NAME
            )
            self.vector_store = ChromaVectorStore(chroma_collection=self.collection)
            self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        except Exception as e:
            logger.error(f"❌ Erro ao limpar coleção: {e}")

# Instância única global
chroma_db = ChromaDB()
