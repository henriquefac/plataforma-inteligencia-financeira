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

# Schema mapeando as colunas para seus nomes amigáveis
ENRICHED_SCHEMA: dict[str, str] = {
    # ── Colunas originais (input do usuário) ──
    "cliente":    "Cliente",
    "valor":      "Valor",
    "status":     "Status",
    "descricao":  "Descrição",
    "data":       "Data",

    # ── Enriquecimento estrutural: datetime ──
    "ano":        "Ano",
    "mes":        "Mês",
    "dia":        "Dia",
    "dia_semana": "Dia da Semana",

    # ── Enriquecimento estrutural: flags de status ──
    "is_pago":          "É Pago",
    "is_inadimplente":  "É Inadimplente",

    # ── Enriquecimento estrutural: tipo de cliente ──
    # (default de settings.TIPOS_CLIENTES)
    # Se TIPOS_CLIENTES mudar no .env, atualize aqui também.
    "empresa":  "Empresa",
    "loja":     "Loja",
    "startup":  "Startup",

    # ── Enriquecimento estrutural: financeiro ──
    "receita_potencial":      "Receita Potencial",
    "receita_real":           "Receita Real",
    "qtd_transacoes_cliente": "Qtd. Transações do Cliente",
    "valor_medio_cliente":    "Valor Médio do Cliente",

    # ── Enriquecimento analítico (IA) ──
    "recorrencia":  "Recorrência",
    "frequencia":   "Frequência",
    "tipo_servico": "Tipo de Serviço",
}
