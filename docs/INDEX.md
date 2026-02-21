# Documentation Index

This is the canonical documentation map for `sdf-plan`.

## Start Here

1. New user (first success in 5 minutes):
   - `README.md`
   - `docs/API_REFERENCE.md` (core calls)
2. Integrating into an agent runtime:
   - `docs/INTEGRATION_RECIPES.md`
   - `docs/ADAPTER_TEMPLATE.md`
3. Security and production hardening:
   - `docs/SECURITY_MODEL.md`
   - `docs/PRODUCTION_HARDENING.md`
4. Migrating from older PlanSpec-first usage:
   - `docs/MIGRATION_PLANSPEC_TO_TOOLGATE.md`

## Core Docs

- `docs/API_REFERENCE.md`
  Canonical public API contracts, signatures, decisions, and errors.
- `docs/ARCHITECTURE.md`
  Internal architecture and data flow from input normalization to gate decision.
- `docs/SECURITY_MODEL.md`
  Threat model, token semantics, replay posture, and host responsibilities.
- `docs/COMPATIBILITY.md`
  Version compatibility and contract drift guidance.

## Integration Docs

- `docs/INTEGRATION_RECIPES.md`
  End-to-end recipes for OpenAI-style calls, custom runtimes, and adapter usage.
- `docs/ADAPTER_TEMPLATE.md`
  Minimal template for building a new thin adapter.
- `docs/TOOL_CLASSIFICATION.md`
  Tool risk map guidance and override strategy.
- `docs/POLICY_TUNING.md`
  Policy knobs and recommended profiles.

## Operations Docs

- `docs/PRODUCTION_HARDENING.md`
  Deployment and runtime hardening baseline.
- `docs/RELEASING.md`
  Release workflow and publishing steps.
- `docs/TROUBLESHOOTING.md`
  Common failures and concrete fixes.

## Release-Specific Docs

- `docs/releases/` and release note/checklist files.

These capture point-in-time release execution and should be read with the version tag in mind.
