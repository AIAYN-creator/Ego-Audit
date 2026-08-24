from unittest.mock import patch

import pandas as pd
import pytest

from ego_audit.pipeline import auditar_estrategia


def _datos(n: int) -> pd.DataFrame:
    idx = pd.date_range("2024-01-01", periods=n, freq="D")
    return pd.DataFrame(
        {"Open": 100.0, "High": 101.0, "Low": 99.0, "Close": 100.0, "Volume": 1000}, index=idx
    )


def test_datos_insuficientes_lanza_error_explicito(tmp_path):
    estrategia_path = tmp_path / "estrategia.py"
    estrategia_path.write_text("def estrategia(datos):\n    pass\n")

    with patch("ego_audit.pipeline.obtener_historico", return_value=_datos(5)):
        with pytest.raises(ValueError, match="no hay suficientes datos"):
            auditar_estrategia(
                "AAPL", estrategia_path, "2024-01-01", "2024-01-06",
                dias_ajuste=60, dias_validacion=20, paso=20,
            )


@pytest.mark.slow
def test_pipeline_completo_devuelve_html_valido(tmp_path):
    """Sin mockear datos ni motor -- solo el sandbox, por falta de Docker."""
    estrategia_path = tmp_path / "estrategia.py"
    estrategia_path.write_text(
        "def estrategia(datos):\n"
        "    media = datos['Close'].rolling(20).mean()\n"
        "    return (datos['Close'] > media).astype(float)\n"
    )

    def ejecutar_de_verdad(datos_ventana, path):
        import importlib.util

        spec = importlib.util.spec_from_file_location("estrategia_usuario", path)
        modulo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modulo)
        return modulo.estrategia(datos_ventana)

    with patch(
        "ego_audit.walkforward.orquestacion.run_strategy_in_sandbox",
        side_effect=ejecutar_de_verdad,
    ):
        html = auditar_estrategia(
            "AAPL",
            estrategia_path,
            "2023-01-01",
            "2024-01-01",
            dias_ajuste=60,
            dias_validacion=20,
            paso=20,
        )

    assert html.startswith("<!DOCTYPE html>")
    assert "AAPL" in html
    assert 'src="data:image/png;base64,' in html
