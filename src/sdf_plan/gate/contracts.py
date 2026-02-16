from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class GateDecision(str, Enum):
    ALLOW = "ALLOW"
    REQUIRE_CONFIRM = "REQUIRE_CONFIRM"
    BLOCK = "BLOCK"
    WARN = "WARN"


class GateErrorCode(str, Enum):
    INVALID_TOKEN = "INVALID_TOKEN"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TOKEN_TAMPERED = "TOKEN_TAMPERED"
    POLICY_BLOCKED = "POLICY_BLOCKED"


class GateContext(BaseModel):
    workspace_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ToolGateRequest(BaseModel):
    tool_name: str = Field(min_length=1)
    args: Dict[str, Any] = Field(default_factory=dict)
    ctx: Optional[GateContext] = None
    meta: Dict[str, Any] = Field(default_factory=dict)
    policy: Optional[Dict[str, Any]] = None
    run_context: Optional[Dict[str, Any]] = None


class ToolGateResume(BaseModel):
    token: Optional[str] = None
    idempotency_key: Optional[str] = None


class ToolGateResponse(BaseModel):
    decision: GateDecision
    reason: Optional[str] = None
    error_code: Optional[GateErrorCode] = None
    risk_flags: List[str] = Field(default_factory=list)
    confirm_prompt: Optional[str] = None
    resume: Optional[ToolGateResume] = None


class ConfirmRequest(BaseModel):
    token: str = Field(min_length=1)
    user_ok: bool = True


class ConfirmResponse(BaseModel):
    decision: GateDecision
    confirmed: bool
    error_code: Optional[GateErrorCode] = None
    reason: Optional[str] = None
    idempotency_key: Optional[str] = None
