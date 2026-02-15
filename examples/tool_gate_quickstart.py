from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from sdf_plan import confirm, propose


def main() -> None:
    first = propose(
        tool_name="filesystem.write",
        args={"path": "/tmp/demo.txt", "content": "hello"},
        meta={"workspace_id": "demo-ws"},
        run_context={"workspace_id": "demo-ws"},
    )
    print("Step 1:", first.decision.value)

    token = first.resume.token if first.resume else None
    if not token:
        raise RuntimeError("Expected confirmation token")

    confirmed = confirm(token, user_ok=True)
    print("Step 2:", "CONFIRMED" if confirmed.confirmed else "DENIED")

    second = propose(
        tool_name="filesystem.write",
        args={"path": "/tmp/demo.txt", "content": "hello"},
        meta={"workspace_id": "demo-ws", "confirmed_token": token},
        run_context={"workspace_id": "demo-ws"},
    )
    print("Step 3:", second.decision.value)


if __name__ == "__main__":
    main()
