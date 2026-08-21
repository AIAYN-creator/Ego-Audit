"""Argumentos de aislamiento para `docker run`, uno por decisión documentada en arq-03-decision-sandbox.

Sin probar contra un daemon Docker real todavia -- ver sandbox-01-dockerfile-base.
"""

SANDBOX_IMAGE = "ego-audit-sandbox:latest"


def runtime_args() -> list[str]:
    """gVisor (runsc) como runtime del contenedor -- arq-03-decision-sandbox."""
    return ["--runtime", "runsc"]


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


def full_run_args(work_dir_host: str, cpus: float = 1.0, memory_mb: int = 512) -> list[str]:
    """Ensambla todas las capas de aislamiento para una invocacion de `docker run`."""
    return (
        ["run", "--rm"]
        + runtime_args()
        + network_args()
        + resource_limit_args(cpus=cpus, memory_mb=memory_mb)
        + filesystem_args(work_dir_host)
        + hardening_args()
        + [SANDBOX_IMAGE]
    )
