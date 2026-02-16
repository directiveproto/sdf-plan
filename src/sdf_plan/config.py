from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Callable


AuditHook = Callable[[Any], None]
_DEV_FALLBACK_SECRET = "sdf-plan-dev-only-secret"


@dataclass(slots=True)
class SdfPlanConfig:
    secret: str | None = None
    token_ttl: int = 600
    audit_hook: AuditHook | None = None
    strict_args: bool = False
    environment: str = "development"


_CONFIG: SdfPlanConfig = SdfPlanConfig()


def configure(config: SdfPlanConfig) -> None:
    global _CONFIG
    _CONFIG = config


def get_config() -> SdfPlanConfig:
    return _CONFIG


def get_secret_bytes() -> bytes:
    cfg = get_config()
    env = (cfg.environment or "development").strip().lower()
    secret = cfg.secret or os.getenv("SDF_PLAN_TOKEN_SECRET")
    if secret:
        return str(secret).encode("utf-8")
    if env == "development":
        return _DEV_FALLBACK_SECRET.encode("utf-8")
    raise RuntimeError(
        "SDF Plan secret is required outside development. "
        "Set SDF_PLAN_TOKEN_SECRET or configure(SdfPlanConfig(secret=...))."
    )

