# BYO Adapter Template

This template shows how to integrate `sdf-plan` ToolGate with any framework in ~20-30 lines.

## Adapter Contract
Your adapter should only do three things:
1. Extract the framework-native tool call into `(tool_name, args, meta, run_context)`.
2. Call `propose(...)`.
3. Map decision to your runtime flow (allow, block, interrupt-for-confirm).

Do not re-implement policy, lint, or idempotency logic in the adapter.

## Minimal Pattern

```python
from sdf_plan import propose


def adapter_handler(framework_state):
    tool_name = framework_state["tool_name"]
    args = framework_state.get("args", {})
    meta = framework_state.get("meta", {})
    run_context = framework_state.get("run_context", {})

    decision = propose(
        tool_name=tool_name,
        args=args,
        meta=meta,
        policy=None,
        run_context=run_context,
    )

    if decision.decision.value == "ALLOW":
        return {"action": "continue", "gate": decision.model_dump()}

    if decision.decision.value == "WARN":
        return {"action": "continue_with_warning", "gate": decision.model_dump()}

    if decision.resume and decision.resume.token:
        return {
            "action": "interrupt_for_confirm",
            "confirm_prompt": decision.confirm_prompt,
            "resume_token": decision.resume.token,
            "gate": decision.model_dump(),
        }

    return {"action": "blocked", "gate": decision.model_dump()}
```

## Confirmation Flow
1. Runtime receives `interrupt_for_confirm`.
2. Human/operator confirms.
3. Runtime resubmits the same tool call with `meta.confirmed_token=<token>`.
4. Adapter calls `propose(...)` again and continues on `ALLOW`.

## Required Adapter Guarantees
1. Preserve caller input objects (no mutation).
2. Always pass through `meta.workspace_id` when available.
3. Keep adapter thin; all safety semantics belong to ToolGate.
