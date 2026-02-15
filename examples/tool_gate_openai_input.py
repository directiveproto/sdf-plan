from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from sdf_plan import normalize_to_ir, propose


def main() -> None:
    payload = {
        "tool_calls": [
            {
                "id": "tc_1",
                "function": {
                    "name": "filesystem.write",
                    "arguments": '{"path":"/tmp/openai.txt","content":"hello"}',
                },
            }
        ]
    }

    ir = normalize_to_ir(payload, input_format="openai")
    action = ir.actions[0]

    out = propose(
        tool_name=action.tool_name,
        args=action.args,
        meta={"workspace_id": "demo-ws"},
        run_context={"workspace_id": "demo-ws"},
    )

    print("Normalized tool:", action.tool_name)
    print("Decision:", out.decision.value)


if __name__ == "__main__":
    main()
