"""datos-04: alinea fechas entre varios tickers (festivos / missing data)."""

import pandas as pd


def alinear_fechas(series_por_ticker: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Recorta todos los DataFrames a las fechas presentes en TODOS los tickers
    (interseccion de indices).

    No se rellenan huecos (ffill/bfill): inventar un precio donde no hay dato
    real seria deshonesto para una herramienta que audita honestidad ajena.
    Si un ticker no cotizo un dia que otro si, esa fecha se descarta para todos.
    """
    if not series_por_ticker:
        return {}

    dfs = list(series_por_ticker.values())
    fechas_comunes = dfs[0].index
    for df in dfs[1:]:
        fechas_comunes = fechas_comunes.intersection(df.index)
    fechas_comunes = fechas_comunes.sort_values()

    return {ticker: df.loc[fechas_comunes] for ticker, df in series_por_ticker.items()}
