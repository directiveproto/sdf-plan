# sdf-plan

Tool safety gates for agent workflows.

[![CI](https://github.com/directiveproto/sdf-plan/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/directiveproto/sdf-plan/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/sdf-plan?label=PyPI&cacheSeconds=60)](https://pypi.org/project/sdf-plan/)
[![Python versions](https://img.shields.io/pypi/pyversions/sdf-plan.svg)](https://pypi.org/project/sdf-plan/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 30-Second Quickstart (ToolGate-first)

```python
from sdf_plan import GateContext, confirm, propose

ctx = GateContext(workspace_id="demo-ws")
first = propose(
    tool_name="filesystem.write",
    args={"path": "/tmp/demo.txt", "content": "hello"},
    ctx=ctx,
)
print(first.decision.value)  # REQUIRE_CONFIRM

token = first.resume.token
_ = confirm(token, user_ok=True)

second = propose(
    tool_name="filesystem.write",
    args={"path": "/tmp/demo.txt", "content": "hello"},
    ctx=ctx,
    meta={"confirmed_token": token},
)
print(second.decision.value)  # ALLOW
```

Expected flow: `REQUIRE_CONFIRM -> CONFIRM -> ALLOW`

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

## CLI

```bash
sdf-plan lint path/to/plan.json
sdf-plan classify --tool filesystem.write
```

## What You Get

- ToolGate runtime decisions (`ALLOW | REQUIRE_CONFIRM | WARN | BLOCK`)
- Signed confirmation tokens + resume flow
- Idempotency key derivation from scope + tool + canonical args
- Tool-mode lint rules + policy defaults
- PlanSpec lint and preflight (optional mode)
- LangGraph adapter (official thin wrapper for v0.2.7)

## Support Matrix (v0.2.7)

- Official maintained adapter: `LangGraph`
- Thin adapters: `CrewAI`, `LangChain`
- Direct parser support: OpenAI-style tool calls, generic tool call JSON, PlanSpec
- BYO adapter support: any framework that can pass `(tool_name, args, meta, run_context)` into `propose(...)`
- Deferred official adapters: additional framework-specific variants beyond thin wrappers

## Public API Stability

Top-level imports are a stable facade:

```python
from sdf_plan import propose, confirm
```

The facade remains stable while internals evolve; core logic stays in `sdf_plan/gate`, not in `__init__.py`.

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

- `docs/API_REFERENCE.md`
- `docs/ARCHITECTURE.md`
- `docs/SECURITY_MODEL.md`
- `docs/MIGRATION_PLANSPEC_TO_TOOLGATE.md`
- `docs/PRODUCTION_HARDENING.md`
- `docs/ADAPTER_TEMPLATE.md`
- `docs/POLICY_TUNING.md`
- `docs/TOOL_CLASSIFICATION.md`
- `docs/COMPATIBILITY.md`
- `docs/RELEASING.md`

## Examples

- `examples/tool_gate_quickstart.py`
- `examples/tool_gate_openai_input.py`
- `examples/plan_mode_preflight.py`
- `examples/adapter_minimal.py`
- `examples/langgraph_plangate_demo.py`
- `examples/crewai_plangate_demo.py` (community-style example, not an official adapter contract in v0.2.0)

## Testing (CI Parity)

Install dev/test dependencies:

```bash
pip install -e ".[dev]"
```

Fast local checks (matches PR path):

```bash
pytest -q -m "not slow" tests/unit
pytest -q tests/contract/test_gate_contract.py tests/contract/test_adapter_contract.py
pytest -q -m "not slow" tests/integration/test_openai_variants_normalization.py tests/integration/test_generic_toolcall_normalization.py tests/integration/test_planspec_to_ir.py tests/integration/test_tool_gate_flow.py tests/integration/test_tool_gate_concurrency.py tests/integration/test_plan_and_tool_mode_coexist.py tests/compat/test_planspec_roundtrip_best_effort.py
pytest -q tests/unit/test_token_security.py tests/integration/test_tool_gate_concurrency.py
```

Coverage gates:

```bash
pytest -q --cov=sdf_plan --cov-report=term-missing --cov-fail-under=70 tests/unit tests/integration
pytest -q --cov=sdf_plan.gate --cov-fail-under=70 tests/unit tests/integration
pytest -q --cov=sdf_plan.policy --cov-fail-under=70 tests/unit tests/integration
pytest -q --cov=sdf_plan.inputs --cov-fail-under=70 tests/unit tests/integration
```

Nightly/slow checks:

```bash
pytest -q -m slow tests/integration/test_fuzz_inputs.py tests/integration/test_perf_budget.py
```

Packaging smoke:

```bash
python -m build
twine check dist/*
pip install dist/*.whl
python -c "import sdf_plan; print('sdf_plan import ok')"
```

## Compatibility

Use Cloud schema hash checks to detect contract drift:

```python
from sdf_plan.compat import assert_schema_compat, package_version

assert_schema_compat(package_version(), "schema_hash_from_/v1/schema")
```

## Releases

- Git tags use `vX.Y.Z` format.
- GitHub Releases notes mirror `CHANGELOG.md`.
- PyPI releases are published from tagged workflow runs.
- See `docs/RELEASING.md` for the exact process.

## License

This project is licensed under the MIT License.
See `LICENSE` for the full text.
