from __future__ import annotations

import pytest

import sdf_plan.config as cfg_module
from sdf_plan import SdfPlanConfig, configure, propose
from sdf_plan.gate.contracts import GateDecision


@pytest.fixture(autouse=True)
def _reset_config() -> None:
    configure(SdfPlanConfig())
    cfg_module._WARNED_DEV_FALLBACK = False
    yield
    configure(SdfPlanConfig())
    cfg_module._WARNED_DEV_FALLBACK = False


def test_development_allows_local_secret_fallback() -> None:
    configure(SdfPlanConfig(secret=None, environment="development"))
    with pytest.warns(RuntimeWarning, match="development fallback token secret"):
        out = propose(
            "filesystem.write",
            {"path": "/tmp/a", "content": "x"},
            ctx={"workspace_id": "ws-1"},
        )
    assert out.decision == GateDecision.REQUIRE_CONFIRM
    assert out.resume is not None
    assert out.resume.token


def test_non_development_requires_secret() -> None:
    configure(SdfPlanConfig(secret=None, environment="production"))
    with pytest.raises(RuntimeError, match="secret is required outside development"):
        propose(
            "filesystem.write",
            {"path": "/tmp/a", "content": "x"},
            ctx={"workspace_id": "ws-1"},
        )


def test_non_development_with_secret_is_valid() -> None:
    configure(SdfPlanConfig(secret="super-secret-value", environment="production"))
    out = propose(
        "filesystem.write",
        {"path": "/tmp/a", "content": "x"},
        ctx={"workspace_id": "ws-1"},
    )
    assert out.decision == GateDecision.REQUIRE_CONFIRM

