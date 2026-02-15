from sdf_plan.adapters.langgraph import langgraph_tool_gate_node


def test_langgraph_adapter_contract_shape_and_no_mutation() -> None:
    node = langgraph_tool_gate_node()

    state = {
        "tool_call": {
            "tool": "filesystem.write",
            "args": {"path": "/tmp/x", "content": "hello"},
            "meta": {"workspace_id": "ws-1"},
        },
        "run_context": {"workspace_id": "ws-1", "recent_actions": []},
    }
    original = {
        "tool_call": {
            "tool": state["tool_call"]["tool"],
            "args": dict(state["tool_call"]["args"]),
            "meta": dict(state["tool_call"]["meta"]),
        },
        "run_context": {"workspace_id": "ws-1", "recent_actions": []},
    }

    out = node(state)
    assert "tool_gate" in out
    assert "tool_gate_decision" in out
    assert "tool_gate_interrupt" in out

    # Adapter must not mutate caller-provided structures.
    assert state == original


def test_langgraph_adapter_contract_flat_keys_supported() -> None:
    node = langgraph_tool_gate_node()
    out = node(
        {
            "tool_name": "filesystem.read",
            "args": {"path": "/tmp/x"},
            "meta": {"workspace_id": "ws-1"},
            "run_context": {"workspace_id": "ws-1", "recent_actions": [{"tool_name": "filesystem.read"}]},
        }
    )
    assert out["tool_gate_decision"] in {"ALLOW", "WARN", "BLOCK"}
