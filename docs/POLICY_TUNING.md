# Policy Tuning

`GatePolicy` controls how strict ToolGate is.

## Defaults (safe)

- `unknown_tool = REQUIRE_CONFIRM`
- `write_requires_confirm = true`
- `require_idempotency_for_write = true`
- `verify_before_write = WARN`
- `strict_mode = false`

## Example: stricter policy

```python
from sdf_plan import propose

policy = {
    "strict_mode": True,
    "unknown_tool": "BLOCK",
    "verify_before_write": "ENFORCE",
}

out = propose(
    tool_name="unknown.tool",
    args={"x": 1},
    policy=policy,
)
print(out.decision.value)
```

## Example: reduce friction for trusted internal tools

```python
policy = {
    "write_requires_confirm": False,
    "verify_before_write": "WARN",
}
```

Use strict policy for production writes and relaxed policy for local/dev workflows.
