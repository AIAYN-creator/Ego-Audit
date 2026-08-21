from ego_audit.datos.universo import BENCHMARK, TICKERS_ADICIONALES, UNIVERSO


def test_benchmark_esta_en_el_universo():
    assert BENCHMARK in UNIVERSO


def test_universo_sin_duplicados():
    assert len(UNIVERSO) == len(set(UNIVERSO))


def test_universo_es_benchmark_mas_adicionales():
    assert UNIVERSO == [BENCHMARK] + TICKERS_ADICIONALES


def test_universo_es_un_punado_no_todo_el_mercado():
    assert 1 < len(UNIVERSO) <= 10
