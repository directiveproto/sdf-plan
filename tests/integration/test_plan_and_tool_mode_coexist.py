from sdf_plan.lint import lint_plan, lint_tool_mode
from sdf_plan.policy import policy_annotate


def test_plan_mode_lint_still_works_with_tool_mode_present() -> None:
    plan = {
        "steps": [
            {
                "id": "S1",
                "type": "ACT",
                "title": "Send",
                "intent": "send email",
                "inputs": [],
                "outputs": ["out"],
                "depends_on": [],
                "stop_condition": "done",
                "fallback": "retry",
                "idempotency_key": "idem_1",
            }
        ]
    }
    plan, _ = policy_annotate(plan)
    findings = lint_plan(plan, max_steps=12, safety_mode="safe")
    codes = {f["code"] for f in findings}
    assert "WRITE_WITHOUT_CONFIRM" not in codes


def test_tool_mode_and_plan_mode_coexist_in_same_run() -> None:
    plan = {
        "steps": [
            {
                "id": "S1",
                "type": "ACT",
                "title": "Write",
                "intent": "write file",
                "inputs": [],
                "outputs": ["file"],
                "depends_on": [],
                "stop_condition": "done",
                "fallback": "retry",
                "idempotency_key": "idem_2",
            }
        ]
    }
    plan, _ = policy_annotate(plan)
    plan_findings = lint_plan(plan, max_steps=12, safety_mode="safe")
    tool_findings = lint_tool_mode(tool_name="filesystem.write", args={"path": "/tmp/a"}, meta={})

    assert isinstance(plan_findings, list)
    assert isinstance(tool_findings, list)
    assert any(f["code"] == "WRITE_REQUIRES_CONFIRM" for f in tool_findings)
