import pandas as pd
import pytest

from ego_audit.costes.comisiones import COMISION_DEFAULT, coste_comisiones


def _cambios(valores: list[float]) -> pd.Series:
    return pd.Series(valores, index=pd.date_range("2024-01-01", periods=len(valores)))


def test_sin_cambio_de_posicion_no_hay_coste():
    assert (coste_comisiones(_cambios([0.0, 0.0, 0.0])) == 0.0).all()


def test_coste_proporcional_al_valor_absoluto_del_cambio():
    costes = coste_comisiones(_cambios([1.0, -1.0, 0.5]), tasa=0.01)
    assert list(costes) == pytest.approx([0.01, 0.01, 0.005])


def test_compra_y_venta_cuestan_lo_mismo():
    costes = coste_comisiones(_cambios([1.0, -1.0]), tasa=0.01)
    assert costes.iloc[0] == costes.iloc[1]


def test_usa_el_default_si_no_se_especifica_tasa():
    costes = coste_comisiones(_cambios([1.0]))
    assert costes.iloc[0] == pytest.approx(COMISION_DEFAULT)


def test_tasa_negativa_lanza_error():
    with pytest.raises(ValueError):
        coste_comisiones(_cambios([1.0]), tasa=-0.01)
