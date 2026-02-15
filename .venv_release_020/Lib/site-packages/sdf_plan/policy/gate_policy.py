from __future__ import annotations

from enum import Enum

from pydantic import BaseModel

from sdf_plan.gate.contracts import GateDecision


class VerifyBeforeWriteMode(str, Enum):
    OFF = "OFF"
    WARN = "WARN"
    ENFORCE = "ENFORCE"


class GatePolicy(BaseModel):
    unknown_tool: GateDecision = GateDecision.REQUIRE_CONFIRM
    write_requires_confirm: bool = True
    require_idempotency_for_write: bool = True
    verify_before_write: VerifyBeforeWriteMode = VerifyBeforeWriteMode.WARN
    strict_mode: bool = False
