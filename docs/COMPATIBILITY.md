# Compatibility

## Input Modes

`sdf-plan` v0.2.0 supports normalization from:

- PlanSpec plans
- OpenAI-style tool call payloads
- Generic tool call JSON

All normalize to `IRSequence` (`sdf.ir.v1`).

## PlanSpec Mapping Note

PlanSpec <-> IR mapping is deterministic best-effort.

It is not guaranteed lossless for framework-specific or extra fields.
When non-lossless mapping occurs in `ir_to_planspec(...)`, a `UserWarning` is emitted.

## Schema Drift Checks

If you use `sdf-cloud`, compare schema hashes:

```python
from sdf_plan.compat import assert_schema_compat, package_version
assert_schema_compat(package_version(), "schema_hash_from_/v1/schema")
```
