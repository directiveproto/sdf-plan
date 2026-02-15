from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

from sdf_plan.gate.tool_gate import propose


def _extract_tool_inputs(
    state: Dict[str, Any],
    *,
    tool_name_key: str,
    args_key: str,
    meta_key: str,
    run_context_key: str,
) -> tuple[str, dict[str, Any], dict[str, Any], dict[str, Any] | None]:
    if isinstance(state.get("tool_call"), dict):
        tc = state["tool_call"]
        tool_name = tc.get("tool") or tc.get("tool_name") or tc.get("name")
        args = tc.get("args") or tc.get("arguments") or {}
        meta = tc.get("meta") or {}
        run_context = state.get(run_context_key)
        return str(tool_name or ""), dict(args or {}), dict(meta or {}), run_context

    tool_name = state.get(tool_name_key)
    args = state.get(args_key) or {}
    meta = state.get(meta_key) or {}
    run_context = state.get(run_context_key)
    return str(tool_name or ""), dict(args or {}), dict(meta or {}), run_context


def langgraph_tool_gate_node(
    *,
    policy: dict[str, Any] | None = None,
    tool_name_key: str = "tool_name",
    args_key: str = "args",
    meta_key: str = "meta",
    run_context_key: str = "run_context",
    output_key: str = "tool_gate",
):
    """Return a thin LangGraph-style node that gates one proposed tool call.

    Expected state (either form):
      - state["tool_call"] = {"tool"|"tool_name"|"name", "args"|"arguments", "meta"}
      - OR flat keys: tool_name/args/meta

    Returns:
      {
        output_key: ToolGateResponse dict,
        "tool_gate_decision": str,
        "tool_gate_interrupt": bool,
      }
    """

    def node(state: Dict[str, Any]) -> Dict[str, Any]:
        tool_name, args, meta, run_context = _extract_tool_inputs(
            state,
            tool_name_key=tool_name_key,
            args_key=args_key,
            meta_key=meta_key,
            run_context_key=run_context_key,
        )
        if not tool_name:
            raise ValueError("tool_name is required")

        # Defensive copy so wrapper never mutates caller state.
        decision = propose(
            tool_name=tool_name,
            args=deepcopy(args),
            meta=deepcopy(meta),
            policy=policy,
            run_context=deepcopy(run_context) if isinstance(run_context, dict) else run_context,
        )

        decision_dict = decision.model_dump()
        interrupt = bool(
            decision.decision.value == "BLOCK"
            and decision.resume is not None
            and bool(decision.resume.token)
        )
        return {
            output_key: decision_dict,
            "tool_gate_decision": decision.decision.value,
            "tool_gate_interrupt": interrupt,
        }

    return node
