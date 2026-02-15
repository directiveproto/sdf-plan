from __future__ import annotations

from typing import Any, Dict, List


def _normalize_one(entry: Dict[str, Any], *, default_id: str) -> Dict[str, Any]:
    tool_name = entry.get("tool") or entry.get("tool_name") or entry.get("name")
    args = entry.get("args")
    if args is None:
        args = entry.get("arguments")
    meta = entry.get("meta") or {}

    return {
        "id": str(entry.get("id") or default_id),
        "tool_name": str(tool_name or "unknown.tool"),
        "args": dict(args or {}),
        "meta": dict(meta),
    }


def parse_generic_toolcall(payload: Any) -> List[Dict[str, Any]]:
    if isinstance(payload, list):
        entries = payload
    elif isinstance(payload, dict) and isinstance(payload.get("tool_calls"), list):
        entries = payload["tool_calls"]
    elif isinstance(payload, dict):
        entries = [payload]
    else:
        raise ValueError("generic payload must be dict or list")

    out: List[Dict[str, Any]] = []
    for idx, raw in enumerate(entries, start=1):
        if not isinstance(raw, dict):
            raise ValueError("generic tool call entries must be objects")
        out.append(_normalize_one(raw, default_id=f"A{idx}"))
    return out
