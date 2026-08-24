"""cli-01: funcion de libreria que encadena datos -> sandbox -> walk-forward -> costes -> output."""

from pathlib import Path

import pandas as pd

from ego_audit.costes.comisiones import COMISION_DEFAULT
from ego_audit.costes.slippage import SLIPPAGE_DEFAULT
from ego_audit.datos.cache import obtener_historico
from ego_audit.datos.universo import BENCHMARK
from ego_audit.output.benchmark import buy_and_hold
from ego_audit.output.desglose import desglose_bruto_neto
from ego_audit.output.reporte import generar_reporte_html
from ego_audit.walkforward.agregacion import agregar_resultados
from ego_audit.walkforward.orquestacion import ejecutar_por_ventana
from ego_audit.walkforward.ventanas import generar_ventanas


def auditar_estrategia(
    ticker: str,
    estrategia_path: Path,
    start: str,
    end: str,
    dias_ajuste: int = 60,
    dias_validacion: int = 20,
    paso: int = 20,
    tasa_comision: float = COMISION_DEFAULT,
    tasa_slippage: float = SLIPPAGE_DEFAULT,
    benchmark: str = BENCHMARK,
) -> str:
    """Ejecuta el pipeline completo -- descarga con cache, walk-forward en
    el sandbox, agregacion, costes, comparacion contra buy-and-hold del
    benchmark -- y devuelve el reporte HTML final como string.

    Encadena, en orden, todo lo ya construido en las epics anteriores:
    epic-datos -> epic-sandbox (via epic-walkforward) -> epic-costes ->
    epic-output. No introduce logica nueva, solo cablea lo existente.
    """
    datos = obtener_historico(ticker, start, end)
    ventanas = generar_ventanas(datos.index, dias_ajuste, dias_validacion, paso)
    if not ventanas:
        raise ValueError(
            f"no hay suficientes datos entre {start} y {end} para ni una ventana "
            f"de {dias_ajuste}+{dias_validacion} dias -- prueba un rango mas largo"
        )

    resultados = ejecutar_por_ventana(datos, ventanas, estrategia_path)
    valor_bruto = agregar_resultados(datos, resultados)
    posiciones = pd.concat(resultados).sort_index()

    datos_benchmark = obtener_historico(benchmark, start, end)
    valor_benchmark = buy_and_hold(datos_benchmark.loc[valor_bruto.index, "Close"])

    desglose = desglose_bruto_neto(
        valor_bruto, posiciones, valor_benchmark, tasa_comision, tasa_slippage
    )
    return generar_reporte_html(desglose, titulo=f"Ego Audit — {ticker}")
