from unittest.mock import patch

import pandas as pd
import pytest

from ego_audit.walkforward.orquestacion import ejecutar_por_ventana
from ego_audit.walkforward.ventanas import Ventana


def _datos(n: int) -> pd.DataFrame:
    idx = pd.date_range("2024-01-01", periods=n, freq="D")
    return pd.DataFrame({"Close": range(n)}, index=idx)


@pytest.fixture
def estrategia_path(tmp_path):
    path = tmp_path / "estrategia.py"
    path.write_text("def estrategia(datos):\n    pass\n")
    return path


def test_pasa_ajuste_y_validacion_juntos_a_la_estrategia(estrategia_path):
    datos = _datos(10)
    ventana = Ventana(ajuste=datos.index[0:6], validacion=datos.index[6:8])
    visto = {}

    def fake_run(datos_pasados, path):
        visto["n_filas"] = len(datos_pasados)
        visto["path"] = path
        return pd.Series(0.0, index=datos_pasados.index)

    with patch(
        "ego_audit.walkforward.orquestacion.run_strategy_in_sandbox", side_effect=fake_run
    ):
        ejecutar_por_ventana(datos, [ventana], estrategia_path)

    assert visto["n_filas"] == 8  # 6 de ajuste + 2 de validacion
    assert visto["path"] == estrategia_path


def test_solo_devuelve_senales_del_periodo_de_validacion(estrategia_path):
    datos = _datos(10)
    ventana = Ventana(ajuste=datos.index[0:6], validacion=datos.index[6:8])

    with patch(
        "ego_audit.walkforward.orquestacion.run_strategy_in_sandbox",
        side_effect=lambda d, p: pd.Series(1.0, index=d.index),
    ):
        resultados = ejecutar_por_ventana(datos, [ventana], estrategia_path)

    assert list(resultados[0].index) == list(ventana.validacion)
    assert len(resultados[0]) == 2


def test_una_entrada_de_resultado_por_ventana(estrategia_path):
    datos = _datos(20)
    ventanas = [
        Ventana(ajuste=datos.index[0:6], validacion=datos.index[6:8]),
        Ventana(ajuste=datos.index[2:8], validacion=datos.index[8:10]),
    ]

    with patch(
        "ego_audit.walkforward.orquestacion.run_strategy_in_sandbox",
        side_effect=lambda d, p: pd.Series(0.0, index=d.index),
    ):
        resultados = ejecutar_por_ventana(datos, ventanas, estrategia_path)

    assert len(resultados) == 2


def test_propaga_errores_del_sandbox(estrategia_path):
    datos = _datos(10)
    ventana = Ventana(ajuste=datos.index[0:6], validacion=datos.index[6:8])

    with patch(
        "ego_audit.walkforward.orquestacion.run_strategy_in_sandbox",
        side_effect=RuntimeError("boom"),
    ):
        with pytest.raises(RuntimeError, match="boom"):
            ejecutar_por_ventana(datos, [ventana], estrategia_path)
