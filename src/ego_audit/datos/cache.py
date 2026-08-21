"""datos-03: cache local de datos descargados, para no repetir llamadas a yfinance."""

from pathlib import Path

import pandas as pd
import platformdirs

from ego_audit.datos.descarga import descargar_historico

CACHE_DIR = Path(platformdirs.user_cache_dir("ego-audit"))


def _cache_path(ticker: str, start: str, end: str) -> Path:
    return CACHE_DIR / f"{ticker}_{start}_{end}.csv"


def obtener_historico(ticker: str, start: str, end: str) -> pd.DataFrame:
    """Como descargar_historico, pero cachea en disco: si ya se pidio antes
    este ticker+rango exacto, lee del cache en vez de volver a llamar a yfinance."""
    path = _cache_path(ticker, start, end)
    if path.exists():
        return pd.read_csv(path, index_col=0, parse_dates=True)

    datos = descargar_historico(ticker, start, end)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    datos.to_csv(path)
    return datos
