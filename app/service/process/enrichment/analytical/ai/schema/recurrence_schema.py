from pydantic import BaseModel
from typing import List

class RecurrenceSchema(BaseModel):
    recorrencia: List[str]


def validate_schema(schema: RecurrenceSchema):

    if len(schema.recorrencia) > 10:
        raise ValueError("Muitos valores de recorrência")

    for v in schema.recorrencia:
        if len(v) > 20:
            raise ValueError(f"Valor muito longo: {v}")

    return True