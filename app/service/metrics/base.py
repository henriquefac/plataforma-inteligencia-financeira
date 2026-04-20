from abc import ABC, abstractmethod
import pandas as pd


class Metric(ABC):
    """Interface para todas as métricas.
    
    Toda métrica calcula um valor escalar (float) a partir de um DataFrame.
    O DataFrame já chega filtrado — a métrica não se preocupa com filtros.
    
    Pode ser usada como callable: metric(df) → float, o que permite
    passá-la diretamente para a função de evolução temporal.
    
    Atributos:
        name: Identificador único da métrica.
        group: Grupo de visualização (ex: "receita", "ticket", "taxa").
               Métricas do mesmo grupo compartilham o mesmo gráfico/escala.
        required_columns: Colunas necessárias no DataFrame para cálculo.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Nome da métrica para exibição"""
        pass

    @property
    @abstractmethod
    def group(self) -> str:
        """Grupo de visualização para agrupar métricas no dashboard.
        
        Métricas do mesmo grupo compartilham escala e gráfico.
        Ex: "receita", "ticket", "taxa"
        """
        pass
    
    @property
    @abstractmethod
    def required_columns(self) -> list[str]:
        """Colunas que precisam existir no DataFrame para o cálculo"""
        pass
    
    def verify_columns_required(self, df: pd.DataFrame) -> bool:
        """Verifica se as colunas necessárias estão presentes no DataFrame"""
        return all(col in df.columns for col in self.required_columns)
    
    @abstractmethod
    def calculate(self, df: pd.DataFrame) -> float:
        """Calcula a métrica. Assume que as colunas necessárias já foram verificadas."""
        pass
    
    def __call__(self, df: pd.DataFrame) -> float:
        """Permite usar a métrica como callable: metric(df) → float.
        
        Valida colunas antes de calcular. Levanta ValueError se faltar alguma.
        """
        if not self.verify_columns_required(df):
            missing = [col for col in self.required_columns if col not in df.columns]
            raise ValueError(
                f"Colunas necessárias para '{self.name}' não encontradas: {missing}"
            )
        return self.calculate(df)