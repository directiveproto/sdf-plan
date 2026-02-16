from __future__ import annotations

import pytest

from sdf_plan import propose
from sdf_plan.gate.contracts import GateDecision


@pytest.mark.slow
def test_fuzz_weird_payloads_do_not_crash() -> None:
    weird_payloads = [
        {"nested": {"a": [1, None, "x", {"k": "v"}]}},
        {"emoji": "write 🚀 café", "null": None, "arr": [[], [{}], [1, 2, 3]]},
        {"long": "x" * 100_000},
        {"mixed": [{"k": 1}, 2, "3", 4.0, True, None]},
        {"deep": {"a": {"b": {"c": {"d": {"e": {"f": 1}}}}}}},
    ]

    for args in weird_payloads:
        out = propose(
            "totally.unknown.tool",
            args,
            meta={"workspace_id": "ws-1"},
            run_context={"workspace_id": "ws-1"},
        )
        # Unknown tool default should be gated but never crash.
        assert out.decision in {GateDecision.REQUIRE_CONFIRM, GateDecision.BLOCK, GateDecision.WARN}
