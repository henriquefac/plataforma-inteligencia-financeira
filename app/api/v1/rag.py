from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.service.rag import RAGIndexer, RAGQueryEngine

router = APIRouter()
rag_indexer = RAGIndexer()
rag_query_engine = RAGQueryEngine()


class QueryRequest(BaseModel):
    ingestion_id: str
    question: str


@router.post("/query")
async def rag_query(request: QueryRequest):
    """
    Consulta geral em linguagem natural. 
    Atualmente utiliza a interpretação direta em Pandas para maior precisão.
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


@router.post("/analytics/interpret")
async def analytics_interpret(request: QueryRequest):
    """
    Endpoint especializado para interpretação analítica.
    Converte a pergunta em código Pandas e executa sobre o dataset.
    Retorna o código gerado e o resultado formatado.
    """
    try:
        # A lógica atual do query_engine já é 100% interpretação
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


@router.post("/{ingestion_id}/index")
def build_index(ingestion_id: str):
    """
    Força a (re)construção do índice vetorial para uma ingestão.
    """
    try:
        rag_indexer.build_index(ingestion_id)
        return {
            "ingestion_id": ingestion_id,
            "status": "indexed",
            "message": "Índice construído com sucesso",
        }

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
