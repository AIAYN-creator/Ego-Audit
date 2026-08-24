"""costes-03: aplica comisiones y slippage sobre la serie agregada, de bruto a neto."""

import pandas as pd

from ego_audit.costes.comisiones import coste_comisiones
from ego_audit.costes.slippage import coste_slippage


def aplicar_costes(
    valor_bruto: pd.Series,
    posiciones: pd.Series,
    tasa_comision: float | None = None,
    tasa_slippage: float | None = None,
) -> pd.Series:
    """Aplica comisiones + slippage sobre valor_bruto (de wf-03-agregacion-resultados)
    segun los cambios de `posiciones` (la serie de señales concatenada que ya
    se le paso al motor Rust en wf-03), y devuelve el valor de portfolio NETO.

    Los costes se descuentan del RETORNO diario, no del valor absoluto:
        valor_neto[t] = valor_neto[t-1] * (1 + retorno_bruto[t] - coste[t])

    El primer dia cuenta como un "cambio" desde flat (0.0) hasta posiciones[0]:
    entrar en una posicion cuesta algo aunque el motor Rust no le asigne
    retorno bruto al dia 0 (no hay precio anterior con el que compararlo) --
    por eso valor_neto[0] puede quedar por debajo de 1.0 aunque
    valor_bruto[0] sea exactamente 1.0. Es el comportamiento correcto, no
    un bug: se paga por entrar antes de que el precio se haya movido.
    """
    if not valor_bruto.index.equals(posiciones.index):
        raise ValueError("valor_bruto y posiciones deben tener el mismo indice")

    cambios = posiciones.diff()
    cambios.iloc[0] = posiciones.iloc[0]

    kwargs_comision = {} if tasa_comision is None else {"tasa": tasa_comision}
    kwargs_slippage = {} if tasa_slippage is None else {"tasa": tasa_slippage}
    costes = coste_comisiones(cambios, **kwargs_comision) + coste_slippage(
        cambios, **kwargs_slippage
    )

    retorno_bruto = valor_bruto.pct_change().fillna(0.0)
    retorno_neto = retorno_bruto - costes
    return (1 + retorno_neto).cumprod()
