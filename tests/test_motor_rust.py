"""wf-motor-rust-pyo3: prueba el motor compilado de verdad.

Se salta entero si el modulo `ego_audit_engine` no esta compilado -- no hay
toolchain de Rust en esta maquina de desarrollo. En cuanto se instale Rust
y se corra `maturin develop` dentro de engine/, este test corre de verdad.
"""

import pytest

ego_audit_engine = pytest.importorskip("ego_audit_engine")


def test_portfolio_flat_no_cambia_de_valor():
    valor = ego_audit_engine.calcular_valor_portfolio([100.0, 105.0, 110.0], [0.0, 0.0, 0.0])
    assert valor == pytest.approx([1.0, 1.0, 1.0])


def test_posicion_se_aplica_con_un_dia_de_rezago():
    # sube 10% el dia 1->2 estando flat el dia 1 (no cuenta);
    # sube 10% otra vez el dia 2->3 estando ya long desde el dia 2 (si cuenta).
    valor = ego_audit_engine.calcular_valor_portfolio(
        [100.0, 110.0, 121.0], [0.0, 1.0, 1.0]
    )
    assert valor[1] == pytest.approx(1.0)  # posicion del dia 0 (flat) manda el dia 1
    assert valor[2] == pytest.approx(1.1)  # posicion del dia 1 (long) manda el dia 2


def test_long_completo_replica_el_retorno_del_precio():
    valor = ego_audit_engine.calcular_valor_portfolio([100.0, 110.0, 121.0], [1.0, 1.0, 1.0])
    assert valor[-1] == pytest.approx(1.21, rel=1e-9)


def test_longitudes_distintas_lanza_error():
    with pytest.raises(ValueError):
        ego_audit_engine.calcular_valor_portfolio([100.0, 105.0], [0.0])


def test_series_vacia_devuelve_vacia():
    assert ego_audit_engine.calcular_valor_portfolio([], []) == []
