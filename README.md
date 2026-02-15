# sdf-plan

Tool safety gates for agent workflows.

## 30-Second Quickstart (ToolGate-first)

```python
from sdf_plan import confirm, propose

first = propose(
    tool_name="filesystem.write",
    args={"path": "/tmp/demo.txt", "content": "hello"},
    meta={"workspace_id": "demo-ws"},
    run_context={"workspace_id": "demo-ws"},
)
print(first.decision.value)  # BLOCK

token = first.resume.token
_ = confirm(token, user_ok=True)

second = propose(
    tool_name="filesystem.write",
    args={"path": "/tmp/demo.txt", "content": "hello"},
    meta={"workspace_id": "demo-ws", "confirmed_token": token},
    run_context={"workspace_id": "demo-ws"},
)
print(second.decision.value)  # ALLOW
```

Expected flow: `BLOCKED -> CONFIRM -> CONTINUE`

## Install

```bash
pip install sdf-plan
```

## 5-Minute First Success

```bash
python examples/tool_gate_quickstart.py
python examples/tool_gate_openai_input.py
python examples/plan_mode_preflight.py
```

## What You Get

- ToolGate runtime decisions (`ALLOW | WARN | BLOCK`)
- Signed confirmation tokens + resume flow
- Idempotency key derivation from scope + tool + canonical args
- Tool-mode lint rules + policy defaults
- PlanSpec lint and preflight (optional mode)
- LangGraph adapter (official thin wrapper)

## Optional PlanSpec Mode

Plan mode remains supported for existing users.

```python
from sdf_plan import lint_plan, policy_annotate, preflight_lint

plan = {
    "steps": [
        {
            "id": "S1",
            "type": "ACT",
            "title": "send email",
            "intent": "send email",
            "inputs": [],
            "outputs": ["ctx.sent"],
            "depends_on": [],
            "stop_condition": "Step S1 completed",
            "fallback": "reduce_scope",
            "idempotency_key": "idem-1",
        }
    ]
}
plan, summary = policy_annotate(plan)
findings = lint_plan(plan, max_steps=12, safety_mode="safe")
preflight_lint(plan, max_steps=12, safety_mode="safe")
```

## Guides

- `docs/ADAPTER_TEMPLATE.md`
- `docs/POLICY_TUNING.md`
- `docs/TOOL_CLASSIFICATION.md`
- `docs/COMPATIBILITY.md`

## Examples

- `examples/tool_gate_quickstart.py`
- `examples/tool_gate_openai_input.py`
- `examples/plan_mode_preflight.py`
- `examples/adapter_minimal.py`
- `examples/langgraph_plangate_demo.py`
- `examples/crewai_plangate_demo.py`

## Compatibility

Use Cloud schema hash checks to detect contract drift:

```python
from sdf_plan.compat import assert_schema_compat, package_version

assert_schema_compat(package_version(), "schema_hash_from_/v1/schema")
```
