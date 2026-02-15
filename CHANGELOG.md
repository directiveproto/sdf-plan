# Changelog

## 0.2.1 - 2026-02-15

### Changed
- Release hygiene follow-up after `0.2.0`:
  - removed accidentally tracked local virtualenv artifacts from repository history tip
  - tightened ignore rules for local venv and bytecode artifacts
- No API or behavior changes from `0.2.0`.

## 0.2.0 - 2026-02-15

### Added
- ToolGate-first runtime API:
  - `propose(tool_name, args, meta, policy, run_context)`
  - `confirm(token, user_ok=True)`
- Gate contract models and stable enums/error codes.
- Canonical hashing + deterministic idempotency key generation.
- Sequence IR (`sdf.ir.v1`) + multi-input normalization:
  - OpenAI-style tool-call payloads
  - Generic tool-call JSON
  - PlanSpec
- PlanSpec compatibility mapping helpers:
  - `planspec_to_ir(...)`
  - `ir_to_planspec(...)` (best-effort, deterministic)
- Tool-mode lint rules:
  - `UNKNOWN_TOOL`
  - `WRITE_REQUIRES_CONFIRM`
  - `ACT_WITHOUT_IDEMPOTENCY`
  - `NO_VERIFY_BEFORE_WRITE` (context-gated)
- Thin LangGraph adapter (`adapters/langgraph.py`) and adapter contract tests.
- New guides:
  - `docs/ADAPTER_TEMPLATE.md`
  - `docs/POLICY_TUNING.md`
  - `docs/TOOL_CLASSIFICATION.md`
  - `docs/COMPATIBILITY.md`
- ToolGate-first examples:
  - `examples/tool_gate_quickstart.py`
  - `examples/tool_gate_openai_input.py`
  - `examples/plan_mode_preflight.py`

### Changed
- README is now ToolGate-first.
- PlanSpec remains supported as optional mode.
- CI hardened with dedicated jobs:
  - `unit` (coverage gate)
  - `contract` (schema freeze)
  - `integration`
  - `adapter-contract`
  - `package-smoke`
- Release workflow now runs extended Python matrix before build/publish.

### Compatibility and Migration Notes
- PlanSpec backward compatibility is preserved for v0.2.0.
- PlanSpec <-> IR conversion is deterministic best-effort.
- Lossless roundtrip is not guaranteed; non-lossless mappings emit `UserWarning`.
- Unknown tools default to confirmation-required behavior via policy defaults.

### Migration from 0.1.x to 0.2.0
1. Existing PlanSpec usage requires no breaking code changes.
2. For tool-call runtimes, switch to ToolGate API:
   - call `propose(...)` before executing a tool
   - if blocked with resume token, call `confirm(...)` and retry with `meta.confirmed_token`
3. If needed, tune policy in code (`strict_mode`, `verify_before_write`, classification overrides).

### Security Notes
- Confirmation tokens are signed and time-bounded.
- Resume flow is bound to tool + canonical args hash + scope.

## 0.1.0
- Initial public release of PlanSpec models, linting, and wrappers.
