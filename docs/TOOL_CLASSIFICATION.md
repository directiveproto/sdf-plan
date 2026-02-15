# Tool Classification

ToolGate classifies each tool into a category + risk flags.

Default map is in `src/sdf_plan/policy/default_tool_map.json`.

## Built-in behavior

- Unknown tools map to category `unknown`
- Unknown tools carry risk flag `unknown_tool`
- Default policy requires confirmation for unknown tools

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
