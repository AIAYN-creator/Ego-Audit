"""wf-02: por cada ventana, ejecuta la estrategia en el sandbox y recoge resultados."""

from pathlib import Path

import pandas as pd

from ego_audit.sandbox.wrapper import run_strategy_in_sandbox
from ego_audit.walkforward.ventanas import Ventana


def ejecutar_por_ventana(
    datos: pd.DataFrame,
    ventanas: list[Ventana],
    estrategia_path: Path,
) -> list[pd.Series]:
    """Para cada ventana, ejecuta estrategia_path sobre datos[ajuste+validacion]
    dentro del sandbox, y devuelve solo las senales del periodo de validacion
    (fuera de muestra) de cada ventana.

    El periodo de ajuste se le pasa a la estrategia junto con el de validacion
    porque el contrato estrategia(datos) -> senales (arq-02-contrato-estrategia)
    no separa "ajustar" de "predecir": es una unica funcion que puede mirar
    hacia atras dentro de `datos` para calcular sus propios indicadores. El
    ajuste es solo el contexto/lookback que necesita para eso -- no se puntua,
    por eso se descarta antes de devolver el resultado de la ventana.
    """
    resultados = []
    for ventana in ventanas:
        fechas_ventana = ventana.ajuste.union(ventana.validacion)
        datos_ventana = datos.loc[fechas_ventana]
        senales = run_strategy_in_sandbox(datos_ventana, estrategia_path)
        resultados.append(senales.loc[ventana.validacion])
    return resultados
