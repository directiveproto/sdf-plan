from __future__ import annotations

import time

import pytest

from sdf_plan import propose
from sdf_plan.gate.contracts import GateDecision


@pytest.mark.slow
def test_tool_gate_perf_budget_for_100_calls() -> None:
    start = time.perf_counter()
    decisions = []
    for i in range(100):
        out = propose(
            "web.search",
            {"q": f"query-{i}"},
            meta={"workspace_id": "ws-1"},
            policy={"unknown_tool": "WARN", "write_requires_confirm": False},
            run_context={"workspace_id": "ws-1"},
        )
        decisions.append(out.decision)
    elapsed = time.perf_counter() - start

    assert all(d in {GateDecision.ALLOW, GateDecision.WARN} for d in decisions)
    # Generous CI-friendly threshold to catch major regressions only.
    assert elapsed < 3.0
