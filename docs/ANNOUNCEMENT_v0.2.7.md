# Announcing sdf-plan v0.2.7

`sdf-plan` v0.2.7 is now live on PyPI.

## What's new
- ToolGate hardening with shared internal policy helpers (no gate/lint drift).
- First-class configuration: `SdfPlanConfig` + `configure(...)`.
- First-class `GateContext` with backward-compatible legacy context support.
- Async APIs: `apropose(...)` and `aconfirm(...)`.
- Versioned tool map support with expanded `v2` defaults.
- Audit hook support for `propose/confirm`.
- Strict args mode for safer untrusted payload handling.
- CLI:
  - `sdf-plan lint <plan.json>`
  - `sdf-plan classify --tool <name>`
- Thin adapters for LangGraph, CrewAI, and LangChain.

## Install
```bash
pip install -U sdf-plan
```

## Links
- PyPI: https://pypi.org/project/sdf-plan/
- Release notes: https://github.com/directiveproto/sdf-plan/releases/tag/v0.2.7
- Changelog: https://github.com/directiveproto/sdf-plan/blob/main/CHANGELOG.md

