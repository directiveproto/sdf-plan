from __future__ import annotations


def test_langgraph_adapter_and_legacy_integration_imports_smoke() -> None:
    from sdf_plan.adapters.langgraph import langgraph_tool_gate_node
    from sdf_plan.integrations.langgraph import sdf_node

    assert callable(langgraph_tool_gate_node)
    assert callable(sdf_node)

