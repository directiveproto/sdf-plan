from __future__ import annotations

from typing import Any

from sdf_plan.core.ir import IRSequence, toolcalls_to_ir
from sdf_plan.inputs.generic_toolcall import parse_generic_toolcall
from sdf_plan.inputs.openai_toolcalls import parse_openai_toolcalls
from sdf_plan.inputs.planspec import parse_planspec


def normalize_to_ir(payload: Any, *, input_format: str = "auto") -> IRSequence:
    fmt = (input_format or "auto").strip().lower()

    if isinstance(payload, IRSequence):
        return payload

    if fmt == "ir":
        if isinstance(payload, dict):
            return IRSequence.model_validate(payload)
        raise ValueError("ir payload must be dict/IRSequence")

    if fmt == "openai":
        return toolcalls_to_ir(parse_openai_toolcalls(payload), source="openai")

    if fmt == "generic":
        return toolcalls_to_ir(parse_generic_toolcall(payload), source="generic")

    if fmt == "planspec":
        return toolcalls_to_ir(parse_planspec(payload), source="planspec")

    if not isinstance(payload, dict) and not isinstance(payload, list):
        raise ValueError("auto normalization expects dict/list/IRSequence")

    if isinstance(payload, dict) and isinstance(payload.get("actions"), list) and str(payload.get("version", "")).startswith("sdf.ir"):
        return IRSequence.model_validate(payload)

    if isinstance(payload, dict) and isinstance(payload.get("steps"), list):
        return toolcalls_to_ir(parse_planspec(payload), source="planspec")

    if isinstance(payload, dict) and (
        isinstance(payload.get("tool_calls"), list)
        or isinstance(payload.get("choices"), list)
    ):
        return toolcalls_to_ir(parse_openai_toolcalls(payload), source="openai")

    if isinstance(payload, list):
        # Prefer OpenAI list shape if entries include function/name hints.
        if payload and isinstance(payload[0], dict) and (
            "function" in payload[0] or "name" in payload[0] or "arguments" in payload[0]
        ):
            return toolcalls_to_ir(parse_openai_toolcalls(payload), source="openai")
        return toolcalls_to_ir(parse_generic_toolcall(payload), source="generic")

    if isinstance(payload, dict):
        return toolcalls_to_ir(parse_generic_toolcall(payload), source="generic")

    raise ValueError("unsupported payload for normalization")
