# sdf-plan v0.2.7

## Highlights
- Unified internal policy helpers across gate/lint/policy paths to remove logic drift.
- Added first-class configuration (`SdfPlanConfig`, `configure`) with non-development secret fail-fast behavior.
- Introduced first-class `GateContext` and canonical `propose(..., ctx=...)` flow, with deprecation-compatible legacy support.
- Added versioned tool map support (`v2` default) with expanded common tool classifications.
- Added optional audit hook payload emission for `propose` and `confirm`.
- Added async APIs: `apropose(...)` and `aconfirm(...)`.
- Added strict args mode enforcement for top-level payload safety.

## Adapter and CLI Enhancements
- Added thin `CrewAI` and `LangChain` ToolGate wrappers.
- Added minimal CLI:
  - `sdf-plan lint <plan.json>`
  - `sdf-plan classify --tool <name>`

## Docs and DX
- Updated README to canonical `GateContext` usage.
- Added migration guide: `docs/MIGRATION_PLANSPEC_TO_TOOLGATE.md`.
- Added production hardening guide: `docs/PRODUCTION_HARDENING.md`.
- Updated API reference for async/config/versioned-map surfaces.

## CI / Release Hygiene
- Added CLI tests to CI and release workflows.
- Updated packaging metadata:
  - Homepage URL corrected
  - dev extras added in `pyproject.toml`
  - `__version__` exported

## Compatibility Notes
- PlanSpec mode remains backward compatible.
- Legacy context in `meta` / `run_context` still works and now emits deprecation warnings.
- Unknown tool default policy remains confirmation-required.
