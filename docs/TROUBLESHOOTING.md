# Troubleshooting

Common issues and concrete fixes for `sdf-plan`.

## 1) `No module named sdf_plan`

Cause:
- package not installed in active environment.

Fix:
```bash
pip install sdf-plan
```

For local development:
```bash
pip install -e ".[dev]"
```

## 2) `TOKEN_TAMPERED`

Cause:
- token was altered, truncated, or signed with different secret.

Fix:
1. Ensure token is passed unchanged.
2. Ensure same signing secret is used across propose/confirm path.
3. Avoid decoding/re-encoding tokens in transit.

## 3) `TOKEN_EXPIRED`

Cause:
- confirmation delayed beyond token TTL.

Fix:
1. shorten human delay between propose and confirm
2. increase TTL in config if operationally acceptable
3. re-run propose to issue a fresh token

## 4) `STRICT_SCOPE_REQUIRED`

Cause:
- strict mode write path without `ctx.workspace_id`.

Fix:
```python
from sdf_plan import GateContext
ctx = GateContext(workspace_id="ws_123")
```

## 5) `TOKEN_BINDING_MISMATCH`

Cause:
- confirmed token reused with different tool or different args.

Fix:
- pass the exact same tool + semantic args after confirm.
- avoid mutating payload between confirm and resume call.

## 6) Unexpected `REQUIRE_CONFIRM` for unknown tool

Cause:
- default policy is safety-biased for unknown tools.

Fix options:
1. classify tool in risk map
2. override policy (`unknown_tool`) where appropriate

Use:
- `docs/TOOL_CLASSIFICATION.md`
- `docs/POLICY_TUNING.md`

## 7) Development fallback secret warning

Cause:
- no explicit token secret configured in development mode.

Fix:
- set `SDF_PLAN_TOKEN_SECRET` even in dev to mirror production behavior.

## 8) Adapter behavior differs from direct API call

Cause:
- adapter may be mutating args/meta or not forwarding context.

Fix:
1. run adapter contract tests
2. compare adapter call vs direct `propose(...)`
3. ensure adapter is thin and stateless

## 9) Schema snapshot test fails

Cause:
- API contract changed, but snapshot not updated (or change unintended).

Fix:
1. confirm contract change is intentional
2. update snapshot fixture(s)
3. add migration note in changelog/release notes

## 10) Which integration path should I use?

Use:
- `sdf_plan.adapters.*` for runtime ToolGate (recommended)

Avoid new usage of:
- `sdf_plan.integrations.*` (legacy decomposition-client path)

## Quick Debug Checklist

1. Confirm package version:
```python
import sdf_plan
print(sdf_plan.__version__)
```
2. Confirm decision + reason + error_code in response.
3. Confirm `ctx.workspace_id` is present.
4. Confirm token roundtrip is unchanged.
5. Confirm policy overrides are what you expect.
6. Run unit/integration tests for token and flow paths.
