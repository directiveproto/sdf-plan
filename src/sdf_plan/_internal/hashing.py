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


def _canonicalize(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (str, bool)):
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return _normalize_number(value)
    if isinstance(value, dict):
        return {
            str(k): _canonicalize(v)
            for k, v in sorted(value.items(), key=lambda kv: str(kv[0]))
        }
    if isinstance(value, (list, tuple)):
        return [_canonicalize(v) for v in value]
    return str(value)


def canonical_json(value: Any) -> str:
    normalized = _canonicalize(value)
    return json.dumps(
        normalized,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def hash_canonical(value: Any, algorithm: str = "sha256") -> str:
    try:
        h = hashlib.new(algorithm)
    except ValueError as exc:
        raise ValueError(f"unsupported hash algorithm: {algorithm}") from exc
    h.update(canonical_json(value).encode("utf-8"))
    return h.hexdigest()

