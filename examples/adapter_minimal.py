"""Minimal custom adapter example (framework-agnostic)."""

from sdf_plan import propose


def minimal_adapter(tool_name: str, args: dict, meta: dict | None = None, run_context: dict | None = None) -> dict:
    decision = propose(
        tool_name=tool_name,
        args=args,
        meta=meta or {},
        run_context=run_context or {},
    )

    if decision.decision.value == "ALLOW":
        return {"status": "allow", "gate": decision.model_dump()}

    if decision.decision.value == "WARN":
        return {"status": "warn", "gate": decision.model_dump()}

    if decision.resume and decision.resume.token:
        return {
            "status": "interrupt_for_confirm",
            "confirm_prompt": decision.confirm_prompt,
            "resume_token": decision.resume.token,
            "gate": decision.model_dump(),
        }

    return {"status": "blocked", "gate": decision.model_dump()}


if __name__ == "__main__":
    out = minimal_adapter(
        tool_name="filesystem.write",
        args={"path": "/tmp/demo.txt", "content": "hello"},
        meta={"workspace_id": "demo-ws"},
        run_context={"workspace_id": "demo-ws"},
    )
    print(out["status"])
