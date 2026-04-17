from dataclasses import dataclass
import pandas as pd
from typing import Dict

@dataclass
class RestultPreProcess:
    df: pd.DataFrame
    statusValid: pd.DataFrame
    statusInvalid: pd.DataFrame
    log: Dict