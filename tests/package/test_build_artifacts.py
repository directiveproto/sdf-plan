import os
import re
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
    dist = root / "dist"
    if dist.exists():
        for p in dist.iterdir():
            p.unlink()
    _run([sys.executable, "-m", "pip", "install", "-U", "twine"], cwd=root)
    _run([sys.executable, "-m", "build"], cwd=root)

    wheels = list(dist.glob("*.whl"))
    sdists = list(dist.glob("*.tar.gz"))
    assert wheels, "wheel artifact missing"
    assert sdists, "sdist artifact missing"
    _run([sys.executable, "-m", "twine", "check", *[str(p) for p in wheels + sdists]], cwd=root)
    assert any(re.match(r"^sdf_plan-.*\.whl$", p.name) for p in wheels), "wheel filename must be normalized"
    assert any(re.match(r"^sdf_plan-.*\.tar\.gz$", p.name) for p in sdists), "sdist filename must be normalized"
