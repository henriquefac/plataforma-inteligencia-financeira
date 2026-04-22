import shutil
import logging

from app.core.config import settingsInst
from app.core.llm import llm_client

logger = logging.getLogger(__name__)

# Diretórios de dados que são gerenciados pela aplicação
_DATA_DIRS = [
    settingsInst.UPLOAD_DIR,
    settingsInst.PROCESS_DIR,
    settingsInst.ENRICH_DIR,
    settingsInst.METADATA_DIR,
    settingsInst.INDEX_DIR,
]

def initApp():
    # inicializar o cliente para acessar as llms
    llm_client.initialize()

    # ralizar teste com o llm

    # Criar pastas baseadas no que foi configurado
    # pastas para armazenar arquivos
    for path in _DATA_DIRS:
        path.mkdir(parents=True, exist_ok=True)


def shutdownApp():
    """Executado ao encerrar a API.

    Se CLEAR_DATA_ON_SHUTDOWN estiver habilitado, apaga todo o conteúdo
    dos diretórios de dados (raw, clean, enrich, metadata, indices).
    """
    if not settingsInst.CLEAR_DATA_ON_SHUTDOWN:
        logger.info("CLEAR_DATA_ON_SHUTDOWN desabilitado — dados preservados.")
        return

    logger.warning("CLEAR_DATA_ON_SHUTDOWN habilitado — apagando dados gerados…")
    for path in _DATA_DIRS:
        if path.exists():
            shutil.rmtree(path)
            logger.info("Removido: %s", path)
    logger.info("Limpeza de dados concluída.")
