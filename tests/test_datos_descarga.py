from unittest.mock import patch

import pandas as pd
import pytest

from ego_audit.datos.descarga import COLUMNAS_OHLCV, descargar_historico


def _fake_yf_multiindex(ticker: str) -> pd.DataFrame:
    """Misma forma que devuelve yfinance 1.6.0 de verdad para un solo ticker:
    MultiIndex (Price, Ticker), orden de columnas no garantizado (alfabetico)."""
    idx = pd.to_datetime(["2024-01-02", "2024-01-03"])
    columnas = pd.MultiIndex.from_product(
        [["Close", "High", "Low", "Open", "Volume"], [ticker]], names=["Price", "Ticker"]
    )
    return pd.DataFrame(
        [[100.0, 101.0, 99.0, 100.5, 1000], [101.0, 102.0, 100.0, 100.0, 1200]],
        index=idx,
        columns=columnas,
    )


def test_aplana_multiindex_y_reordena_a_ohlcv():
    with patch("ego_audit.datos.descarga.yf.download", return_value=_fake_yf_multiindex("AAPL")):
        datos = descargar_historico("AAPL", "2024-01-01", "2024-01-05")

    assert list(datos.columns) == COLUMNAS_OHLCV
    assert not isinstance(datos.columns, pd.MultiIndex)
    assert len(datos) == 2


def test_pide_auto_adjust_true():
    captured = {}

    def fake_download(*args, **kwargs):
        captured.update(kwargs)
        return _fake_yf_multiindex("AAPL")

    with patch("ego_audit.datos.descarga.yf.download", side_effect=fake_download):
        descargar_historico("AAPL", "2024-01-01", "2024-01-05")

    assert captured["auto_adjust"] is True


def test_lanza_error_si_yfinance_devuelve_vacio():
    with patch("ego_audit.datos.descarga.yf.download", return_value=pd.DataFrame()):
        with pytest.raises(ValueError, match="TICKER_INVENTADO"):
            descargar_historico("TICKER_INVENTADO", "2024-01-01", "2024-01-05")


@pytest.mark.slow
def test_descarga_real_contra_yfinance():
    """Sin mockear -- comprobacion de verdad contra la API real, para detectar
    si yfinance cambia de forma con el tiempo. Requiere red."""
    datos = descargar_historico("SPY", "2024-01-01", "2024-01-15")
    assert list(datos.columns) == COLUMNAS_OHLCV
    assert len(datos) > 0
    assert (datos["High"] >= datos["Low"]).all()
