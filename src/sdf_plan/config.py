from __future__ import annotations

import os
import warnings
from dataclasses import dataclass
from typing import Any, Callable


AuditHook = Callable[[Any], None]
ToolArgsValidator = Callable[[str, dict[str, Any]], None]
_DEV_FALLBACK_SECRET = "sdf-plan-dev-only-secret"


@dataclass(slots=True)
class SdfPlanConfig:
    secret: str | None = None
    token_ttl: int = 600
    audit_hook: AuditHook | None = None
    strict_args: bool = False
    tool_args_validator: ToolArgsValidator | None = None
    environment: str = "development"


_CONFIG: SdfPlanConfig = SdfPlanConfig()
_WARNED_DEV_FALLBACK = False


def configure(config: SdfPlanConfig) -> None:
    global _CONFIG
    _CONFIG = config


def get_config() -> SdfPlanConfig:
    return _CONFIG


def get_secret_bytes() -> bytes:
    global _WARNED_DEV_FALLBACK
    cfg = get_config()
    env = (cfg.environment or "development").strip().lower()
    secret = cfg.secret or os.getenv("SDF_PLAN_TOKEN_SECRET")
    if secret:
        return str(secret).encode("utf-8")
    if env == "development":
        if not _WARNED_DEV_FALLBACK:
            warnings.warn(
                "Using development fallback token secret. Set SDF_PLAN_TOKEN_SECRET for non-local usage.",
                RuntimeWarning,
                stacklevel=2,
            )
            _WARNED_DEV_FALLBACK = True
        return _DEV_FALLBACK_SECRET.encode("utf-8")
    raise RuntimeError(
        "SDF Plan secret is required outside development. "
        "Set SDF_PLAN_TOKEN_SECRET or configure(SdfPlanConfig(secret=...))."
    )

