from unittest.mock import patch

import pandas as pd
import pytest

from ego_audit.datos.descarga import descargar_historico
from ego_audit.output.benchmark import buy_and_hold
from ego_audit.output.desglose import desglose_bruto_neto
from ego_audit.output.reporte import generar_reporte_html
from ego_audit.walkforward.agregacion import agregar_resultados
from ego_audit.walkforward.orquestacion import ejecutar_por_ventana
from ego_audit.walkforward.ventanas import generar_ventanas


def _desglose() -> pd.DataFrame:
    idx = pd.date_range("2024-01-01", periods=3)
    return pd.DataFrame(
        {
            "bruto": [1.0, 1.05, 1.1],
            "tras_comisiones": [1.0, 1.04, 1.08],
            "neto": [1.0, 1.03, 1.06],
            "buy_and_hold": [1.0, 1.02, 1.04],
        },
        index=idx,
    )


def test_devuelve_html_bien_formado():
    html = generar_reporte_html(_desglose(), titulo="Test")

    assert html.startswith("<!DOCTYPE html>")
    assert "<title>Test</title>" in html
    assert "</html>" in html


def test_incluye_la_imagen_embebida_en_base64():
    html = generar_reporte_html(_desglose())
    assert 'src="data:image/png;base64,' in html


def test_incluye_los_valores_finales():
    html = generar_reporte_html(_desglose())
    assert "1.1000" in html  # bruto final
    assert "1.0600" in html  # neto final
    assert "1.0400" in html  # buy_and_hold final


def test_columnas_faltantes_lanza_error():
    incompleto = _desglose().drop(columns=["neto"])
    with pytest.raises(ValueError, match="columnas"):
        generar_reporte_html(incompleto)


@pytest.mark.slow
def test_reporte_completo_con_pipeline_real(tmp_path):
    datos = descargar_historico("SPY", "2024-01-01", "2024-06-01")
    ventanas = generar_ventanas(datos.index, dias_ajuste=40, dias_validacion=10, paso=10)

    def estrategia_comprar_y_mantener(datos_ventana, _path):
        return pd.Series(1.0, index=datos_ventana.index)

    with patch(
        "ego_audit.walkforward.orquestacion.run_strategy_in_sandbox",
        side_effect=estrategia_comprar_y_mantener,
    ):
        resultados = ejecutar_por_ventana(datos, ventanas, estrategia_path="ignorado")

    valor_bruto = agregar_resultados(datos, resultados)
    posiciones = pd.concat(resultados).sort_index()
    benchmark = buy_and_hold(datos.loc[valor_bruto.index, "Close"])
    desglose = desglose_bruto_neto(valor_bruto, posiciones, benchmark)

    html = generar_reporte_html(desglose, titulo="SPY buy-and-hold (demo)")

    destino = tmp_path / "reporte.html"
    destino.write_text(html, encoding="utf-8")
    assert destino.stat().st_size > 10_000  # la imagen embebida pesa bastante mas que el html solo
