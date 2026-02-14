from __future__ import annotations

import json
from pathlib import Path

from sdf_plan.lint import lint_plan
from sdf_plan.policy import policy_annotate


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    target = root / "tests" / "fixtures" / "golden" / "minimal_policy_lint.json"

    plan = {
        "steps": [
            {
                "id": "S1",
                "type": "ACT",
                "title": "send email",
                "intent": "send email to customer",
                "inputs": [],
                "outputs": ["ctx.email_sent"],
                "depends_on": [],
                "stop_condition": "Email accepted by provider",
                "fallback": "queue_retry",
                "idempotency_key": "idem_s1",
            },
            {
                "id": "S2",
                "type": "VERIFY",
                "title": "verify send",
                "intent": "check provider status",
                "inputs": ["ctx.email_sent"],
                "outputs": ["ctx.verified"],
                "depends_on": ["S1"],
                "stop_condition": "Provider status OK",
                "fallback": "manual_review",
            },
        ]
    }

    annotated, summary = policy_annotate(plan)
    findings = lint_plan(annotated, max_steps=12, safety_mode="safe")
    payload = {
        "input_plan": plan,
        "expected_summary": summary,
        "expected_findings": findings,
    }
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
