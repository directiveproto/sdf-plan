# Integration Recipes

This guide shows practical integration patterns for `sdf-plan`.

## 1) Minimal Runtime Gate (Framework-Agnostic)

```python
from sdf_plan import GateContext, confirm, propose

ctx = GateContext(workspace_id="ws_123", user_id="u_1", session_id="sess_9")

proposal = propose(
    tool_name="filesystem.write",
    args={"path": "/tmp/out.txt", "content": "hello"},
    ctx=ctx,
)

if proposal.decision.value == "REQUIRE_CONFIRM":
    token = proposal.resume.token
    result = confirm(token, user_ok=True)
    if result.confirmed:
        proposal = propose(
            tool_name="filesystem.write",
            args={"path": "/tmp/out.txt", "content": "hello"},
            ctx=ctx,
            meta={"confirmed_token": token},
        )

if proposal.decision.value == "ALLOW":
    # execute tool
    pass
```

## 2) OpenAI-Style Tool Calls

Use `normalize_to_ir(...)` to parse OpenAI-style payloads and gate each action.

```python
from sdf_plan.core import normalize_to_ir
from sdf_plan import GateContext, propose

payload = {
    "tool_calls": [
        {
            "id": "call_1",
            "type": "function",
            "function": {"name": "filesystem.write", "arguments": "{\"path\":\"/tmp/a\",\"content\":\"x\"}"},
        }
    ]
}

ir = normalize_to_ir(payload, input_format="openai")
ctx = GateContext(workspace_id="ws_123")
for action in ir.actions:
    decision = propose(action.tool_name, args=action.args, ctx=ctx, meta=action.meta)
    print(action.tool_name, decision.decision.value)
```

## 3) Generic Tool Payloads

```python
from sdf_plan.core import normalize_to_ir

payload = {"tool": "web.search", "args": {"q": "toolgate"}, "meta": {"caller": "agent"}}
ir = normalize_to_ir(payload, input_format="generic")
```

## 4) LangGraph (Official Thin Adapter)

```python
from sdf_plan.adapters.langgraph import langgraph_tool_gate_node

node = langgraph_tool_gate_node()
```

Adapter guidance:
- Keep adapter logic thin.
- Pass through context and tool args.
- Let `sdf-plan` own policy/lint/decision semantics.

## 5) LangChain/CrewAI (Thin Wrappers)

Use provided thin wrappers in:
- `sdf_plan.adapters.langchain`
- `sdf_plan.adapters.crewai`

If framework behavior differs, follow:
- `docs/ADAPTER_TEMPLATE.md`

## 6) Strict Mode Integration

```python
from sdf_plan import SdfPlanConfig, configure

def validate_args(tool_name: str, args: dict) -> None:
    if tool_name == "payments.send" and "amount" not in args:
        raise ValueError("amount is required")

configure(SdfPlanConfig(strict_args=True, tool_args_validator=validate_args))
```

Recommended:
- strict mode for production write paths
- always provide `workspace_id`
- host replay protection keyed by token `jti`

## 7) PlanSpec Compatibility Mode

If your runtime is still plan-first:

```python
from sdf_plan import lint_plan, policy_annotate, preflight_lint

plan = {"steps": [...]}  # PlanSpec shape
plan, policy_summary = policy_annotate(plan)
findings = lint_plan(plan, max_steps=12, safety_mode="safe")
preflight_lint(plan, max_steps=12, safety_mode="safe")
```

Plan mode is supported, but ToolGate runtime mode is the recommended primary path.
