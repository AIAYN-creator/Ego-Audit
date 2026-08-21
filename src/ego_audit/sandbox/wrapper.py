"""sandbox-05: levanta el contenedor efimero, inyecta script y datos, recoge senales, lo destruye.

Sin timeout de wall-clock todavia -- eso es sandbox-06-manejo-errores-timeout.
Sin probar contra un daemon Docker real: los tests mockean subprocess.run.
"""

import shutil
import subprocess
import tempfile
from pathlib import Path

import pandas as pd

from ego_audit.sandbox.config import full_run_args

_CONTAINER_RUNNER = Path(__file__).parent / "container_runner.py"


def run_strategy_in_sandbox(
    datos: pd.DataFrame,
    estrategia_path: Path,
    cpus: float = 1.0,
    memory_mb: int = 512,
) -> pd.Series:
    """Ejecuta la funcion estrategia() de estrategia_path sobre datos, dentro del sandbox."""
    with tempfile.TemporaryDirectory(prefix="ego-audit-") as tmp:
        work_dir = Path(tmp)
        datos.to_csv(work_dir / "datos.csv")
        shutil.copy(estrategia_path, work_dir / "estrategia_usuario.py")
        shutil.copy(_CONTAINER_RUNNER, work_dir / "runner.py")

        args = ["docker"] + full_run_args(str(work_dir), cpus=cpus, memory_mb=memory_mb)
        result = subprocess.run(args, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"El sandbox termino con error:\n{result.stderr}")

        senales_path = work_dir / "senales.csv"
        if not senales_path.exists():
            raise RuntimeError("La estrategia no produjo senales.csv")

        return pd.read_csv(senales_path, index_col=0, parse_dates=True)["senal"]
