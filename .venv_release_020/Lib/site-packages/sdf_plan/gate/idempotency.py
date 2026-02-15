from __future__ import annotations

from copy import deepcopy
from typing import Any, Iterable

from sdf_plan.core.hashing import hash_canonical


def _drop_path(target: Any, path: list[str]) -> None:
    if not path:
        return
    if not isinstance(target, dict):
        return

    head = path[0]
    if head not in target:
        return
    if len(path) == 1:
        target.pop(head, None)
        return
    _drop_path(target.get(head), path[1:])


def apply_exclusions(args: dict[str, Any], exclude_fields: Iterable[str] | None = None) -> dict[str, Any]:
    materialized = deepcopy(args)
    if not exclude_fields:
        return materialized

    for field in exclude_fields:
        pieces = [p for p in str(field).split(".") if p]
        if not pieces:
            continue
        _drop_path(materialized, pieces)
    return materialized


def args_hash(args: dict[str, Any], exclude_fields: Iterable[str] | None = None) -> str:
    filtered = apply_exclusions(args, exclude_fields=exclude_fields)
    return hash_canonical(filtered)


def generate_idempotency_key(
    *,
    scope: Any,
    tool_name: str,
    args: dict[str, Any],
    exclude_fields: Iterable[str] | None = None,
    prefix: str = "idem",
) -> str:
    payload = {
        "scope": scope,
        "tool": (tool_name or "").strip().lower(),
        "args_hash": args_hash(args, exclude_fields=exclude_fields),
    }
    digest = hash_canonical(payload)
    return f"{prefix}_{digest}"
