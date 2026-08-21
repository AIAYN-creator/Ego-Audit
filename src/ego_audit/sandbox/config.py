"""Argumentos de aislamiento para `docker run`, uno por decisión documentada en arq-03-decision-sandbox.

Sin probar contra un daemon Docker real todavia -- ver sandbox-01-dockerfile-base.
"""

SANDBOX_IMAGE = "ego-audit-sandbox:latest"


def network_args() -> list[str]:
    """sandbox-02: sin red saliente, sin excepciones."""
    return ["--network", "none"]


def resource_limit_args(cpus: float = 1.0, memory_mb: int = 512) -> list[str]:
    """sandbox-03: limites estrictos de CPU, memoria y numero de procesos via cgroups."""
    return [
        "--cpus", str(cpus),
        "--memory", f"{memory_mb}m",
        "--memory-swap", f"{memory_mb}m",
        "--pids-limit", "64",
    ]


def filesystem_args(work_dir_host: str) -> list[str]:
    """sandbox-04: filesystem read-only salvo el directorio de trabajo montado."""
    return [
        "--read-only",
        "--tmpfs", "/tmp:rw,size=64m",
        "--mount", f"type=bind,source={work_dir_host},target=/work",
    ]


def hardening_args() -> list[str]:
    """Capas adicionales de arq-03: usuario no-root fijo y sin capabilities de Linux extra."""
    return [
        "--user", "1000:1000",
        "--cap-drop", "ALL",
        "--security-opt", "no-new-privileges",
    ]


def full_run_args(
    work_dir_host: str,
    entrypoint_script: str = "/work/runner.py",
    cpus: float = 1.0,
    memory_mb: int = 512,
    container_name: str | None = None,
) -> list[str]:
    """Ensambla todas las capas de aislamiento para una invocacion de `docker run`.

    entrypoint_script es la ruta (dentro del contenedor) del script que la imagen
    ejecuta -- sandbox-05 copia runner.py a work_dir_host antes de lanzar esto,
    donde queda montado como /work/runner.py. container_name (sandbox-06) permite
    identificar el contenedor para poder matarlo explicitamente si hay timeout.
    """
    name_args = ["--name", container_name] if container_name else []
    return (
        ["run", "--rm"]
        + name_args
        + network_args()
        + resource_limit_args(cpus=cpus, memory_mb=memory_mb)
        + filesystem_args(work_dir_host)
        + hardening_args()
        + [SANDBOX_IMAGE, entrypoint_script]
    )
