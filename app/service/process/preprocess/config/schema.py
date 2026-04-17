import pandas as pd

def to_string(s):
    return s.astype("string")

def to_float(s):
    return pd.to_numeric(s, errors="coerce")

def to_datetime(s):
    return pd.to_datetime(s, errors="coerce")


SCHEMA = {
    "cliente": to_string,
    "valor": to_float,
    "status": to_string,
    "descricao": to_string,
    "data": to_datetime
}