from sdf_plan import lint_plan, policy_annotate, preflight_lint


def main() -> None:
    plan = {
        "plan_id": "pln_example",
        "version": "sdf.v1.2",
        "template_key": "default",
        "confidence": 0.4,
        "steps": [
            {
                "id": "S1",
                "type": "ACT",
                "title": "send invoice",
                "intent": "send invoice email to customer",
                "inputs": [],
                "outputs": ["ctx.step1"],
                "depends_on": [],
                "stop_condition": "Step S1 completed",
                "fallback": "reduce_scope",
                "retry": 0,
                "time_budget_sec": 120,
                "confirm": None,
                "idempotency_key": "idem-1",
            }
        ],
    }

    plan, summary = policy_annotate(plan)
    findings = lint_plan(plan, max_steps=12, safety_mode="safe")
    preflight_lint(plan, max_steps=12, safety_mode="safe")

    print("Policy summary:", summary)
    print("Lint findings:")
    for item in findings:
        print(f"- {item['level']} {item['code']}: {item['message']}")


if __name__ == "__main__":
    main()
