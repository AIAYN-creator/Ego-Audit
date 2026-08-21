"""datos-01: descarga de historico diario OHLCV via yfinance."""

import pandas as pd
import yfinance as yf

COLUMNAS_OHLCV = ["Open", "High", "Low", "Close", "Volume"]


def descargar_historico(ticker: str, start: str, end: str) -> pd.DataFrame:
    """Descarga historico diario OHLCV de un ticker entre start y end (YYYY-MM-DD).

    Devuelve un DataFrame con DatetimeIndex diario y exactamente las columnas
    Open, High, Low, Close, Volume, en ese orden -- la forma que espera
    estrategia(datos) segun arq-02-contrato-estrategia.

    auto_adjust=True a proposito (explicito, no depende del default de la
    version de yfinance instalada): Open/High/Low/Close quedan ajustados por
    splits y dividendos, para que un split no aparezca como una caida de
    precio falsa y las rentabilidades calculadas mas adelante sean reales.
    """
    datos = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)

    if datos.empty:
        raise ValueError(f"yfinance no devolvio datos para '{ticker}' entre {start} y {end}")

    if isinstance(datos.columns, pd.MultiIndex):
        datos.columns = datos.columns.get_level_values(0)

    return datos[COLUMNAS_OHLCV]
