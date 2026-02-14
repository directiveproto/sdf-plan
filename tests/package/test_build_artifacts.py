import os
import subprocess
import sys
from pathlib import Path

import pytest


def _run(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


@pytest.mark.package
def test_build_produces_wheel_and_sdist_and_twine_is_valid():
    if os.getenv("RUN_PACKAGE_TESTS") != "1":
        pytest.skip("Set RUN_PACKAGE_TESTS=1 to run packaging tests")

    root = Path(__file__).resolve().parents[2]
    _run([sys.executable, "-m", "build"], cwd=root)
    _run([sys.executable, "-m", "twine", "check", "dist/*"], cwd=root)

    wheels = list((root / "dist").glob("*.whl"))
    sdists = list((root / "dist").glob("*.tar.gz"))
    assert wheels, "wheel artifact missing"
    assert sdists, "sdist artifact missing"
