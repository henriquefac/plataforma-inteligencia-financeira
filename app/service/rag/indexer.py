import pandas as pd
from pathlib import Path

from llama_index.core import (
    VectorStoreIndex,
    Document,
    StorageContext,
    load_index_from_storage,
)

from app.domain.data_artifact import DataArtifact, DataStatus
from app.core.config import settingsInst


class RAGIndexer:
    """
    Responsável por construir e persistir índices vetoriais
    a partir dos dados enriquecidos, para permitir consultas
    em linguagem natural (RAG).
    """

    def _get_index_path(self, ingestion_id: str) -> Path:
        """Retorna o diretório do índice para uma ingestão."""
        return settingsInst.INDEX_DIR / ingestion_id

    def _row_to_document(self, row: pd.Series) -> Document:
        """
        Converte uma linha do DataFrame em um Document do LlamaIndex.
        Combina todas as informações relevantes em texto legível.
        """
        parts = []

        if pd.notna(row.get("cliente")):
            parts.append(f"Cliente: {row['cliente']}")

        if pd.notna(row.get("data")):
            parts.append(f"Data: {row['data']}")

        if pd.notna(row.get("valor")):
            parts.append(f"Valor: R$ {row['valor']:.2f}")

        if pd.notna(row.get("status")):
            parts.append(f"Status: {row['status']}")

        if pd.notna(row.get("descricao")):
            parts.append(f"Descrição: {row['descricao']}")

        if pd.notna(row.get("recorrencia")):
            parts.append(f"Recorrência: {row['recorrencia']}")

        if pd.notna(row.get("frequencia")):
            parts.append(f"Frequência: {row['frequencia']}")

        if pd.notna(row.get("tipo_servico")):
            parts.append(f"Tipo de serviço: {row['tipo_servico']}")

        if pd.notna(row.get("is_inadimplente")):
            parts.append(f"Inadimplente: {'Sim' if row['is_inadimplente'] else 'Não'}")

        text = "\n".join(parts)

        # Metadata para filtros e referência
        metadata = {}
        for col in ["id", "cliente", "status", "valor", "data", "recorrencia", "tipo_servico"]:
            if col in row.index and pd.notna(row[col]):
                metadata[col] = str(row[col])

        return Document(text=text, metadata=metadata)

    def build_index(self, ingestion_id: str) -> VectorStoreIndex:
        """
        Constrói o índice vetorial a partir dos dados enriquecidos
        e persiste em disco.
        """
        # 1. Carregar dados enriquecidos
        artifact = DataArtifact.load(ingestion_id)

        if artifact.status != DataStatus.ENRICHED:
            raise ValueError(
                f"Dados não estão enriquecidos (status: {artifact.status}). "
                f"Execute o pipeline completo antes de indexar."
            )

        df = artifact.load_enriched()

        # 2. Converter linhas em Documents
        documents = []
        for _, row in df.iterrows():
            doc = self._row_to_document(row)
            documents.append(doc)

        # 3. Criar índice vetorial
        index = VectorStoreIndex.from_documents(documents)

        # 4. Persistir
        persist_dir = self._get_index_path(ingestion_id)
        persist_dir.mkdir(parents=True, exist_ok=True)
        index.storage_context.persist(persist_dir=str(persist_dir))

        return index

    def load_index(self, ingestion_id: str) -> VectorStoreIndex:
        """Carrega um índice previamente persistido."""
        persist_dir = self._get_index_path(ingestion_id)

        if not persist_dir.exists():
            raise FileNotFoundError(
                f"Índice não encontrado para ingestão {ingestion_id}. "
                f"Execute a indexação primeiro."
            )

        storage_context = StorageContext.from_defaults(
            persist_dir=str(persist_dir)
        )
        return load_index_from_storage(storage_context)

    def get_or_build_index(self, ingestion_id: str) -> VectorStoreIndex:
        """
        Tenta carregar o índice existente.
        Se não existir, constrói automaticamente.
        """
        try:
            return self.load_index(ingestion_id)
        except FileNotFoundError:
            return self.build_index(ingestion_id)

    def index_exists(self, ingestion_id: str) -> bool:
        """Verifica se já existe um índice para a ingestão."""
        return self._get_index_path(ingestion_id).exists()
