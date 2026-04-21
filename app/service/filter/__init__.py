# os filtros vão servir para consumir o objeto
# DataArtifact e devolver o DataFrame de interesse
# apenas com os registros que satisfazem os os parametros passados

# ideia central: 
# - Objeto FilterService vai ser declarado
# - A instância do objeto vai ser passado para o serviço de métricas.
# - O serviço de métricas, quando for calcular, vai checar se possui a instancia
# - se possuir, vai passar os filtros e receber o dataframe
# - se não possuir, vai calcular sem filtros

# Além disso, o filtro vai eleger quais são as colunas usáveis para filtrar e como
# pode ser filtrado. Por exemplo:
# - valor: pode ser filtrado por faixa de valores
# - status: pode ser filtrado por valores exatos
# - cliente: pode ser filtrado por valores exatos
# - descricao: NÃO é filtrado
# - data: pode ser filtrado por faixa de datas

from app.service.filter.filter import FilterService
from app.service.filter.util import EXCLUDED_COLUMNS

__all__ = ["FilterService", "EXCLUDED_COLUMNS"]