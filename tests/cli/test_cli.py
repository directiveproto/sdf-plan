from __future__ import annotations

import json
import os
import subprocess
import sys


def _env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    return env


def test_cli_classify() -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "sdf_plan", "classify", "--tool", "filesystem.write"],
        capture_output=True,
        text=True,
        env=_env(),
        check=False,
    )
    assert proc.returncode == 0
    out = json.loads(proc.stdout)
    assert out["tool"] == "filesystem.write"
    assert out["category"] in {"write_local", "write_external"}


def test_cli_lint(tmp_path) -> None:
    plan = {
        "steps": [
            {
                "id": "S1",
                "type": "ACT",
                "title": "Write file",
                "intent": "write a file",
                "inputs": [],
                "outputs": ["out"],
                "depends_on": [],
                "stop_condition": "done",
                "fallback": "noop",
                "idempotency_key": "idem-1",
            }
        ]
    }
    p = tmp_path / "plan.json"
    p.write_text(json.dumps(plan), encoding="utf-8")

    proc = subprocess.run(
        [sys.executable, "-m", "sdf_plan", "lint", str(p)],
        capture_output=True,
        text=True,
        env=_env(),
        check=False,
    )
    assert proc.returncode in {0, 1}
    parsed = json.loads(proc.stdout)
    assert isinstance(parsed, list)

