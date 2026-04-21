"""
Testes rápidos para o FilterService.
Roda standalone: python -m app.service.filter.test_filter
"""

import pandas as pd
from app.service.filter.filter import FilterService


def _sample_df() -> pd.DataFrame:
    """Cria um DataFrame de exemplo imitando o schema enriquecido."""
    return pd.DataFrame({
        "cliente": ["Empresa A", "Empresa B", "Empresa C", "Empresa A"],
        "valor": [1000.0, 2500.0, 500.0, 3000.0],
        "status": ["pago", "pendente", "atrasado", "pago"],
        "descricao": ["Serv. X", "Serv. Y", "Serv. Z", "Serv. W"],
        "data": pd.to_datetime(["2024-01-15", "2024-03-20", "2024-06-01", "2024-12-10"]),
        "is_pago": [True, False, False, True],
        "is_inadimplente": [False, False, True, False],
    })


def test_discover():
    svc = FilterService()
    df = _sample_df()
    filters = svc.discover_filters(df)

    print("=== Filtros Descobertos ===")
    for f in filters:
        print(f"  {f}")

    # descricao NÃO deve aparecer
    col_names = [f["column"] for f in filters]
    assert "descricao" not in col_names, "descricao não deveria estar nos filtros!"

    # valor e data devem ser range
    valor_filter = next(f for f in filters if f["column"] == "valor")
    assert valor_filter["filter_type"] == "range"
    assert valor_filter["kind"] == "number"
    assert valor_filter["min"] == 500.0
    assert valor_filter["max"] == 3000.0

    data_filter = next(f for f in filters if f["column"] == "data")
    assert data_filter["filter_type"] == "range"
    assert data_filter["kind"] == "date"

    # status deve ser tag
    status_filter = next(f for f in filters if f["column"] == "status")
    assert status_filter["filter_type"] == "tag"
    assert set(status_filter["values"]) == {"pago", "pendente", "atrasado"}

    print("  ✓ discover_filters OK")


def test_apply_range():
    svc = FilterService()
    df = _sample_df()

    # Filtrar valor entre 500 e 1500
    result = svc.apply(df, {"valor": {"min": 500, "max": 1500}})
    assert len(result) == 2, f"Esperado 2 registros, obteve {len(result)}"
    assert set(result["valor"]) == {500.0, 1000.0}
    print("  ✓ apply range (valor) OK")


def test_apply_tag():
    svc = FilterService()
    df = _sample_df()

    # Filtrar apenas status = pago
    result = svc.apply(df, {"status": ["pago"]})
    assert len(result) == 2, f"Esperado 2 registros, obteve {len(result)}"
    assert all(result["status"] == "pago")
    print("  ✓ apply tag (status) OK")


def test_apply_combined():
    svc = FilterService()
    df = _sample_df()

    # Filtrar status = pago E valor >= 2000
    result = svc.apply(df, {
        "status": ["pago"],
        "valor": {"min": 2000},
    })
    assert len(result) == 1, f"Esperado 1 registro, obteve {len(result)}"
    assert result.iloc[0]["valor"] == 3000.0
    print("  ✓ apply combined (status + valor) OK")


def test_apply_date_range():
    svc = FilterService()
    df = _sample_df()

    # Filtrar datas do primeiro semestre de 2024
    result = svc.apply(df, {
        "data": {"min": "2024-01-01", "max": "2024-06-30"},
    })
    assert len(result) == 3, f"Esperado 3 registros, obteve {len(result)}"
    print("  ✓ apply date range OK")


def test_apply_empty():
    svc = FilterService()
    df = _sample_df()

    # Filtro vazio não deve remover nada
    result = svc.apply(df, {})
    assert len(result) == len(df)
    print("  ✓ apply empty OK")


def test_descricao_ignored():
    svc = FilterService()
    df = _sample_df()

    # Tentar filtrar por descricao — deve ser ignorado
    result = svc.apply(df, {"descricao": ["Serv. X"]})
    assert len(result) == len(df), "descricao deveria ser ignorada!"
    print("  ✓ descricao ignored OK")


if __name__ == "__main__":
    test_discover()
    test_apply_range()
    test_apply_tag()
    test_apply_combined()
    test_apply_date_range()
    test_apply_empty()
    test_descricao_ignored()
    print("\n✅ Todos os testes passaram!")
