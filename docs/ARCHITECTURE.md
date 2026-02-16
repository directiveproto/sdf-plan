# Architecture

`sdf-plan` is organized around a ToolGate-first safety pipeline with optional PlanSpec support.

## High-Level Flow

1. Input ingestion:
- OpenAI-style tool calls
- Generic tool call JSON
- PlanSpec plans
2. Normalization:
- Convert inputs to sequence IR (`sdf_plan.core`)
3. Policy and classification:
- Tool risk classification and policy application (`sdf_plan.policy`)
4. Linting:
- Tool-mode and plan-mode lint checks (`sdf_plan.lint`)
5. Gate decision:
- `propose(...)` returns `ALLOW | REQUIRE_CONFIRM | WARN | BLOCK` (`sdf_plan.gate`)
6. Confirmation:
- `confirm(...)` verifies token and enables deterministic continuation (`sdf_plan.gate`)

## Package Layout

- `src/sdf_plan/gate/`
  - Contracts, token flow, idempotency helpers, runtime gate logic.
- `src/sdf_plan/core/`
  - IR models and normalization/conversion functions.
- `src/sdf_plan/inputs/`
  - OpenAI parser, generic tool call parser, PlanSpec parser.
- `src/sdf_plan/policy/`
  - Policy model, defaults, risk map, classification.
- `src/sdf_plan/lint/`
  - Tool-mode and plan-mode lint engines and rule registry.
- `src/sdf_plan/adapters/`
  - Official thin adapter(s). v0.2.0: LangGraph only.
- `src/sdf_plan/integrations/`
  - Legacy/community wrappers preserved for compatibility.

## Design Principles

1. ToolGate-first:
- Runtime tool-call interception is the primary API.
2. Backward compatible:
- Existing PlanSpec usage remains supported.
3. Deterministic behavior:
- Canonical hashing and stable policy flow.
4. Thin adapters:
- Adapters map framework objects to ToolGate API; policy and decision logic lives in core.
5. Safe defaults:
- Unknown tools do not silently pass in default policy posture.
