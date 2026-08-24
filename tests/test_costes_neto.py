from unittest.mock import patch

import pandas as pd
import pytest

from ego_audit.costes.neto import aplicar_costes
from ego_audit.datos.descarga import descargar_historico
from ego_audit.walkforward.agregacion import agregar_resultados
from ego_audit.walkforward.orquestacion import ejecutar_por_ventana
from ego_audit.walkforward.ventanas import generar_ventanas


def _serie(valores: list[float]) -> pd.Series:
    return pd.Series(valores, index=pd.date_range("2024-01-01", periods=len(valores)))


def test_sin_operaciones_neto_igual_a_bruto():
    bruto = _serie([1.0, 1.05, 1.1])
    posiciones = _serie([0.0, 0.0, 0.0])

    neto = aplicar_costes(bruto, posiciones)

    assert list(neto) == pytest.approx(list(bruto))


def test_entrar_en_posicion_el_dia_0_cuesta_aunque_el_bruto_no_se_mueva():
    bruto = _serie([1.0, 1.0])
    posiciones = _serie([1.0, 1.0])  # entra long el dia 0, se queda quieto

    neto = aplicar_costes(bruto, posiciones, tasa_comision=0.01, tasa_slippage=0.0)

    assert bruto.iloc[0] == 1.0
    assert neto.iloc[0] < 1.0


def test_mas_operaciones_mas_coste():
    bruto = _serie([1.0, 1.0, 1.0, 1.0])
    quieto = _serie([1.0, 1.0, 1.0, 1.0])
    rotando = _serie([1.0, -1.0, 1.0, -1.0])

    neto_quieto = aplicar_costes(bruto, quieto, tasa_comision=0.01, tasa_slippage=0.0)
    neto_rotando = aplicar_costes(bruto, rotando, tasa_comision=0.01, tasa_slippage=0.0)

    assert neto_rotando.iloc[-1] < neto_quieto.iloc[-1]


def test_indices_distintos_lanza_error():
    bruto = _serie([1.0, 1.0])
    posiciones = pd.Series([0.0, 0.0], index=pd.date_range("2025-01-01", periods=2))

    with pytest.raises(ValueError, match="mismo indice"):
        aplicar_costes(bruto, posiciones)


@pytest.mark.slow
def test_pipeline_completo_bruto_a_neto_con_datos_reales():
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

    neto = aplicar_costes(valor_bruto, posiciones)

    assert len(neto) == len(valor_bruto)
    assert neto.iloc[-1] <= valor_bruto.iloc[-1]  # los costes nunca ayudan
