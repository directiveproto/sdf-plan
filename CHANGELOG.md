# Changelog

## 0.2.9 - 2026-02-26

### Added
- New example directories:
  - `examples/langgraph-full/`
  - `examples/crewai-thin-wrapper/`
- Repository metadata-as-code in `.github/settings.yml` for About description, homepage, and topics.

### Changed
- README top section rewritten for landing-page style positioning.
- README now includes:
  - stronger trust/positioning copy
  - a capabilities comparison table (`sdf-plan` vs manual checks / LangGraph interrupts / NeMo)
  - updated badge set and demo references
- Package metadata updated to ToolGate-first description and URLs:
  - homepage: `https://safetydf.com`
  - documentation: `https://safetydf.com/docs`

## 0.2.8 - 2026-02-16

### Added
- Prefix/wildcard tool classification support (for example `filesystem.*`) with deterministic precedence:
  - exact match
  - longest prefix match
  - unknown fallback
- Optional strict `tool_args_validator(tool_name, args)` hook in `SdfPlanConfig`.
- Strict hashing support for canonicalization/idempotency paths; strict mode now rejects non-JSON-native values.
- Explicit CI guard job for:
  - token `jti` presence
  - strict write-scope enforcement
  - legacy-vs-adapter import clarity smoke test
- Release notes template for v0.2.8: `docs/releases/v0.2.8.md`.

### Changed
- `propose(...)` now threads strict-mode behavior consistently across token arg-binding and idempotency derivation.
- Documentation refreshed across README/API/security/hardening/migration guides:
  - replay protection with `jti` store example
  - legacy integrations vs ToolGate adapters table
  - strict mode rollout checklist

### Migration Notes
- Strict-mode behavior is intentionally tighter:
  - write tools without `ctx.workspace_id` are blocked (`STRICT_SCOPE_REQUIRED`)
  - non-JSON-native values are rejected in strict hashing paths
  - optional `tool_args_validator` can block invalid payloads
- This is a behavior change in strict mode only. Non-strict mode remains backward compatible.

## 0.2.7 - 2026-02-16

### Added
- Internal shared helper modules to eliminate duplicated gate/lint/policy logic:
  - `_internal/policy_helpers.py`
  - `_internal/token.py`
  - `_internal/hashing.py`
- Config API:
  - `SdfPlanConfig`
  - `configure(...)`
  - environment-aware secret handling with non-development fail-fast behavior.
- First-class `GateContext` and canonical `propose(..., ctx=...)` usage.
- Async gate APIs:
  - `apropose(...)`
  - `aconfirm(...)`
- Tool map v2 support and versioned loader:
  - `load_default_tool_risk_map(version=...)`
  - `load_tool_risk_map(..., version=...)`
- Audit hook support on `propose/confirm`.
- Minimal CLI:
  - `sdf-plan lint <plan.json>`
  - `sdf-plan classify --tool <name>`
- Thin adapter wrappers:
  - `crewai_tool_gate`
  - `langchain_tool_gate`
- New docs:
  - `docs/MIGRATION_PLANSPEC_TO_TOOLGATE.md`
  - `docs/PRODUCTION_HARDENING.md`

### Changed
- README quickstart now uses `GateContext`-first canonical flow.
- API reference updated for `ctx`, async APIs, config API, and map versioning.
- CI/release workflows now include CLI tests.

## 0.2.6 - 2026-02-15

### Fixed
- Updated build backend requirement to setuptools>=77 so sdist names are generated in canonical form (sdf_plan-*.tar.gz) accepted by PyPI.
- Resolves repeated PyPI 400 failures caused by invalid/non-canonical sdist filename format.

## 0.2.5 - 2026-02-15

### Fixed
- PyPI release workflow now uses skip-existing: true in publish step to make reruns idempotent when one artifact from the same version already exists.
- Prevents false release failures caused by partial prior uploads.

## 0.2.4 - 2026-02-15

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
