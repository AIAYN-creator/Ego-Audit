from unittest.mock import patch

import pytest

from ego_audit.cli import main


def test_fichero_de_estrategia_inexistente_devuelve_1_y_mensaje(tmp_path, capsys):
    codigo = main(
        [
            "run",
            str(tmp_path / "no_existe.py"),
            "--ticker", "AAPL",
            "--start", "2024-01-01",
            "--end", "2024-06-01",
        ]
    )

    assert codigo == 1
    assert "no existe" in capsys.readouterr().err


def test_run_exitoso_escribe_el_html_y_devuelve_0(tmp_path, capsys):
    estrategia_path = tmp_path / "estrategia.py"
    estrategia_path.write_text("def estrategia(datos):\n    pass\n")
    destino = tmp_path / "salida.html"

    with patch("ego_audit.cli.auditar_estrategia", return_value="<html>demo</html>"):
        codigo = main(
            [
                "run",
                str(estrategia_path),
                "--ticker", "AAPL",
                "--start", "2024-01-01",
                "--end", "2024-06-01",
                "--output", str(destino),
            ]
        )

    assert codigo == 0
    assert destino.read_text(encoding="utf-8") == "<html>demo</html>"
    assert "Reporte generado" in capsys.readouterr().out


def test_pasa_los_parametros_al_pipeline(tmp_path):
    estrategia_path = tmp_path / "estrategia.py"
    estrategia_path.write_text("def estrategia(datos):\n    pass\n")

    with patch("ego_audit.cli.auditar_estrategia", return_value="<html></html>") as mock_pipeline:
        main(
            [
                "run",
                str(estrategia_path),
                "--ticker", "MSFT",
                "--start", "2020-01-01",
                "--end", "2021-01-01",
                "--dias-ajuste", "30",
                "--dias-validacion", "10",
                "--paso", "10",
                "--tasa-comision", "0.002",
                "--tasa-slippage", "0.001",
                "--benchmark", "QQQ",
                "--output", str(tmp_path / "out.html"),
            ]
        )

    mock_pipeline.assert_called_once_with(
        ticker="MSFT",
        estrategia_path=estrategia_path,
        start="2020-01-01",
        end="2021-01-01",
        dias_ajuste=30,
        dias_validacion=10,
        paso=10,
        tasa_comision=0.002,
        tasa_slippage=0.001,
        benchmark="QQQ",
    )


def test_error_del_pipeline_se_reporta_sin_traceback_y_devuelve_1(tmp_path, capsys):
    estrategia_path = tmp_path / "estrategia.py"
    estrategia_path.write_text("def estrategia(datos):\n    pass\n")

    with patch("ego_audit.cli.auditar_estrategia", side_effect=RuntimeError("boom")):
        codigo = main(
            [
                "run",
                str(estrategia_path),
                "--ticker", "AAPL",
                "--start", "2024-01-01",
                "--end", "2024-06-01",
            ]
        )

    assert codigo == 1
    assert "boom" in capsys.readouterr().err


def test_falta_argumento_requerido_sale_con_error(tmp_path):
    estrategia_path = tmp_path / "estrategia.py"
    estrategia_path.write_text("def estrategia(datos):\n    pass\n")

    with pytest.raises(SystemExit):
        main(["run", str(estrategia_path), "--start", "2024-01-01", "--end", "2024-06-01"])
