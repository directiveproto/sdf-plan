from __future__ import annotations

from typing import Any

WRITE_INTENT_KEYWORDS = (
    "send",
    "email",
    "post",
    "tweet",
    "publish",
    "charge",
    "pay",
    "buy",
    "book",
    "reservation",
    "delete",
    "remove",
    "update",
    "write",
    "commit",
    "submit",
    "upload",
    "transfer",
)


def is_write_tool(category: str, risk_flags: list[str]) -> bool:
    if category.startswith("write"):
        return True
    write_like = {"write", "external_side_effect", "payment", "prod_change", "credential_access"}
    return any(flag in write_like for flag in risk_flags)


def has_verify_context(run_context: dict[str, Any] | None) -> bool:
    ctx = run_context or {}
    if ctx.get("verified") is True:
        return True
    actions = ctx.get("recent_actions") or []
    for action in actions:
        if not isinstance(action, dict):
            continue
        kind = str(action.get("kind") or "").lower()
        tool_name = str(action.get("tool_name") or "").lower()
        if kind in {"verify", "confirm"}:
            return True
        if "verify" in tool_name or tool_name.endswith(".read"):
            return True
    return False


def looks_like_write_intent(intent: str) -> bool:
    normalized = (intent or "").lower()
    return any(k in normalized for k in WRITE_INTENT_KEYWORDS)

