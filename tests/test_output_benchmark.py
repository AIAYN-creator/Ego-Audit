import pandas as pd
import pytest

from ego_audit.datos.descarga import descargar_historico
from ego_audit.output.benchmark import buy_and_hold


def _precios(valores: list[float]) -> pd.Series:
    return pd.Series(valores, index=pd.date_range("2024-01-01", periods=len(valores)))


def test_primer_dia_siempre_vale_1():
    valor = buy_and_hold(_precios([100.0, 110.0, 90.0]))
    assert valor.iloc[0] == 1.0


def test_replica_el_retorno_completo_del_precio():
    valor = buy_and_hold(_precios([100.0, 110.0, 121.0]))
    assert valor.iloc[-1] == pytest.approx(1.21, rel=1e-9)


def test_precio_plano_no_cambia_de_valor():
    valor = buy_and_hold(_precios([100.0, 100.0, 100.0]))
    assert (valor == 1.0).all()


def test_conserva_el_indice_de_precios():
    precios = _precios([100.0, 105.0])
    valor = buy_and_hold(precios)
    assert list(valor.index) == list(precios.index)


@pytest.mark.slow
def test_buy_and_hold_real_de_spy():
    precios = descargar_historico("SPY", "2024-01-01", "2024-06-01")["Close"]
    valor = buy_and_hold(precios)

    assert valor.iloc[0] == 1.0
    assert len(valor) == len(precios)
    # el retorno total del ultimo dia debe coincidir con el retorno real del precio
    retorno_precio = precios.iloc[-1] / precios.iloc[0]
    assert valor.iloc[-1] == pytest.approx(retorno_precio, rel=1e-6)
