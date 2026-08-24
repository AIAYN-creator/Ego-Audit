from unittest.mock import patch

import pandas as pd
import pytest

from ego_audit.datos.descarga import descargar_historico
from ego_audit.walkforward.agregacion import agregar_resultados
from ego_audit.walkforward.orquestacion import ejecutar_por_ventana
from ego_audit.walkforward.ventanas import generar_ventanas


def _datos(precios: list[float]) -> pd.DataFrame:
    idx = pd.date_range("2024-01-01", periods=len(precios), freq="D")
    return pd.DataFrame({"Close": precios}, index=idx)


def test_concatena_ventanas_y_calcula_valor_via_motor_rust():
    datos = _datos([100.0, 110.0, 121.0, 133.1])
    resultados = [
        pd.Series([0.0, 1.0], index=datos.index[0:2]),
        pd.Series([1.0, 1.0], index=datos.index[2:4]),
    ]

    valor = agregar_resultados(datos, resultados)

    assert list(valor.index) == list(datos.index)
    assert valor.iloc[-1] > 1.0


def test_ventanas_solapadas_lanza_error():
    datos = _datos([100.0, 110.0, 121.0])
    resultados = [
        pd.Series([1.0, 1.0], index=datos.index[0:2]),
        pd.Series([1.0], index=datos.index[1:2]),  # fecha repetida
    ]

    with pytest.raises(ValueError, match="solapadas"):
        agregar_resultados(datos, resultados)


def test_sin_resultados_lanza_error():
    with pytest.raises(ValueError, match="no hay resultados"):
        agregar_resultados(_datos([100.0]), [])


def test_portfolio_siempre_flat_no_cambia_de_valor():
    datos = _datos([100.0, 105.0, 95.0, 120.0])
    resultados = [pd.Series([0.0] * 4, index=datos.index)]

    valor = agregar_resultados(datos, resultados)

    assert (valor == 1.0).all()


@pytest.mark.slow
def test_pipeline_completo_con_datos_reales_y_motor_real():
    """Sin mockear nada salvo el sandbox (no hay Docker): datos reales de
    SPY, ventanas reales, y el motor Rust real calculando el valor."""
    datos = descargar_historico("SPY", "2024-01-01", "2024-06-01")
    ventanas = generar_ventanas(datos.index, dias_ajuste=40, dias_validacion=10, paso=10)
    assert len(ventanas) > 0

    def estrategia_comprar_y_mantener(datos_ventana, _path):
        return pd.Series(1.0, index=datos_ventana.index)

    with patch(
        "ego_audit.walkforward.orquestacion.run_strategy_in_sandbox",
        side_effect=estrategia_comprar_y_mantener,
    ):
        resultados = ejecutar_por_ventana(datos, ventanas, estrategia_path="ignorado")

    valor = agregar_resultados(datos, resultados)

    assert len(valor) > 0
    assert valor.iloc[0] == pytest.approx(1.0)
    assert not valor.isna().any()
