from __future__ import annotations

from copy import deepcopy

import pytest

from sdf_plan.integrations.langgraph import sdf_node
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


def test_langgraph_wrapper_returns_expected_shape_and_no_input_mutation(monkeypatch):
    state = {"goal": "send mail", "context": {"a": 1}, "tools": [{"name": "mail"}], "options": {"max_steps": 5}}
    state_before = deepcopy(state)

    def fake_decompose_via_api(**kwargs):
        assert kwargs["goal"] == "send mail"
        return _ok_plan()

    def fake_preflight_lint(plan, **kwargs):
        assert isinstance(plan, dict)
        return []

    monkeypatch.setattr("sdf_plan.integrations.langgraph.decompose_via_api", fake_decompose_via_api)
    monkeypatch.setattr("sdf_plan.integrations.langgraph.preflight_lint", fake_preflight_lint)

    node = sdf_node(api_base="http://x", api_key="k")
    out = node(state)
    assert "sdf_plan" in out
    assert out["sdf_plan"]["steps"][0]["id"] == "S1"
    assert state == state_before


def test_langgraph_wrapper_supports_empty_tools(monkeypatch):
    monkeypatch.setattr("sdf_plan.integrations.langgraph.decompose_via_api", lambda **_: _ok_plan())
    monkeypatch.setattr("sdf_plan.integrations.langgraph.preflight_lint", lambda *_args, **_kwargs: [])
    node = sdf_node(api_base="http://x", api_key="k")
    out = node({"goal": "send mail", "tools": []})
    assert out["sdf_plan"]["steps"]


def test_langgraph_wrapper_propagates_confirm_gate_signal(monkeypatch):
    monkeypatch.setattr("sdf_plan.integrations.langgraph.decompose_via_api", lambda **_: _ok_plan())

    def fake_preflight_lint(*_args, **_kwargs):
        raise LintError([{"level": "ERROR", "code": "WRITE_WITHOUT_CONFIRM", "step_id": "S1"}])

    monkeypatch.setattr("sdf_plan.integrations.langgraph.preflight_lint", fake_preflight_lint)
    node = sdf_node(api_base="http://x", api_key="k")
    with pytest.raises(LintError) as exc:
        node({"goal": "send mail"})
    assert exc.value.findings[0]["code"] == "WRITE_WITHOUT_CONFIRM"
