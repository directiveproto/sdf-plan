# sdf-plan

PlanSpec + lint + safety gates for agent plans.

## 3-Minute Quickstart

```bash
pip install sdf-plan
python -c "from sdf_plan import preflight_lint; print('OK')"
python examples/quickstart_local_lint.py
```

Expected output includes:
- lint findings
- policy summary with confirm-required counts

## What You Get

- PlanSpec models (`sdf.v1.2`)
- lint engine
- policy annotation helper
- `preflight_lint` helper/decorator
- LangGraph/CrewAI adapters

## Local Dev Install

```bash
pip install -e .
```

## Basic Example

```python
from sdf_plan import lint_plan, policy_annotate, preflight_lint

plan = {"steps": [{"id": "S1", "type": "ACT", "intent": "send email", "inputs": [], "outputs": ["x"], "depends_on": [], "stop_condition": "Step S1 completed", "fallback": "reduce_scope"}]}
plan, summary = policy_annotate(plan)
findings = lint_plan(plan, max_steps=12, safety_mode="safe")
preflight_lint(plan, max_steps=12, safety_mode="safe")
```

## Examples

- `examples/quickstart_local_lint.py`
- `examples/langgraph_plangate_demo.py`
- `examples/crewai_plangate_demo.py`

## Compatibility

Use Cloud schema hash checks to detect contract drift:

```python
from sdf_plan.compat import assert_schema_compat, package_version

assert_schema_compat(package_version(), "schema_hash_from_/v1/schema")
```
