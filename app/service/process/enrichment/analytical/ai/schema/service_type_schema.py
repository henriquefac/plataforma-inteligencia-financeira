from pydantic import BaseModel
from typing import List

class ServiceTypeSchema(BaseModel):
    tipo_servico: List[str]


def validate_schema(schema: ServiceTypeSchema):

    if len(schema.tipo_servico) > 10:
        raise ValueError("Muitos tipos de serviço")

    for v in schema.tipo_servico:
        if len(v) > 20:
            raise ValueError(f"Valor muito longo: {v}")

    return True