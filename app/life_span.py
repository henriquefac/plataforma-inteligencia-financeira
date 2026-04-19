from app.core.config import settingsInst
from app.core.llm import llm_client

def initApp():
    # inicializar o cliente para acessar as llms
    llm_client.initialize()

    # ralizar teste com o llm

    # Criar pastas baseadas no que foi configurado
    # pastas para armazenar arquivos
    for path in [
        settingsInst.UPLOAD_DIR,
        settingsInst.PROCESS_DIR,
        settingsInst.ENRICH_DIR,
        settingsInst.METADATA_DIR,
    ]:
        path.mkdir(parents=True, exist_ok=True)
