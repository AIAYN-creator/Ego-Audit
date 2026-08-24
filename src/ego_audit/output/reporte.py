"""output-03: reporte HTML/imagen estatico con el desglose bruto->neto vs. benchmark."""

import base64
import io

import matplotlib

matplotlib.use("Agg")  # sin backend interactivo -- solo generar la imagen
import matplotlib.pyplot as plt
import pandas as pd

# Paleta validada en estetica-01-paleta-colores (docs/paleta.md) -- no son
# los colores por defecto de matplotlib, ver esa card para el porque.
_ESTILOS = {
    "bruto": {"color": "#2a78d6", "linestyle": "--", "label": "Bruto"},
    "tras_comisiones": {"color": "#1baf7a", "linestyle": ":", "label": "Tras comisiones"},
    "neto": {"color": "#eb6834", "linewidth": 2, "label": "Neto"},
    "buy_and_hold": {"color": "#898781", "linewidth": 2, "label": "Buy & hold"},
}


def _grafico_b64(desglose: pd.DataFrame, titulo: str) -> str:
    fig, ax = plt.subplots(figsize=(10, 6))
    for columna, estilo in _ESTILOS.items():
        ax.plot(desglose.index, desglose[columna], **estilo)

    ax.set_xlabel("Fecha")
    ax.set_ylabel("Valor de portfolio (base 1.0)")
    ax.set_title(titulo)
    ax.legend()
    ax.grid(alpha=0.3)
    fig.autofmt_xdate()

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=120, bbox_inches="tight")
    plt.close(fig)
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def generar_reporte_html(desglose: pd.DataFrame, titulo: str = "Ego Audit") -> str:
    """Genera un reporte HTML autocontenido (imagen embebida en base64, sin
    ficheros externos) con las 4 curvas de output-02-desglose-bruto-neto.
    """
    columnas_esperadas = set(_ESTILOS)
    if not columnas_esperadas.issubset(desglose.columns):
        raise ValueError(f"desglose debe tener las columnas {sorted(columnas_esperadas)}")

    imagen_b64 = _grafico_b64(desglose, titulo)
    valor_final = desglose[["bruto", "neto", "buy_and_hold"]].iloc[-1]

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>{titulo}</title>
</head>
<body>
<h1>{titulo}</h1>
<img src="data:image/png;base64,{imagen_b64}" alt="Desglose bruto a neto vs buy-and-hold">
<table>
<tr><th></th><th>Bruto</th><th>Neto</th><th>Buy &amp; hold</th></tr>
<tr>
<td>Valor final</td>
<td>{valor_final['bruto']:.4f}</td>
<td>{valor_final['neto']:.4f}</td>
<td>{valor_final['buy_and_hold']:.4f}</td>
</tr>
</table>
</body>
</html>
"""
