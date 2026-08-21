"""sandbox-07: tests de fuga -- confirman que el aislamiento del sandbox funciona
de verdad contra un contenedor real, no solo que los argumentos se construyen bien
(eso ya lo cubren test_sandbox_config.py y test_sandbox_wrapper.py con mocks).

Se saltan enteros si Docker no esta disponible -- no lo esta en la maquina de
desarrollo actual (ver arq-03-decision-sandbox). En cuanto haya Docker instalado,
`pytest tests/test_sandbox_leak.py` los ejecuta de verdad.
"""

import shutil
import subprocess

import pandas as pd
import pytest

from ego_audit.sandbox.wrapper import run_strategy_in_sandbox

pytestmark = pytest.mark.skipif(
    shutil.which("docker") is None,
    reason="Docker no esta instalado en este entorno -- ver arq-03-decision-sandbox",
)


def _fake_datos() -> pd.DataFrame:
    return pd.DataFrame(
        {"Open": [1.0], "High": [1.5], "Low": [0.5], "Close": [1.2], "Volume": [100]},
        index=pd.to_datetime(["2024-01-01"]),
    )


@pytest.fixture(scope="module", autouse=True)
def sandbox_image():
    subprocess.run(
        ["docker", "build", "-t", "ego-audit-sandbox:latest", "docker/sandbox"],
        check=True,
    )


def test_intento_de_red_falla(tmp_path_factory):
    path = tmp_path_factory.mktemp("fuga") / "estrategia_fuga_red.py"
    path.write_text(
        "import pandas as pd\n"
        "import urllib.request\n"
        "\n"
        "def estrategia(datos):\n"
        "    try:\n"
        "        urllib.request.urlopen('http://example.com', timeout=3)\n"
        "        bloqueada = False\n"
        "    except Exception:\n"
        "        bloqueada = True\n"
        "    return pd.Series([1.0 if bloqueada else 0.0], index=datos.index[:1])\n"
    )
    senales = run_strategy_in_sandbox(_fake_datos(), path)
    assert senales.iloc[0] == 1.0, "FUGA: la estrategia alcanzo la red desde dentro del sandbox"


def test_intento_de_escritura_fuera_de_work_falla(tmp_path_factory):
    path = tmp_path_factory.mktemp("fuga") / "estrategia_fuga_fs.py"
    path.write_text(
        "import pandas as pd\n"
        "\n"
        "def estrategia(datos):\n"
        "    try:\n"
        "        with open('/etc/ego-audit-leak-test', 'w') as f:\n"
        "            f.write('leak')\n"
        "        bloqueada = False\n"
        "    except Exception:\n"
        "        bloqueada = True\n"
        "    return pd.Series([1.0 if bloqueada else 0.0], index=datos.index[:1])\n"
    )
    senales = run_strategy_in_sandbox(_fake_datos(), path)
    assert senales.iloc[0] == 1.0, "FUGA: la estrategia escribio fuera de /work"
