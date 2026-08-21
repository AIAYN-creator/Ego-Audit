"""Se copia a work_dir y se ejecuta DENTRO del contenedor como /work/runner.py.

No se importa nunca desde el paquete -- ver sandbox-05-wrapper-orquestacion,
que lo copia como archivo de texto junto a datos.csv y estrategia_usuario.py.
Sin manejo de errores/timeout aqui a proposito: eso es responsabilidad de
sandbox-06-manejo-errores-timeout, vigilando desde fuera del contenedor.
"""

import sys

import pandas as pd

sys.path.insert(0, "/work")

from estrategia_usuario import estrategia  # noqa: E402

datos = pd.read_csv("/work/datos.csv", index_col=0, parse_dates=True)
senales = estrategia(datos)
senales.to_frame(name="senal").to_csv("/work/senales.csv")
