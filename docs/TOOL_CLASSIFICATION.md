# Tool Classification

ToolGate classifies each tool into a category + risk flags.

Default map for compatibility (`v1`) is in `src/sdf_plan/policy/default_tool_map.json`.
Current default map (`v2`) is in `src/sdf_plan/policy/tool_map_v2.json`.

## Built-in behavior

- Unknown tools map to category `unknown`
- Unknown tools carry risk flag `unknown_tool`
- Default policy requires confirmation for unknown tools
- `v2` is intentionally more conservative for selected external/privileged tools
  (for example: `filesystem.copy`, `http.post`, `shell.exec`).
- `v2` supports exact and prefix patterns (for example `filesystem.*`).

## Match precedence

Tool classification is deterministic:

1. exact match (for example `filesystem.read`)
2. longest prefix match (for example `filesystem.secure.*` over `filesystem.*`)
3. unknown fallback

This allows broad namespace defaults without enumerating every tool name.

## Tool map versions

Load map versions explicitly:

```python
from sdf_plan.policy import load_default_tool_risk_map

v2 = load_default_tool_risk_map(version="v2")  # current default
v1 = load_default_tool_risk_map(version="v1")  # compatibility map
```

## Override map (dict)

```python
from sdf_plan.policy import load_tool_risk_map, classify_tool

overrides = {
    "payments.refund": {
        "category": "money",
        "risk_flags": ["payment", "write", "external_side_effect"],
    }
}

risk_map = load_tool_risk_map(overrides)
print(classify_tool("payments.refund", risk_map))
```

## Override map (JSON file)

```python
risk_map = load_tool_risk_map("./tool_risk_overrides.json")
```

Use overrides to align ToolGate semantics with your internal tool naming.

Prefix override example:

```python
overrides = {
    "filesystem.*": {"category": "write_local", "risk_flags": ["write"]},
    "filesystem.read": {"category": "read_only", "risk_flags": []},  # exact override
}
```
