from __future__ import annotations

import json
from typing import Any, Dict, List


def _parse_args(value: Any) -> Dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, dict):
        return dict(value)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return {}
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                return parsed
            return {"_value": parsed}
        except Exception:
            return {"_raw": value}
    return {"_value": value}


def _extract_tool_calls(payload: Any) -> List[Dict[str, Any]]:
    if isinstance(payload, list):
        return payload
    if not isinstance(payload, dict):
        raise ValueError("openai payload must be dict or list")

    if isinstance(payload.get("tool_calls"), list):
        return payload["tool_calls"]

    choices = payload.get("choices")
    if isinstance(choices, list) and choices:
        msg = (choices[0] or {}).get("message") or {}
        tcs = msg.get("tool_calls")
        if isinstance(tcs, list):
            return tcs

    raise ValueError("no OpenAI tool calls found")


def parse_openai_toolcalls(payload: Any) -> List[Dict[str, Any]]:
    tool_calls = _extract_tool_calls(payload)
    out: List[Dict[str, Any]] = []

    for idx, call in enumerate(tool_calls, start=1):
        if not isinstance(call, dict):
            raise ValueError("tool call entries must be objects")

        call_id = call.get("id") or f"A{idx}"

        fn = call.get("function") if isinstance(call.get("function"), dict) else None
        name = call.get("name") or (fn or {}).get("name")
        args_raw = call.get("arguments")
        if args_raw is None and fn:
            args_raw = fn.get("arguments")

        out.append(
            {
                "id": str(call_id),
                "tool_name": str(name or "unknown.tool"),
                "args": _parse_args(args_raw),
                "meta": {
                    "provider": "openai",
                    "type": call.get("type"),
                },
            }
        )

    return out
