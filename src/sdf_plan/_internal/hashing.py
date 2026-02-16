from __future__ import annotations

import hashlib
import json
import math
from typing import Any


def _normalize_number(value: int | float) -> int | float:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if not math.isfinite(value):
        raise ValueError("non-finite floats are not allowed in canonical JSON")
    if value == 0.0:
        return 0
    if value.is_integer():
        return int(value)
    return float(format(value, ".15g"))


def _canonicalize(value: Any, *, strict: bool) -> Any:
    if value is None:
        return None
    if isinstance(value, (str, bool)):
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return _normalize_number(value)
    if isinstance(value, dict):
        normalized_items: list[tuple[str, Any]] = []
        for key, nested_value in value.items():
            if strict and not isinstance(key, str):
                raise ValueError("non-string object keys are not allowed in strict mode")
            normalized_key = str(key)
            normalized_items.append(
                (normalized_key, _canonicalize(nested_value, strict=strict))
            )
        return {k: v for k, v in sorted(normalized_items, key=lambda kv: kv[0])}
    if isinstance(value, (list, tuple)):
        return [_canonicalize(v, strict=strict) for v in value]
    if strict:
        raise ValueError(
            f"non-JSON-native value type {type(value).__name__} is not allowed in strict mode"
        )
    return str(value)


def canonical_json(value: Any, *, strict: bool = False) -> str:
    normalized = _canonicalize(value, strict=strict)
    return json.dumps(
        normalized,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def hash_canonical(value: Any, algorithm: str = "sha256", *, strict: bool = False) -> str:
    try:
        h = hashlib.new(algorithm)
    except ValueError as exc:
        raise ValueError(f"unsupported hash algorithm: {algorithm}") from exc
    h.update(canonical_json(value, strict=strict).encode("utf-8"))
    return h.hexdigest()

