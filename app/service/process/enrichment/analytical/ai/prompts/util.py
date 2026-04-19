from typing import get_origin
import json

def schema_to_example(schema_cls):
    example = {}

    for name, field in schema_cls.model_fields.items():
        origin = get_origin(field.annotation)

        if origin is list:
            example[name] = ["valor1", "valor2"]
        else:
            example[name] = "valor"

    return json.dumps(example, indent=2, ensure_ascii=False)