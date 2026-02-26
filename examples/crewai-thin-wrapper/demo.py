"""Thin CrewAI wrapper ToolGate demo.

Run:
  python examples/crewai-thin-wrapper/demo.py
"""

from sdf_plan.adapters.crewai import crewai_tool_gate
from sdf_plan.gate.contracts import GateContext


def main() -> None:
    gate = crewai_tool_gate(default_ctx=GateContext(workspace_id="demo-ws"))

    first = gate(
        tool_name="filesystem.write",
        args={"path": "/tmp/demo.txt", "content": "hello"},
    )
    print("first:", first.decision.value)

    if first.resume and first.resume.token:
        second = gate(
            tool_name="filesystem.write",
            args={"path": "/tmp/demo.txt", "content": "hello"},
            meta={"confirmed_token": first.resume.token},
        )
        print("second:", second.decision.value)


if __name__ == "__main__":
    main()
