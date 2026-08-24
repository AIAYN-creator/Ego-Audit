from unittest.mock import patch

import pandas as pd
import pytest

from ego_audit.datos.descarga import descargar_historico
from ego_audit.output.benchmark import buy_and_hold
from ego_audit.output.desglose import desglose_bruto_neto
from ego_audit.walkforward.agregacion import agregar_resultados
from ego_audit.walkforward.orquestacion import ejecutar_por_ventana
from ego_audit.walkforward.ventanas import generar_ventanas


def _serie(valores: list[float]) -> pd.Series:
    return pd.Series(valores, index=pd.date_range("2024-01-01", periods=len(valores)))


def test_columnas_esperadas():
    bruto = _serie([1.0, 1.0])
    df = desglose_bruto_neto(bruto, _serie([0.0, 0.0]), bruto)

    assert list(df.columns) == ["bruto", "tras_comisiones", "neto", "buy_and_hold"]


def test_sin_operaciones_las_cuatro_columnas_coinciden():
    bruto = _serie([1.0, 1.05, 1.1])
    df = desglose_bruto_neto(bruto, _serie([0.0, 0.0, 0.0]), bruto)

    assert (df["bruto"] == df["tras_comisiones"]).all()
    assert (df["tras_comisiones"] == df["neto"]).all()


def test_con_operaciones_bruto_mayor_o_igual_que_tras_comisiones_mayor_o_igual_que_neto():
    bruto = _serie([1.0, 1.0, 1.0, 1.0])
    posiciones = _serie([1.0, -1.0, 1.0, -1.0])  # rota cada dia

    df = desglose_bruto_neto(
        bruto, posiciones, bruto, tasa_comision=0.01, tasa_slippage=0.005
    )

    assert (df["bruto"] >= df["tras_comisiones"]).all()
    assert (df["tras_comisiones"] >= df["neto"]).all()


def test_indices_no_coincidentes_lanza_error():
    bruto = _serie([1.0, 1.0])
    otro_indice = pd.Series([1.0, 1.0], index=pd.date_range("2025-01-01", periods=2))

    with pytest.raises(ValueError, match="mismo indice"):
        desglose_bruto_neto(bruto, bruto, otro_indice)


@pytest.mark.slow
def test_desglose_completo_con_datos_reales():
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

    df = desglose_bruto_neto(valor_bruto, posiciones, benchmark)

    assert len(df) == len(valor_bruto)
    assert not df.isna().any().any()
