# Primeiramente é preciso pegar o diretório base
from pathlib import Path
BASEDIR = Path(__file__).resolve().parent.parent # Nível superior ao diretório "app"

from fastapi import FastAPI

# definir comportamento ao iniciar
# e finalizar a aplicação
from contextlib import asynccontextmanager
from app.life_span import initApp, shutdownApp

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Definir comportamento ao iniciar
    initApp()
    # =================================
    yield
    # Definir comportamento ao finalizar
    shutdownApp()
    # ==================================
    
# Instanciar a aplicação
app = FastAPI(lifespan=lifespan)

# Routers
from app.api.v1.upload import router as upload_router
from app.api.v1.metrics import router as metrics_router
from app.api.v1.insights import router as insights_router
from app.api.v1.rag import router as rag_router
from app.api.v1.artifacts import router as artifacts_router
from app.api.v1.filters import router as filters_router

app.include_router(upload_router, prefix="/files", tags=["files"])
app.include_router(metrics_router, prefix="/metrics", tags=["metrics"])
app.include_router(filters_router, prefix="/filters", tags=["filters"])
app.include_router(insights_router, prefix="/insights", tags=["insights"])
app.include_router(rag_router, prefix="/rag", tags=["rag"])
app.include_router(artifacts_router, prefix="/artifacts", tags=["artifacts"])