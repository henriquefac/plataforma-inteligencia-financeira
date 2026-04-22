import pandas as pd
import numpy as np
from typing import Dict, Any, List
from app.core.config import settingsInst


class DeterministicInsightsService:
    """
    Camada determinística de métricas com explicação embutida.
    """

    # -----------------------------
    # Helper padrão de métrica
    # -----------------------------
    def _metric(self, valor, descricao, unidade=None, interpretacao=None):
        return {
            "valor": valor,
            "descricao": descricao,
            "unidade": unidade,
            "interpretacao": interpretacao
        }

    def calculate(self, df: pd.DataFrame) -> Dict[str, Any]:
        if df.empty:
            return {}

        results = {}
        client_types = settingsInst.TIPOS_CLIENTES

        total_real = df["receita_real"].sum()
        total_potencial = df["receita_potencial"].sum()

        # -----------------------------
        # Receita / Conversão
        # -----------------------------
        taxa_conv = float(total_real / total_potencial) if total_potencial > 0 else 0

        results["taxa_conversao_receita_total"] = self._metric(
            taxa_conv,
            "Percentual da receita potencial convertido em receita real",
            unidade="%",
            interpretacao="Boa" if taxa_conv > 0.8 else "Atenção" if taxa_conv > 0.6 else "Crítica"
        )

        receita_perdida = float(total_potencial - total_real)

        results["receita_perdida_total"] = self._metric(
            receita_perdida,
            "Valor de receita potencial não convertido em receita real",
            unidade="R$",
            interpretacao="Crítica" if receita_perdida > (total_potencial * 0.3) else "Atenção" if receita_perdida > (total_potencial * 0.1) else "Saudável"
        )

        # -----------------------------
        # Cliente (base)
        # -----------------------------
        receita_cliente = df.groupby("cliente")[["receita_real", "receita_potencial"]].sum()

        receita_cliente["taxa_conversao"] = (
            receita_cliente["receita_real"] / receita_cliente["receita_potencial"]
        ).fillna(0)

        results["taxa_conversao_por_cliente_top_10"] = self._metric(
            receita_cliente["taxa_conversao"].nlargest(10).to_dict(),
            "Top 10 clientes com maior taxa de conversão de receita",
            unidade="%"
        )

        results["receita_perdida_por_cliente_top_10"] = self._metric(
            (receita_cliente["receita_potencial"] - receita_cliente["receita_real"])
            .nlargest(10).to_dict(),
            "Top 10 clientes com maior volume de receita não convertida (gap de faturamento)",
            unidade="R$"
        )

        # -----------------------------
        # Inadimplência
        # -----------------------------
        inad_valor = (
            df[df["is_inadimplente"]]["receita_potencial"].sum() / total_potencial
        ) if total_potencial > 0 else 0

        results["taxa_inadimplencia_ponderada_valor"] = self._metric(
            float(inad_valor),
            "Percentual da receita potencial perdida por inadimplência (valor ponderado)",
            unidade="%",
            interpretacao="Crítica" if inad_valor > 0.15 else "Atenção" if inad_valor > 0.07 else "Saudável"
        )

        # -----------------------------
        # Segmentos
        # -----------------------------
        if "tipo_servico" in df.columns:
            risco_segmento = df.groupby("tipo_servico")["is_inadimplente"].mean().to_dict()

            results["risco_inadimplencia_percentual_por_segmento"] = self._metric(
                risco_segmento,
                "Probabilidade de inadimplência baseada no histórico de cada segmento",
                unidade="%"
            )

            receita_risco = (
                df[df["is_inadimplente"]]
                .groupby("tipo_servico")["receita_potencial"]
                .sum()
                .to_dict()
            )

            results["receita_em_risco_por_segmento"] = self._metric(
                receita_risco,
                "Valor financeiro em risco por tipo de serviço",
                unidade="R$"
            )

        # -----------------------------
        # Pareto
        # -----------------------------
        sorted_receita = receita_cliente["receita_real"].sort_values(ascending=False)

        top_n = max(1, int(len(sorted_receita) * 0.2))
        top_sum = sorted_receita.iloc[:top_n].sum()

        pareto = float(top_sum / total_real) if total_real > 0 else 0

        results["indice_concentracao_pareto_top_20"] = self._metric(
            pareto,
            "Grau de dependência dos 20% maiores clientes no faturamento total",
            unidade="%",
            interpretacao="Risco de Concentração" if pareto > 0.8 else "Distribuição Saudável"
        )

        # -----------------------------
        # Distribuição dinâmica
        # -----------------------------
        if not receita_cliente.empty:
            distribuicao = (
                pd.qcut(
                    receita_cliente["receita_potencial"],
                    q=5,
                    duplicates="drop"
                )
                .value_counts()
                .sort_index()
            )

            results["distribuicao_clientes_por_faixa_valor"] = self._metric(
                {str(k): int(v) for k, v in distribuicao.items()},
                "Distribuição de clientes por faixa de receita potencial"
            )

        # -----------------------------
        # Recorrência
        # -----------------------------
        if "recorrencia" in df.columns:
            rec = df.groupby("recorrencia")["receita_real"].sum().to_dict()

            results["receita_real_por_tipo_recorrencia"] = self._metric(
                rec,
                "Distribuição da receita por tipo de recorrência"
            )

        # -----------------------------
        # Receita ajustada por risco
        # -----------------------------
        receita_ajustada = total_real * (1 - inad_valor)

        results["receita_ajustada_risco"] = self._metric(
            float(receita_ajustada),
            "Expectativa de receita real após descontar o risco de inadimplência atual",
            unidade="R$",
            interpretacao="Abaixo do esperado" if receita_ajustada < total_real else "Estável"
        )

        # -----------------------------
        # Conversão por segmento
        # -----------------------------
        if "tipo_servico" in df.columns:
            conv_segmento = (
                df.groupby("tipo_servico")
                .apply(lambda x: x["receita_real"].sum() / x["receita_potencial"].sum()
                       if x["receita_potencial"].sum() > 0 else 0)
                .to_dict()
            )

            results["taxa_conversao_por_segmento"] = self._metric(
                conv_segmento,
                "Eficiência de faturamento por tipo de serviço",
                unidade="%"
            )

        # -----------------------------
        # Tempo
        # -----------------------------
        receita_mes = df.groupby(["ano", "mes"])["receita_real"].sum()

        volatilidade = receita_mes.pct_change().std()
        consistencia = (receita_mes.pct_change() > 0).mean()

        results["volatilidade_receita_mensal"] = self._metric(
            float(volatilidade),
            "Grau de oscilação do faturamento mensal (estabilidade do fluxo de caixa)",
            interpretacao="Alta Volatilidade" if volatilidade > 0.25 else "Estável"
        )

        results["crescimento_consistente_meses"] = self._metric(
            float(consistencia),
            "Frequência de meses com viés de alta no faturamento",
            unidade="%",
            interpretacao="Excelente" if consistencia > 0.8 else "Inconsistente" if consistencia < 0.5 else "Moderado"
        )

        # -----------------------------
        # Cliente comportamento
        # -----------------------------
        ticket_cliente = df.groupby("cliente")["receita_real"].mean()

        results["ticket_medio_por_cliente_top_10"] = self._metric(
            ticket_cliente.nlargest(10).to_dict(),
            "Valor médio por transação dos 10 clientes de maior ticket",
            unidade="R$"
        )

        freq_cliente = df.groupby("cliente")["receita_real"].count()

        results["frequencia_transacoes_cliente_top_10"] = self._metric(
            freq_cliente.nlargest(10).to_dict(),
            "Número de transações realizadas pelos 10 clientes mais ativos",
            unidade="Qtd"
        )

        if "tipo_servico" in df.columns:
            ticket_segmento = df.groupby("tipo_servico")["receita_real"].mean()

            results["ticket_medio_por_segmento"] = self._metric(
                ticket_segmento.to_dict(),
                "Ticket médio por tipo de serviço"
            )

            freq_segmento = df.groupby("tipo_servico")["receita_real"].count()

            results["frequencia_transacoes_por_segmento"] = self._metric(
                freq_segmento.to_dict(),
                "Frequência de transações por tipo de serviço"
            )

        # -----------------------------
        # Contribuição
        # -----------------------------
        self._add_contribution_metrics(df, results, client_types)

        return results

    def _add_contribution_metrics(self, df: pd.DataFrame, results: dict, client_types: List[str]):
        total_real = df["receita_real"].sum()
        if total_real <= 0:
            return

        receita_cliente = df.groupby("cliente")["receita_real"].sum()

        results["contribuicao_receita_por_cliente_top_10"] = self._metric(
            (receita_cliente / total_real).nlargest(10).to_dict(),
            "Participação percentual dos 10 principais clientes na receita total (Share)",
            unidade="%"
        )

        contribuicao_tipo = {}
        for tipo in client_types:
            if tipo in df.columns:
                contribuicao_tipo[tipo] = float(
                    df[df[tipo]]["receita_real"].sum() / total_real
                )

        results["contribuicao_por_tipo_cliente"] = self._metric(
            contribuicao_tipo,
            "Representatividade de cada categoria de cliente no faturamento global",
            unidade="%"
        )

        if "recorrencia" in df.columns:
            results["contribuicao_por_tipo_recorrencia"] = self._metric(
                (df.groupby("recorrencia")["receita_real"].sum() / total_real).to_dict(),
                "Divisão da receita entre contratos recorrentes e vendas pontuais",
                unidade="%"
            )