import pandas as pd
import pytest

from ego_audit.datos.descarga import descargar_historico
from ego_audit.walkforward.ventanas import generar_ventanas


def _fechas(n: int) -> pd.DatetimeIndex:
    return pd.date_range("2024-01-01", periods=n, freq="D")


def test_genera_el_numero_esperado_de_ventanas():
    # 10 fechas, ajuste=4, validacion=2 (total=6), paso=2 -> caben en 0..6, 2..8
    ventanas = generar_ventanas(_fechas(10), dias_ajuste=4, dias_validacion=2, paso=2)
    assert len(ventanas) == 3


def test_validacion_empieza_justo_donde_termina_el_ajuste():
    ventanas = generar_ventanas(_fechas(10), dias_ajuste=4, dias_validacion=2, paso=2)
    primera = ventanas[0]
    assert primera.ajuste[-1] < primera.validacion[0]
    assert len(primera.ajuste) == 4
    assert len(primera.validacion) == 2


def test_paso_controla_el_desplazamiento_entre_ventanas():
    ventanas = generar_ventanas(_fechas(10), dias_ajuste=4, dias_validacion=2, paso=1)
    assert ventanas[0].ajuste[0] == ventanas[1].ajuste[0] - pd.Timedelta(days=1)


def test_sin_datos_suficientes_devuelve_lista_vacia():
    assert generar_ventanas(_fechas(3), dias_ajuste=4, dias_validacion=2, paso=1) == []


@pytest.mark.parametrize("dias_ajuste,dias_validacion,paso", [(0, 2, 1), (4, 0, 1), (4, 2, 0)])
def test_parametros_invalidos_lanzan_valueerror(dias_ajuste, dias_validacion, paso):
    with pytest.raises(ValueError):
        generar_ventanas(_fechas(10), dias_ajuste, dias_validacion, paso)


@pytest.mark.slow
def test_ventanas_sobre_datos_reales_de_spy():
    datos = descargar_historico("SPY", "2024-01-01", "2024-06-01")
    ventanas = generar_ventanas(datos.index, dias_ajuste=40, dias_validacion=10, paso=10)

    assert len(ventanas) > 0
    for v in ventanas:
        assert v.ajuste[-1] < v.validacion[0]
        assert len(v.ajuste) == 40
        assert len(v.validacion) == 10
