"""wf-01: motor de ventanas deslizantes para walk-forward validation."""

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class Ventana:
    ajuste: pd.DatetimeIndex
    validacion: pd.DatetimeIndex


def generar_ventanas(
    fechas: pd.DatetimeIndex,
    dias_ajuste: int,
    dias_validacion: int,
    paso: int,
) -> list[Ventana]:
    """Genera ventanas deslizantes (ajuste, validacion) sobre fechas.

    Cada ventana: dias_ajuste dias consecutivos de ajuste seguidos
    inmediatamente por dias_validacion dias de validacion (fuera de
    muestra, nunca vistos en el ajuste). La ventana siguiente se desliza
    `paso` dias hacia adelante sobre `fechas`. Si no hay suficientes
    fechas para ni una ventana completa, devuelve una lista vacia.
    """
    if dias_ajuste <= 0 or dias_validacion <= 0:
        raise ValueError("dias_ajuste y dias_validacion deben ser positivos")
    if paso <= 0:
        raise ValueError("paso debe ser positivo, si no nunca avanza")

    fechas = fechas.sort_values()
    total = dias_ajuste + dias_validacion
    ventanas = []
    inicio = 0
    while inicio + total <= len(fechas):
        ajuste = fechas[inicio : inicio + dias_ajuste]
        validacion = fechas[inicio + dias_ajuste : inicio + total]
        ventanas.append(Ventana(ajuste=ajuste, validacion=validacion))
        inicio += paso
    return ventanas
