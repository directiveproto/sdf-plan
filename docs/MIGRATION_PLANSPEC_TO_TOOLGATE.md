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

