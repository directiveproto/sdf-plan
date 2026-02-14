from __future__ import annotations

from copy import deepcopy

import pytest

from sdf_plan.integrations.crewai import SDFTool
from sdf_plan.preflight import LintError


def _ok_plan() -> dict:
    return {
        "steps": [
            {
                "id": "S1",
                "type": "ACT",
                "title": "Send",
                "intent": "send email",
                "inputs": [],
                "outputs": ["ctx.sent"],
                "depends_on": [],
                "stop_condition": "Provider accepted",
                "fallback": "retry",
                "confirm": "Confirm",
                "idempotency_key": "idem_s1",
            },
            {
                "id": "S2",
                "type": "VERIFY",
                "title": "Verify",
                "intent": "verify status",
                "inputs": ["ctx.sent"],
                "outputs": ["ctx.verified"],
                "depends_on": ["S1"],
                "stop_condition": "Status is delivered",
                "fallback": "manual_review",
            },
        ]
    }


def test_crewai_wrapper_returns_plan_and_no_input_mutation(monkeypatch):
    context = {"a": 1}
    tools = [{"name": "mail"}]
    context_before = deepcopy(context)
    tools_before = deepcopy(tools)

    monkeypatch.setattr("sdf_plan.integrations.crewai.decompose_via_api", lambda **_: _ok_plan())
    monkeypatch.setattr("sdf_plan.integrations.crewai.preflight_lint", lambda *_args, **_kwargs: [])

    tool = SDFTool(api_base="http://x", api_key="k")
    out = tool.run("send mail", context=context, tools=tools)
    assert out["steps"][0]["id"] == "S1"
    assert context == context_before
    assert tools == tools_before


def test_crewai_wrapper_works_with_empty_tool_list(monkeypatch):
    monkeypatch.setattr("sdf_plan.integrations.crewai.decompose_via_api", lambda **_: _ok_plan())
    monkeypatch.setattr("sdf_plan.integrations.crewai.preflight_lint", lambda *_args, **_kwargs: [])
    tool = SDFTool(api_base="http://x", api_key="k")
    out = tool.run("send mail", tools=[])
    assert out["steps"]


def test_crewai_wrapper_propagates_confirm_gate_signal(monkeypatch):
    monkeypatch.setattr("sdf_plan.integrations.crewai.decompose_via_api", lambda **_: _ok_plan())

    def fake_preflight_lint(*_args, **_kwargs):
        raise LintError([{"level": "ERROR", "code": "WRITE_WITHOUT_CONFIRM", "step_id": "S1"}])

    monkeypatch.setattr("sdf_plan.integrations.crewai.preflight_lint", fake_preflight_lint)
    tool = SDFTool(api_base="http://x", api_key="k")
    with pytest.raises(LintError) as exc:
        tool.run("send mail")
    assert exc.value.findings[0]["code"] == "WRITE_WITHOUT_CONFIRM"
