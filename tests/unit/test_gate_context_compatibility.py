from __future__ import annotations

import pytest

from sdf_plan import propose
from sdf_plan.gate.contracts import GateDecision, GateContext


def test_ctx_first_call_style_is_supported() -> None:
    out = propose(
        "filesystem.write",
        {"path": "/tmp/a", "content": "x"},
        ctx=GateContext(workspace_id="ws-1", user_id="u-1", session_id="s-1"),
    )
    assert out.decision == GateDecision.REQUIRE_CONFIRM
    assert out.resume is not None
    assert out.resume.idempotency_key is not None


def test_legacy_meta_run_context_still_works_with_warning() -> None:
    with pytest.warns(DeprecationWarning, match="deprecated"):
        out = propose(
            "filesystem.write",
            {"path": "/tmp/a", "content": "x"},
            meta={"workspace_id": "ws-1"},
            run_context={"workspace_id": "ws-1"},
        )
    assert out.decision == GateDecision.REQUIRE_CONFIRM


def test_legacy_positional_meta_still_works_with_warning() -> None:
    with pytest.warns(DeprecationWarning, match="third positional argument"):
        out = propose(
            "filesystem.write",
            {"path": "/tmp/a", "content": "x"},
            {"confirm_prompt": "Confirm write"},
        )
    assert out.decision == GateDecision.REQUIRE_CONFIRM
