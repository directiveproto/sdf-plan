from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import Any

from sdf_plan.config import get_config, get_secret_bytes


def now_epoch_seconds() -> int:
    return int(time.time())


def b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def b64url_decode(text: str) -> bytes:
    pad = "=" * ((4 - len(text) % 4) % 4)
    return base64.urlsafe_b64decode((text + pad).encode("ascii"))


def sign_payload(payload: dict[str, Any]) -> str:
    payload_json = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    payload_b64 = b64url_encode(payload_json)
    sig = hmac.new(get_secret_bytes(), payload_b64.encode("ascii"), hashlib.sha256).digest()
    sig_b64 = b64url_encode(sig)
    return f"{payload_b64}.{sig_b64}"


def verify_token(token: str, *, now_fn=now_epoch_seconds) -> dict[str, Any]:
    parts = (token or "").split(".")
    if len(parts) != 2:
        raise ValueError("INVALID_TOKEN")

    payload_b64, sig_b64 = parts
    expected_sig = hmac.new(get_secret_bytes(), payload_b64.encode("ascii"), hashlib.sha256).digest()
    if not hmac.compare_digest(b64url_encode(expected_sig), sig_b64):
        raise ValueError("TOKEN_TAMPERED")

    try:
        payload = json.loads(b64url_decode(payload_b64).decode("utf-8"))
    except Exception as exc:
        raise ValueError("INVALID_TOKEN") from exc

    exp = int(payload.get("exp", 0))
    if now_fn() > exp:
        raise ValueError("TOKEN_EXPIRED")

    return payload


def issue_resume_token(
    *,
    tool_name: str,
    args_hash: str,
    scope: Any,
    idempotency_key: str | None,
    ttl_sec: int | None = None,
    now_fn=now_epoch_seconds,
) -> str:
    cfg = get_config()
    ttl = int(ttl_sec if ttl_sec is not None else cfg.token_ttl)
    payload = {
        "jti": secrets.token_urlsafe(16),
        "tool": tool_name,
        "args_hash": args_hash,
        "scope": scope,
        "idempotency_key": idempotency_key,
        "iat": now_fn(),
        "exp": now_fn() + ttl,
    }
    return sign_payload(payload)

