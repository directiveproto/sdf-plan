from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import pytest

from sdf_plan import confirm, propose
from sdf_plan.gate.contracts import GateDecision


@pytest.mark.security
def test_parallel_propose_is_stable_for_same_write_call() -> None:
    def call_once():
        return propose(
            "filesystem.write",
            {"path": "/tmp/a", "content": "hello"},
            meta={"workspace_id": "ws-1"},
            run_context={"workspace_id": "ws-1"},
        )

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda _: call_once(), range(20)))

    assert all(r.decision == GateDecision.REQUIRE_CONFIRM for r in results)
    idempotency_keys = [r.resume.idempotency_key for r in results if r.resume is not None]
    assert len(set(idempotency_keys)) == 1


@pytest.mark.security
def test_parallel_confirm_is_stable_for_same_token() -> None:
    first = propose(
        "filesystem.write",
        {"path": "/tmp/a", "content": "hello"},
        meta={"workspace_id": "ws-1"},
        run_context={"workspace_id": "ws-1"},
    )
    assert first.resume is not None
    assert first.resume.token is not None
    token = first.resume.token

    with ThreadPoolExecutor(max_workers=8) as pool:
        confirms = list(pool.map(lambda _: confirm(token), range(20)))

    assert all(c.decision == GateDecision.ALLOW for c in confirms)
    assert all(c.confirmed is True for c in confirms)
