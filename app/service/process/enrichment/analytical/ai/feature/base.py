from abc import ABC, abstractmethod
import pandas as pd

class BaseFeature(ABC):

    feature_name = None

    @abstractmethod
    def discover_values(self, df: pd.DataFrame, max_retries):
        pass

    @abstractmethod
    def classify(self, text, values):
        pass

    @abstractmethod
    def apply(self, df: pd.DataFrame, values):
        pass