"""costes-01: modelo de comisiones."""

import pandas as pd

COMISION_DEFAULT = 0.001
"""10 puntos basicos por operacion -- valor conservador tipico de broker
retail, incluso con brokers "sin comision" hay letra pequena (spread,
payment for order flow, etc.). Configurable, no forzado a 0 por defecto:
un default de 0 haria que la herramienta subestimara friccion a menos
que el usuario recuerde configurarlo, justo el sesgo que existe para
exponer."""


def coste_comisiones(cambios_posicion: pd.Series, tasa: float = COMISION_DEFAULT) -> pd.Series:
    """Coste de comision por dia, proporcional al valor absoluto del cambio
    de posicion (fraccion de capital). No distingue compra de venta -- ambas
    cuestan lo mismo, como en la mayoria de brokers modernos.
    """
    if tasa < 0:
        raise ValueError("tasa de comision no puede ser negativa")
    return cambios_posicion.abs() * tasa
