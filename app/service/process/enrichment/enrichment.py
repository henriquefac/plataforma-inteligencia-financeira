import pandas as pd
from app.domain.data_artifact import DataArtifact, DataStatus
from app.core.config import settingsInst

from .structural import StructuralEnrich
from .analytical import AnalyticalEnrich

# Aqui será feito o enriquecimento dos dados.
# Esse enriquecimento por sua vez possui duas vertentes,
# analítico e estrutural. O estrutural apenas utiliza
# as colunas já presentes para expandir as colunas.
# Já o analitico usa o campo "descricao" com o apoio
# de ia para conseguir extrair valores pertinentes a novas
# colunas.  

class EnrichService:
    def __init__(self):
        self.df:pd.DataFrame = None
        self.log = {}

        # Sub-pipelines
        self.structural = StructuralEnrich()
        self.analytical = AnalyticalEnrich()
    

    def run(self, data: DataArtifact) -> dict:
        # ter certeza que os dados foram processados
        if data.status == DataStatus.ERROR:
            raise(ValueError("Houve um erro na etapa de preprocessamento"))
        if not (data.status == DataStatus.PROCESSED):
            raise(ValueError("Dados não passram pelo processo de preprocessamento antes do enriquecimento"))
        print("Inciando enriquecimento")
        try:
            # é esperado que os dados tenham passado pelo pre-processamento
            # 1. Carregar dados processados
            df = data.load_processed()

            # 2. iniciar DataFrame da classe
            self.df = df.copy()


            print("Usando ia")
            # 4. ralizar enriquecimento analitico
            self.df = self.analytical.run(self.df)
            print("Feito")

            # 3. realizar enriquecimento estrutural
            print("Enriquecimento estrutual")
            self.df = self.structural.run(self.df)
            print("Enriquecimento estrutural feito")

            data.save_enriched(self.df)

        except Exception as e:
            data.status = "erro"
            data._save_metadata()
            raise e
    