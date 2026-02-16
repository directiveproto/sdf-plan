from sdf_plan import confirm
from sdf_plan.adapters.langgraph import langgraph_tool_gate_node


def test_langgraph_adapter_requires_confirm_for_write_and_interrupts() -> None:
    node = langgraph_tool_gate_node()
    out = node(
        {
            "tool_call": {
                "tool": "filesystem.write",
                "args": {"path": "/tmp/a", "content": "x"},
                "meta": {"workspace_id": "ws-1"},
            },
            "run_context": {"workspace_id": "ws-1"},
        }
    )

    assert out["tool_gate_decision"] == "REQUIRE_CONFIRM"
    assert out["tool_gate_interrupt"] is True
    token = out["tool_gate"]["resume"]["token"]
    assert isinstance(token, str) and token


def test_langgraph_adapter_confirm_then_continue_allow() -> None:
    node = langgraph_tool_gate_node()

    first = node(
        {
            "tool_call": {
                "tool": "filesystem.write",
                "args": {"path": "/tmp/a", "content": "x"},
                "meta": {"workspace_id": "ws-1"},
            },
            "run_context": {"workspace_id": "ws-1"},
        }
    )
    token = first["tool_gate"]["resume"]["token"]
    c = confirm(token)
    assert c.confirmed is True

    second = node(
        {
            "tool_call": {
                "tool": "filesystem.write",
                "args": {"path": "/tmp/a", "content": "x"},
                "meta": {"workspace_id": "ws-1", "confirmed_token": token},
            },
            "run_context": {"workspace_id": "ws-1"},
        }
    )
    assert second["tool_gate_decision"] == "ALLOW"
    assert second["tool_gate_interrupt"] is False


def test_langgraph_adapter_strict_unknown_hard_block_no_interrupt() -> None:
    node = langgraph_tool_gate_node(policy={"strict_mode": True})
    out = node({"tool_name": "unknown.tool", "args": {}, "meta": {}, "run_context": {}})
    assert out["tool_gate_decision"] == "BLOCK"
    assert out["tool_gate_interrupt"] is False
