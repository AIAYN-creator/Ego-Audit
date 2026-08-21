import pandas as pd
import pytest

from ego_audit.datos.alineacion import alinear_fechas
from ego_audit.datos.descarga import descargar_historico


def _df(fechas: list[str], valor_base: float) -> pd.DataFrame:
    idx = pd.to_datetime(fechas)
    return pd.DataFrame({"Close": [valor_base + i for i in range(len(idx))]}, index=idx)


def test_recorta_a_la_interseccion_de_fechas():
    series = {
        "A": _df(["2024-01-02", "2024-01-03", "2024-01-04"], 1.0),
        "B": _df(["2024-01-02", "2024-01-04"], 2.0),
    }
    alineado = alinear_fechas(series)

    assert list(alineado["A"].index.strftime("%Y-%m-%d")) == ["2024-01-02", "2024-01-04"]
    assert list(alineado["B"].index.strftime("%Y-%m-%d")) == ["2024-01-02", "2024-01-04"]


def test_no_rellena_huecos_solo_descarta():
    series = {
        "A": _df(["2024-01-02", "2024-01-03"], 1.0),
        "B": _df(["2024-01-02"], 2.0),
    }
    alineado = alinear_fechas(series)

    assert len(alineado["A"]) == 1
    assert not alineado["A"].isna().any().any()


def test_diccionario_vacio_devuelve_vacio():
    assert alinear_fechas({}) == {}


def test_todas_las_fechas_iguales_no_pierde_filas():
    fechas = ["2024-01-02", "2024-01-03", "2024-01-04"]
    series = {"A": _df(fechas, 1.0), "B": _df(fechas, 2.0), "C": _df(fechas, 3.0)}
    alineado = alinear_fechas(series)

    assert len(alineado["A"]) == len(alineado["B"]) == len(alineado["C"]) == 3


@pytest.mark.slow
def test_alinea_dos_tickers_reales():
    spy = descargar_historico("SPY", "2024-01-01", "2024-02-01")
    aapl = descargar_historico("AAPL", "2024-01-01", "2024-02-01")

    alineado = alinear_fechas({"SPY": spy, "AAPL": aapl})

    assert len(alineado["SPY"]) == len(alineado["AAPL"])
    assert alineado["SPY"].index.equals(alineado["AAPL"].index)
    assert len(alineado["SPY"]) > 15
