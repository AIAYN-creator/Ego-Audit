import subprocess
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

from ego_audit.sandbox.wrapper import run_strategy_in_sandbox


def _fake_datos() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Open": [1.0, 2.0],
            "High": [1.5, 2.5],
            "Low": [0.5, 1.5],
            "Close": [1.2, 2.2],
            "Volume": [100, 200],
        },
        index=pd.to_datetime(["2024-01-01", "2024-01-02"]),
    )


def _work_dir_from_args(args: list[str]) -> Path:
    mount = next(a for a in args if a.startswith("type=bind"))
    source = next(p for p in mount.split(",") if p.startswith("source="))
    return Path(source.removeprefix("source="))


@pytest.fixture
def estrategia_path(tmp_path):
    path = tmp_path / "estrategia_usuario.py"
    path.write_text("def estrategia(datos):\n    pass\n")
    return path


def test_inyecta_datos_y_scripts_y_lee_senales_de_vuelta(estrategia_path):
    def fake_docker_run(args, capture_output, text, timeout=None):
        work_dir = _work_dir_from_args(args)
        assert (work_dir / "datos.csv").exists()
        assert (work_dir / "estrategia_usuario.py").exists()
        assert (work_dir / "runner.py").exists()
        pd.DataFrame({"senal": [0.0, 1.0]}, index=_fake_datos().index).to_csv(
            work_dir / "senales.csv"
        )
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")

    with patch("ego_audit.sandbox.wrapper.subprocess.run", side_effect=fake_docker_run):
        senales = run_strategy_in_sandbox(_fake_datos(), estrategia_path)

    assert list(senales) == [0.0, 1.0]


def test_borra_el_directorio_de_trabajo_al_terminar(estrategia_path):
    seen_work_dir = {}

    def fake_docker_run(args, capture_output, text, timeout=None):
        work_dir = _work_dir_from_args(args)
        seen_work_dir["path"] = work_dir
        pd.DataFrame({"senal": [0.0]}, index=[_fake_datos().index[0]]).to_csv(
            work_dir / "senales.csv"
        )
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")

    with patch("ego_audit.sandbox.wrapper.subprocess.run", side_effect=fake_docker_run):
        run_strategy_in_sandbox(_fake_datos(), estrategia_path)

    assert not seen_work_dir["path"].exists()


def test_docker_no_instalado_da_mensaje_claro_no_traceback_crudo(estrategia_path):
    with patch(
        "ego_audit.sandbox.wrapper.subprocess.run",
        side_effect=FileNotFoundError("El sistema no puede encontrar el archivo especificado"),
    ):
        with pytest.raises(RuntimeError, match="Docker Desktop"):
            run_strategy_in_sandbox(_fake_datos(), estrategia_path)


def test_lanza_error_si_docker_termina_con_codigo_no_cero(estrategia_path):
    def fake_docker_run(args, capture_output, text, timeout=None):
        return subprocess.CompletedProcess(args=args, returncode=1, stdout="", stderr="boom")

    with patch("ego_audit.sandbox.wrapper.subprocess.run", side_effect=fake_docker_run):
        with pytest.raises(RuntimeError, match="boom"):
            run_strategy_in_sandbox(_fake_datos(), estrategia_path)


def test_lanza_error_si_no_se_produce_senales_csv(estrategia_path):
    def fake_docker_run(args, capture_output, text, timeout=None):
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")

    with patch("ego_audit.sandbox.wrapper.subprocess.run", side_effect=fake_docker_run):
        with pytest.raises(RuntimeError, match="senales.csv"):
            run_strategy_in_sandbox(_fake_datos(), estrategia_path)


def test_mata_el_contenedor_por_nombre_y_lanza_timeouterror_si_no_termina(estrategia_path):
    stopped = {}

    def fake_docker_run(args, capture_output, text, timeout=None):
        if args[1] == "stop":
            stopped["name"] = args[2]
            return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")
        raise subprocess.TimeoutExpired(cmd=args, timeout=timeout)

    with patch("ego_audit.sandbox.wrapper.subprocess.run", side_effect=fake_docker_run):
        with pytest.raises(TimeoutError):
            run_strategy_in_sandbox(_fake_datos(), estrategia_path, timeout_seconds=1)

    assert stopped["name"].startswith("ego-audit-sandbox-")


def test_no_intenta_matar_nada_si_termina_a_tiempo(estrategia_path):
    calls = []

    def fake_docker_run(args, capture_output, text, timeout=None):
        calls.append(args)
        pd.DataFrame({"senal": [0.0]}, index=[_fake_datos().index[0]]).to_csv(
            _work_dir_from_args(args) / "senales.csv"
        )
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")

    with patch("ego_audit.sandbox.wrapper.subprocess.run", side_effect=fake_docker_run):
        run_strategy_in_sandbox(_fake_datos(), estrategia_path)

    assert len(calls) == 1
