# Esses são os únicos valores possíveis para as colunas
# que serão utilizadas para os filtros
# Isso servirá para garantir a consistência dos dados
FEATURE_VALUES = {
    "status": [
        "pendente",
        "pago",
        "atrasado"
    ],
    "recorrencia": [
        "recorrente",
        "unico"
    ],
    "frequencia": [
        "mensal",
        "anual",
        "sob demanda",
        "nao aplicavel"
    ],
    "tipo_servico": [
        "assinatura",
        "licenca",
        "servico_continuo",
        "servico_pontual",
        "upgrade_plano"
    ]
}   

# No futuro será necessário também adicionar aqui todos os valores possíveis
# para as colunas que não estiverem no df enriquecido
# 