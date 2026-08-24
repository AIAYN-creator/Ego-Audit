"""wf-03: agrega los resultados out-of-sample de todas las ventanas en una serie continua."""

import ego_audit_engine
import pandas as pd


def agregar_resultados(datos: pd.DataFrame, resultados_por_ventana: list[pd.Series]) -> pd.Series:
    """Concatena las senales de validacion de todas las ventanas (wf-02) en
    una unica serie continua, y calcula el valor de portfolio BRUTO
    resultante (sin comisiones ni slippage -- eso es epic-costes) via el
    motor Rust de wf-motor-rust-pyo3.

    Si el paso entre ventanas es mayor que la validacion, puede haber huecos
    de fechas sin cubrir: el retorno del primer dia tras un hueco se calcula
    igualmente contra el ultimo precio conocido, no se inventa nada para
    los dias saltados -- coherente con datos-04-alineacion-fechas (no rellenar).
    """
    if not resultados_por_ventana:
        raise ValueError("no hay resultados de ninguna ventana que agregar")

    senales = pd.concat(resultados_por_ventana).sort_index()
    if senales.index.duplicated().any():
        raise ValueError(
            "ventanas de validacion solapadas: hay fechas repetidas "
            "(paso menor que dias_validacion en wf-01-motor-ventanas)"
        )

    precios = datos.loc[senales.index, "Close"]
    valor = ego_audit_engine.calcular_valor_portfolio(precios.tolist(), senales.tolist())
    return pd.Series(valor, index=senales.index, name="valor_portfolio_bruto")
