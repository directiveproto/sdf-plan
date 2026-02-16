from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable

from sdf_plan.gate.contracts import GateContext, ToolGateResponse
from sdf_plan.gate.tool_gate import propose


def langchain_tool_gate(
    *,
    policy: dict[str, Any] | None = None,
    default_ctx: GateContext | dict[str, Any] | None = None,
) -> Callable[..., ToolGateResponse]:
    """Thin LangChain-style gate wrapper for tool-call interception."""

    def gate(
        *,
        tool_name: str,
        args: dict[str, Any] | None = None,
        ctx: GateContext | dict[str, Any] | None = None,
        meta: dict[str, Any] | None = None,
        run_context: dict[str, Any] | None = None,
    ) -> ToolGateResponse:
        resolved_ctx = ctx if ctx is not None else default_ctx
        return propose(
            tool_name=tool_name,
            args=deepcopy(args or {}),
            ctx=deepcopy(resolved_ctx) if isinstance(resolved_ctx, dict) else resolved_ctx,
            meta=deepcopy(meta or {}),
            run_context=deepcopy(run_context or {}),
            policy=policy,
        )

    return gate

