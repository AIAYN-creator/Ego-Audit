"""output-01: serie buy-and-hold del benchmark en el periodo evaluado."""

import ego_audit_engine
import pandas as pd


def buy_and_hold(precios: pd.Series) -> pd.Series:
    """Valor de portfolio (base 1.0) de comprar al primer precio de la serie
    y mantener sin operar mas, sobre el mismo indice que `precios`.

    Reutiliza el motor Rust de wf-motor-rust-pyo3 con posicion constante en
    1.0, en vez de reimplementar la contabilidad de otra forma -- el rezago
    de un dia del motor no penaliza aqui: con posicion siempre en 1.0, cada
    transicion participa del retorno completo desde el primer dia.

    Quien llama es responsable de pasar `precios` ya recortado al mismo
    periodo out-of-sample que el valor bruto/neto de la estrategia
    (costes-03-aplicar-bruto-a-neto) -- comparar contra un rango de fechas
    distinto no seria un benchmark justo.
    """
    posiciones = [1.0] * len(precios)
    valor = ego_audit_engine.calcular_valor_portfolio(precios.tolist(), posiciones)
    return pd.Series(valor, index=precios.index, name="buy_and_hold")
