from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.service.rag import RAGIndexer, RAGQueryEngine
from app.service.rag.embedding import EmbeddingService

router = APIRouter()
rag_indexer = RAGIndexer()
rag_query_engine = RAGQueryEngine()
embedding_service = EmbeddingService()


class QueryRequest(BaseModel):
    ingestion_id: str
    question: str

class SimpleConsult(BaseModel):
    ingestion_id: str


@router.post("/query")
async def rag_query(request: QueryRequest):
    """
    Consulta em linguagem natural sobre os dados financeiros.
    Usa RAG para buscar transações relevantes e gerar resposta contextualizada.
    """
    try:
        result = await rag_query_engine.query(
            ingestion_id=request.ingestion_id,
            question=request.question,
        )
        return result

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/embeddings")
async def create_embeddings(request: SimpleConsult):
    """
    Gera e armazena os embeddings para uma ingestão no ChromaDB.
    Este processo transforma os dados enriquecidos em representações vetoriais.
    """
    try:
        result = await embedding_service.generate_and_store_embeddings(ingestion_id=request.ingestion_id)
        
        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("error"))
            
        return result

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
