from __future__ import annotations

import json
import time
from pathlib import Path

from sdf_plan.lint import lint_plan
from sdf_plan.models import PlanSpecEnvelope
from sdf_plan.policy import policy_annotate


FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "large_plan.json"


def test_perf_budget_large_plan():
    plan = json.loads(FIXTURE.read_text(encoding="utf-8"))
    t0 = time.perf_counter()
    annotated, summary = policy_annotate(plan)
    findings = lint_plan(annotated, max_steps=100, safety_mode="safe")
    envelope = {
        "plan_id": "perf_large",
        "version": "sdf.v1.2",
        "template_key": "default",
        "confidence": 0.8,
        "mode_used": "deterministic",
        "goal_spec": {"goal": "perf"},
        "steps": annotated["steps"],
        "lint": findings,
        "policy_summary": summary,
    }
    PlanSpecEnvelope.model_validate(envelope)
    elapsed = time.perf_counter() - t0
    assert elapsed < 2.0
