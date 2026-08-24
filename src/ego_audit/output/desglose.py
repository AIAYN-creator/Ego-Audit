"""output-02: desglose bruto -> comisiones -> slippage -> neto, comparado contra el benchmark."""

import pandas as pd

from ego_audit.costes.neto import aplicar_costes


def desglose_bruto_neto(
    valor_bruto: pd.Series,
    posiciones: pd.Series,
    valor_buy_and_hold: pd.Series,
    tasa_comision: float | None = None,
    tasa_slippage: float | None = None,
) -> pd.DataFrame:
    """Construye el desglose bruto -> tras comisiones -> neto (comisiones +
    slippage), comparado contra buy-and-hold del benchmark ([[output-01]]).

    "tras comisiones" no es un calculo nuevo: se obtiene llamando a
    aplicar_costes (costes-03-aplicar-bruto-a-neto) con slippage forzado a
    cero, reutilizando la misma funcion en vez de reimplementar un paso
    intermedio aparte.
    """
    if not (
        valor_bruto.index.equals(posiciones.index)
        and valor_bruto.index.equals(valor_buy_and_hold.index)
    ):
        raise ValueError(
            "valor_bruto, posiciones y valor_buy_and_hold deben compartir el mismo indice"
        )

    tras_comisiones = aplicar_costes(
        valor_bruto, posiciones, tasa_comision=tasa_comision, tasa_slippage=0.0
    )
    neto = aplicar_costes(
        valor_bruto, posiciones, tasa_comision=tasa_comision, tasa_slippage=tasa_slippage
    )

    return pd.DataFrame(
        {
            "bruto": valor_bruto,
            "tras_comisiones": tras_comisiones,
            "neto": neto,
            "buy_and_hold": valor_buy_and_hold,
        }
    )
