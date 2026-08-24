"""cli-02: comando `ego-audit run`."""

import argparse
import sys
from pathlib import Path

from ego_audit.costes.comisiones import COMISION_DEFAULT
from ego_audit.costes.slippage import SLIPPAGE_DEFAULT
from ego_audit.datos.universo import BENCHMARK
from ego_audit.pipeline import auditar_estrategia


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ego-audit",
        description=(
            "Audita una estrategia de trading: walk-forward validation, "
            "costes reales, comparado contra buy-and-hold."
        ),
    )
    subparsers = parser.add_subparsers(dest="comando", required=True)

    run = subparsers.add_parser("run", help="Audita una estrategia y genera el reporte HTML")
    run.add_argument(
        "estrategia", type=Path, help="Ruta al .py con la funcion estrategia(datos) -> señales"
    )
    run.add_argument("--ticker", required=True, help="Ticker a auditar (p.ej. AAPL)")
    run.add_argument("--start", required=True, help="Fecha de inicio, YYYY-MM-DD")
    run.add_argument("--end", required=True, help="Fecha de fin, YYYY-MM-DD")
    run.add_argument("--dias-ajuste", type=int, default=60, help="Dias de lookback por ventana")
    run.add_argument("--dias-validacion", type=int, default=20, help="Dias out-of-sample por ventana")
    run.add_argument("--paso", type=int, default=20, help="Desplazamiento entre ventanas")
    run.add_argument("--tasa-comision", type=float, default=COMISION_DEFAULT)
    run.add_argument("--tasa-slippage", type=float, default=SLIPPAGE_DEFAULT)
    run.add_argument("--benchmark", default=BENCHMARK, help="Ticker de comparacion buy-and-hold")
    run.add_argument(
        "-o", "--output", type=Path, default=Path("reporte.html"), help="Ruta del HTML de salida"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)

    if not args.estrategia.exists():
        print(f"error: no existe el fichero '{args.estrategia}'", file=sys.stderr)
        return 1

    try:
        html = auditar_estrategia(
            ticker=args.ticker,
            estrategia_path=args.estrategia,
            start=args.start,
            end=args.end,
            dias_ajuste=args.dias_ajuste,
            dias_validacion=args.dias_validacion,
            paso=args.paso,
            tasa_comision=args.tasa_comision,
            tasa_slippage=args.tasa_slippage,
            benchmark=args.benchmark,
        )
    except (ValueError, RuntimeError, TimeoutError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    args.output.write_text(html, encoding="utf-8")
    print(f"Reporte generado en {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
