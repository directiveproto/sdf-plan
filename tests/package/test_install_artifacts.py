import os
import subprocess
import sys
from pathlib import Path

import pytest


def _run(cmd: list[str], cwd: Path) -> str:
    proc = subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
    return proc.stdout.strip()


def _venv_python(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def _install_and_import(artifact: Path, root: Path, suffix: str) -> None:
    venv_dir = root / ".pytest_tmp" / f"venv_{suffix}"
    venv_dir.parent.mkdir(parents=True, exist_ok=True)
    _run([sys.executable, "-m", "venv", str(venv_dir)], cwd=root)
    py = _venv_python(venv_dir)
    _run([str(py), "-m", "pip", "install", "-U", "pip"], cwd=root)
    _run([str(py), "-m", "pip", "install", str(artifact)], cwd=root)
    version = _run([str(py), "-c", "import sdf_plan; print(sdf_plan.__version__)"], cwd=root)
    assert version


@pytest.mark.package
def test_install_wheel_and_sdist_in_clean_env():
    if os.getenv("RUN_PACKAGE_TESTS") != "1":
        pytest.skip("Set RUN_PACKAGE_TESTS=1 to run packaging tests")

    root = Path(__file__).resolve().parents[2]
    wheel = sorted((root / "dist").glob("*.whl"))
    sdist = sorted((root / "dist").glob("*.tar.gz"))
    assert wheel, "wheel artifact missing"
    assert sdist, "sdist artifact missing"

    _install_and_import(wheel[-1], root, "wheel")
    _install_and_import(sdist[-1], root, "sdist")
