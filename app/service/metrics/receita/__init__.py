# Aqui será os métodos e funções associados a o calculo da métrica "Receita"

# Receita potencial ou total
# - Soma direta da coluna "valor" do df
# Receita real
# - Soma direta da coluna "valor" do df cujo registro possui o valor "pago" na coluna "status"
# Receita inadimplente
# - Soma direta da coluna "valor" do df cujo registro possui o valor "True" na coluna "is_inadimplente"

# Além disso será necessário também criar os métodos para o calculo da evolução temporal da receita.

# Qualquer outra observação da receita, por exemplo: "Receita total para as empresa do tipo loja"
# sera feito usando filtros dinâmicos, limitando os registros apenas para aqueles que forem
# do tipo loja (seguindo esse exemplo).

from app.service.metrics.base import Metric