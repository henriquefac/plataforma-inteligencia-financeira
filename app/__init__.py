# Primeiramente é preciso pegar o diretório base
from pathlib import Path
BASEDIR = Path(__file__).resolve().parent.parent # Nível superior ao diretório "app"

from fastapi import FastAPI

# definir comportamento ao iniciar
# e finalizar a aplicação
from contextlib import asynccontextmanager
from app.life_span import initApp

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Definir comportamento ao iniciar
    initApp()
    # =================================
    yield
    # Definir comporttamento ao fializar
    # ==================================
    
# Instanciar a aplicação
app = FastAPI(lifespan=lifespan)

# Routers
from app.api.v1.upload import router as upload_router

app.include_router(upload_router, prefix="/files", tags=["files"])