"""sandbox-05: levanta el contenedor efimero, inyecta script y datos, recoge senales, lo destruye.

sandbox-06: timeout de wall-clock -- si `docker run` no termina a tiempo, se mata
el CONTENEDOR explicitamente (docker stop), no solo el proceso `docker run` del
host, que de otro modo dejaria el contenedor huerfano consumiendo recursos.
"errores de estrategia" (excepciones, I/O prohibido por el propio sandbox) ya
quedan cubiertos por el mismo camino que un docker run con codigo de salida
distinto de cero -- no hace falta un mecanismo aparte para eso.

Sin probar contra un daemon Docker real: los tests mockean subprocess.run.
"""

import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path

import pandas as pd

from ego_audit.sandbox.config import full_run_args

_CONTAINER_RUNNER = Path(__file__).parent / "container_runner.py"

DEFAULT_TIMEOUT_SECONDS = 30


def run_strategy_in_sandbox(
    datos: pd.DataFrame,
    estrategia_path: Path,
    cpus: float = 1.0,
    memory_mb: int = 512,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> pd.Series:
    """Ejecuta la funcion estrategia() de estrategia_path sobre datos, dentro del sandbox."""
    with tempfile.TemporaryDirectory(prefix="ego-audit-") as tmp:
        work_dir = Path(tmp)
        datos.to_csv(work_dir / "datos.csv")
        shutil.copy(estrategia_path, work_dir / "estrategia_usuario.py")
        shutil.copy(_CONTAINER_RUNNER, work_dir / "runner.py")

        container_name = f"ego-audit-sandbox-{uuid.uuid4().hex[:12]}"
        args = ["docker"] + full_run_args(
            str(work_dir), cpus=cpus, memory_mb=memory_mb, container_name=container_name
        )
        try:
            result = subprocess.run(
                args, capture_output=True, text=True, timeout=timeout_seconds
            )
        except FileNotFoundError as e:
            raise RuntimeError(
                "No se encontro el comando 'docker'. Instala Docker Desktop "
                "(https://docs.docker.com/get-docker/) y verifica que 'docker' "
                "este en el PATH antes de auditar una estrategia."
            ) from e
        except subprocess.TimeoutExpired:
            try:
                subprocess.run(
                    ["docker", "stop", container_name],
                    capture_output=True,
                    text=True,
                    timeout=15,
                )
            except subprocess.TimeoutExpired:
                pass
            raise TimeoutError(
                f"La estrategia no termino en {timeout_seconds}s -- "
                f"contenedor {container_name} detenido."
            )

        if result.returncode != 0:
            raise RuntimeError(f"El sandbox termino con error:\n{result.stderr}")

        senales_path = work_dir / "senales.csv"
        if not senales_path.exists():
            raise RuntimeError("La estrategia no produjo senales.csv")

        return pd.read_csv(senales_path, index_col=0, parse_dates=True)["senal"]
