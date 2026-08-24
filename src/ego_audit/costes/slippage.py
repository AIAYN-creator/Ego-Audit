"""costes-02: modelo de slippage estimado."""

import pandas as pd

SLIPPAGE_DEFAULT = 0.0005
"""5 puntos basicos por operacion -- estimacion fija y conservadora para
tickers liquidos como los del universo de v1 (datos-02-universo-tickers).
No escala con volumen ni volatilidad en v1: modelar slippage dependiente
del tamano de orden exigiria saber el tamano real de la cuenta del
usuario, que esta herramienta no conoce ni le pide -- se deja como
limitacion explicita, no como omision accidental."""


def coste_slippage(cambios_posicion: pd.Series, tasa: float = SLIPPAGE_DEFAULT) -> pd.Series:
    """Coste de slippage estimado por dia, proporcional al valor absoluto
    del cambio de posicion (fraccion de capital).
    """
    if tasa < 0:
        raise ValueError("tasa de slippage no puede ser negativa")
    return cambios_posicion.abs() * tasa
