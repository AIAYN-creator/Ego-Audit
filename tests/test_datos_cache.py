from unittest.mock import patch

import pandas as pd
import pytest

import ego_audit.datos.cache as cache_module
from ego_audit.datos.cache import obtener_historico


def _fake_datos() -> pd.DataFrame:
    return pd.DataFrame(
        {"Open": [1.0], "High": [1.5], "Low": [0.5], "Close": [1.2], "Volume": [100]},
        index=pd.to_datetime(["2024-01-02"]),
    )


@pytest.fixture(autouse=True)
def cache_dir_temporal(tmp_path, monkeypatch):
    monkeypatch.setattr(cache_module, "CACHE_DIR", tmp_path)
    return tmp_path


def test_primera_llamada_descarga_y_guarda_en_cache(cache_dir_temporal):
    with patch(
        "ego_audit.datos.cache.descargar_historico", return_value=_fake_datos()
    ) as mock_descarga:
        datos = obtener_historico("AAPL", "2024-01-01", "2024-01-05")

    mock_descarga.assert_called_once_with("AAPL", "2024-01-01", "2024-01-05")
    assert (cache_dir_temporal / "AAPL_2024-01-01_2024-01-05.csv").exists()
    assert list(datos.columns) == ["Open", "High", "Low", "Close", "Volume"]


def test_segunda_llamada_no_vuelve_a_llamar_a_yfinance(cache_dir_temporal):
    with patch(
        "ego_audit.datos.cache.descargar_historico", return_value=_fake_datos()
    ) as mock_descarga:
        obtener_historico("AAPL", "2024-01-01", "2024-01-05")
        obtener_historico("AAPL", "2024-01-01", "2024-01-05")

    mock_descarga.assert_called_once()


def test_tickers_o_rangos_distintos_no_comparten_cache(cache_dir_temporal):
    with patch(
        "ego_audit.datos.cache.descargar_historico", return_value=_fake_datos()
    ) as mock_descarga:
        obtener_historico("AAPL", "2024-01-01", "2024-01-05")
        obtener_historico("MSFT", "2024-01-01", "2024-01-05")

    assert mock_descarga.call_count == 2


@pytest.mark.slow
def test_roundtrip_real_conserva_forma_y_valores(cache_dir_temporal):
    """Sin mockear -- descarga real una vez, lee la segunda del cache, y
    comprueba que el csv no ha perdido tipos ni precision al hacer roundtrip."""
    primera = obtener_historico("SPY", "2024-01-02", "2024-01-10")
    segunda = obtener_historico("SPY", "2024-01-02", "2024-01-10")

    # Ni el dtype exacto del indice (datetime64[s] en la descarga fresca vs
    # [us] tras el roundtrip por csv) ni la ultima cifra de precision del
    # float (el propio to_csv/read_csv introduce ~1e-14 de ruido de texto)
    # son parte del contrato del cache -- solo que el dato sea el mismo
    # dentro de una tolerancia irrelevante para precios reales.
    assert (primera.values - segunda.values).__abs__().max() < 1e-9
    assert list(primera.index.astype(str)) == list(segunda.index.astype(str))
    assert list(primera.columns) == ["Open", "High", "Low", "Close", "Volume"]
