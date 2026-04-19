from typing import Any
import json


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",") if i.strip()]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)

def parse_extensoes(v: Any) -> list[str]:
    if isinstance(v, str):
        # Caso: ".csv,.xlsx"
        if not v.startswith("["):
            return [ext.strip().lower() for ext in v.split(",") if ext.strip()]
        
        # Caso: JSON string '[".csv",".xlsx"]'
        import json
        return [ext.strip().lower() for ext in json.loads(v)]

    elif isinstance(v, list):
        return [str(ext).strip().lower() for ext in v]

    raise ValueError(f"Formato inválido para EXTENSOES_VALIDAS: {v}")

def parse_list_str(v: Any) -> list[str]:
    if isinstance(v, str):
        if not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        return json.loads(v)

    elif isinstance(v, list):
        return [str(i).strip() for i in v]

    raise ValueError(f"Formato inválido: {v}")


def parse_max_size(v: Any) -> int:
    if isinstance(v, int):
        if v <= 0:
            raise ValueError("MAX_SIZE deve ser positivo")
        return v

    if isinstance(v, str):
        v = v.strip().upper()

        if v.endswith("MB"):
            return int(v.replace("MB", "").strip()) * 1024 * 1024
        if v.endswith("KB"):
            return int(v.replace("KB", "").strip()) * 1024
        if v.isdigit():
            return int(v)

    raise ValueError(f"Formato inválido para MAX_SIZE: {v}")


def validate_colunas(v: list[str]) -> list[str]:
    if not v:
        raise ValueError("COLUNAS não pode ser vazio")

    normalized = [c.strip().lower() for c in v]

    if len(set(normalized)) != len(normalized):
        raise ValueError("COLUNAS contém duplicatas")

    return normalized


def validate_status(v: list[str]) -> list[str]:
    if not v:
        raise ValueError("STATUS_VALIDOS não pode ser vazio")

    normalized = [s.strip().lower() for s in v]

    if len(set(normalized)) != len(normalized):
        raise ValueError("STATUS_VALIDOS contém duplicatas")

    return normalized