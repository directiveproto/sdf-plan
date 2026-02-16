# Migration Guide: PlanSpec to ToolGate

## Goal
Move from plan-only preflight checks to runtime tool-call gating without breaking existing PlanSpec workflows.

## 1. Keep current plan mode running
Your existing calls still work:

```python
from sdf_plan import lint_plan, policy_annotate, preflight_lint
```

No migration is required to keep these APIs.

## 2. Add ToolGate at execution boundary
Start gating each proposed tool call before execution:

```python
from sdf_plan import GateContext, propose

ctx = GateContext(workspace_id="ws_123", user_id="u_1")
decision = propose("filesystem.write", {"path": "/tmp/a", "content": "x"}, ctx=ctx)
```

## 3. Handle confirm flow
When response is `REQUIRE_CONFIRM`, perform a human check and call `confirm(token)` before resuming.

## 4. Move identity context out of legacy fields
Legacy `meta`/`run_context` identity fields are still accepted but deprecated.
Use `ctx` for workspace/user/session identity going forward.

## 5. Optional adapter path
If you use framework wrappers:
- LangGraph: `langgraph_tool_gate_node`
- CrewAI: `crewai_tool_gate`
- LangChain: `langchain_tool_gate`

All wrappers are thin and call `propose(...)` internally.

## 6. Legacy integration note
`sdf_plan.integrations.*` is the pre-ToolGate decomposition-client path. It is
still available for compatibility, but new integrations should use
`sdf_plan.adapters.*` for runtime gating semantics.

Quick mapping:

| Legacy path | ToolGate-first replacement |
|---|---|
| `sdf_plan.integrations.langgraph.sdf_node` | `sdf_plan.adapters.langgraph.langgraph_tool_gate_node` |
| `sdf_plan.integrations.crewai.SDFTool` | `sdf_plan.adapters.crewai.crewai_tool_gate` |

## 7. Strict mode migration note

If you enable strict mode, this behavior changes by design:

- write tools without `ctx.workspace_id` are blocked (`STRICT_SCOPE_REQUIRED`)
- deep payload validation can be enforced with `tool_args_validator`

Apply strict mode in staged rollout: development -> staging -> production.

