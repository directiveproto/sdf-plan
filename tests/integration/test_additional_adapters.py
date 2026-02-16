from __future__ import annotations

from sdf_plan.adapters import crewai_tool_gate, langchain_tool_gate


def test_crewai_adapter_thin_wrapper() -> None:
    gate = crewai_tool_gate(default_ctx={"workspace_id": "ws-1"})
    out = gate(tool_name="filesystem.write", args={"path": "/tmp/a", "content": "x"})
    assert out.decision.value == "REQUIRE_CONFIRM"
    assert out.resume is not None


def test_langchain_adapter_thin_wrapper() -> None:
    gate = langchain_tool_gate(default_ctx={"workspace_id": "ws-1"})
    out = gate(tool_name="filesystem.read", args={"path": "/tmp/a"})
    assert out.decision.value in {"ALLOW", "WARN", "BLOCK", "REQUIRE_CONFIRM"}

