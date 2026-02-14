from __future__ import annotations

import json

from sdf_plan.lint import lint_plan
from sdf_plan.models import PlanSpecEnvelope, PlanStep
from sdf_plan.policy import policy_annotate


def test_unicode_and_emoji_inputs():
    plan = {
        "steps": [
            {
                "id": "S1",
                "type": "ACT",
                "title": "Notify 🚀",
                "intent": "send email with unicode ✅",
                "inputs": [""],
                "outputs": ["ctx.üñïçødé"],
                "depends_on": [],
                "stop_condition": "Provider accepted ✅",
                "fallback": "retry",
                "idempotency_key": "idem_emoji",
                "confirm": "confirm",
            }
        ]
    }
    annotated, _summary = policy_annotate(plan)
    findings = lint_plan(annotated, max_steps=12, safety_mode="safe")
    assert {f["code"] for f in findings} == {"NO_VERIFY_BEFORE_WRITE"}


def test_long_goal_and_weird_context_keys():
    goal_text = "x" * 20000
    envelope = PlanSpecEnvelope(
        plan_id="fuzz_goal",
        template_key="default",
        confidence=0.5,
        goal_spec={"goal": goal_text, "ctx..x": {"ctx/x": [1, {"k": "v"}]}},
        steps=[
            PlanStep(
                id="S1",
                type="ANALYZE",
                title="Analyze",
                intent="analyze",
                stop_condition="analysis generated",
                fallback="reduce_scope",
            )
        ],
    )
    assert envelope.goal_spec["goal"] == goal_text


def test_duplicate_output_keys_warn():
    plan = {
        "steps": [
            {
                "id": "S1",
                "type": "ANALYZE",
                "title": "Analyze",
                "intent": "analyze",
                "inputs": [],
                "outputs": ["ctx.same"],
                "depends_on": [],
                "stop_condition": "ok",
                "fallback": "reduce_scope",
            },
            {
                "id": "S2",
                "type": "ANALYZE",
                "title": "Analyze 2",
                "intent": "analyze",
                "inputs": [],
                "outputs": ["ctx.same"],
                "depends_on": [],
                "stop_condition": "ok",
                "fallback": "reduce_scope",
            },
        ]
    }
    findings = lint_plan(plan, max_steps=12, safety_mode="safe")
    codes = {f["code"] for f in findings}
    assert "DUPLICATE_OUTPUT_KEY" in codes


def test_nested_json_payload_roundtrip():
    payload = {
        "steps": [
            {
                "id": "S1",
                "type": "ANALYZE",
                "title": "Analyze",
                "intent": "analyze",
                "inputs": [],
                "outputs": ["ctx.out"],
                "depends_on": [],
                "stop_condition": "ok",
                "fallback": "reduce_scope",
            }
        ],
        "meta": {"ctx/x": [1, 2, {"a": ["b", {"c": 3}]}]},
    }
    data = json.dumps(payload)
    assert json.loads(data)["meta"]["ctx/x"][2]["a"][1]["c"] == 3
