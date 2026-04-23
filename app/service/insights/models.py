from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum

class Severity(str, Enum):
    ALTA = "alta"
    MEDIA = "media"
    BAIXA = "baixa"

class Risk(str, Enum):
    ALTO = "alto"
    MEDIO = "medio"
    BAIXO = "baixo"

class AnomalyType(str, Enum):
    OUTLIER = "outlier"
    CONCENTRACAO = "concentracao"
    INADIMPLENCIA = "inadimplencia"
    CONVERSAO = "conversao"
    QUEDA_CONTRIBUICAO = "queda_contribuicao"
    VOLATILIDADE = "volatilidade"

class PatternType(str, Enum):
    COMPORTAMENTO = "comportamento"
    SEGMENTACAO = "segmentacao"
    CORRELACAO = "correlacao"
    RECORRENCIA = "recorrencia"

class InsightModel(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    titulo: str
    observacao: str
    impacto: str
    acao: str
    severidade: str
class InsightResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    insights: List[InsightModel]

class AnomalyModel(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    tipo: str
    descricao: str
    evidencia: str
    risco: str
    recomendacao: str

class PatternModel(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    tipo: str
    descricao: str
    evidencia: str

class AnomalyResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    anomalias: List[AnomalyModel]
    padroes: List[PatternModel]
