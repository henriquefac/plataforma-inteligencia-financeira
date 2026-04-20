from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.service.metrics import MetricsService
from app.domain import DataArtifact

router = APIRouter()
metrics_service = MetricsService()


@router.get("/{ingestion_id}")
async def get_metrics(
    ingestion_id: str,
    status: Optional[list[str]] = Query(None, description="Filtrar por status: pago, pendente, atrasado (aceita múltiplos)"),
    cliente: Optional[str] = Query(None, description="Filtrar por nome do cliente (busca parcial)"),
    data_inicio: Optional[str] = Query(None, description="Filtrar a partir desta data (YYYY-MM-DD)"),
    data_fim: Optional[str] = Query(None, description="Filtrar até esta data (YYYY-MM-DD)"),
    recorrencia: Optional[list[str]] = Query(None, description="Filtrar por recorrência: Recorrente, Unico (aceita múltiplos)"),
    tipo_servico: Optional[list[str]] = Query(None, description="Filtrar por tipo: Assinatura, Licenca, etc (aceita múltiplos)"),
):
    """
    Retorna todas as métricas consolidadas de uma ingestão,
    com filtros opcionais para dashboard dinâmico.
    
    Filtros categóricos (status, recorrencia, tipo_servico) aceitam
    múltiplos valores: ?status=pago&status=pendente
    """
    try:
        dados = DataArtifact.load(ingestion_id)
        dados.load_enriched()

        # por enquanto ignorar os filtros, depois será implementado

        resultado = metrics_service.compute(data_artifact=dados)
        return resultado
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise e


@router.get("/{ingestion_id}/temporal")
async def get_temporal(
    ingestion_id: str,
    status: Optional[list[str]] = Query(None),
    cliente: Optional[str] = Query(None),
    data: Optional[str] = Query(None),
    recorrencia: Optional[list[str]] = Query(None),
    tipo_servico: Optional[list[str]] = Query(None),
):
    """
    Retorna evolução temporal otimizada para gráficos,
    com os mesmos filtros dinâmicos.
    """
    try:
        result = metrics_service.compute_temporal(
            ingestion_id=ingestion_id,
            status=status,
            cliente=cliente,
            data=data,
            recorrencia=recorrencia,
            tipo_servico=tipo_servico,
        )
        return result

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
