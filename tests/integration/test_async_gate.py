from __future__ import annotations

import asyncio

from sdf_plan import aconfirm, apropose
from sdf_plan.gate.contracts import GateDecision


def test_apropose_matches_sync_behavior() -> None:
    out = asyncio.run(
        apropose(
            "filesystem.write",
            {"path": "/tmp/a", "content": "x"},
            ctx={"workspace_id": "ws-1"},
        )
    )
    assert out.decision == GateDecision.REQUIRE_CONFIRM
    assert out.resume is not None
    assert out.resume.token


def test_aconfirm_allows_valid_token() -> None:
    first = asyncio.run(
        apropose(
            "filesystem.write",
            {"path": "/tmp/a", "content": "x"},
            ctx={"workspace_id": "ws-1"},
        )
    )
    token = first.resume.token if first.resume else None
    assert token
    out = asyncio.run(aconfirm(token))
    assert out.decision == GateDecision.ALLOW
    assert out.confirmed is True
