"""Full LangGraph-style ToolGate demo.

Run:
  python examples/langgraph-full/demo.py
"""

from sdf_plan.adapters.langgraph import langgraph_tool_gate_node


def main() -> None:
    node = langgraph_tool_gate_node()
    state = {
        "tool_call": {
            "tool_name": "filesystem.write",
            "args": {"path": "/tmp/demo.txt", "content": "hello"},
            "meta": {},
        },
        "run_context": {"workspace_id": "demo-ws", "user_id": "user-1"},
    }

    result = node(state)
    gate = result["tool_gate"]

    print("decision:", result["tool_gate_decision"])
    print("interrupt:", result["tool_gate_interrupt"])
    if gate.get("resume"):
        print("resume token present:", bool(gate["resume"].get("token")))


if __name__ == "__main__":
    main()
