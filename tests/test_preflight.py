from sdf_plan import LintError, policy_annotate, preflight_lint


def test_preflight_raises_for_invalid_act_step():
    plan = {
        "steps": [
            {
                "id": "S1",
                "type": "ACT",
                "title": "send email",
                "intent": "send email to customer",
                "inputs": [],
                "outputs": ["ctx.step1"],
                "depends_on": [],
                "stop_condition": "Step S1 completed",
                "fallback": "reduce_scope",
                "retry": 0,
                "time_budget_sec": 120,
                "confirm": None,
            }
        ]
    }
    plan, _summary = policy_annotate(plan)
    try:
        preflight_lint(plan, max_steps=12, safety_mode="safe")
        assert False, "expected LintError"
    except LintError:
        assert True
