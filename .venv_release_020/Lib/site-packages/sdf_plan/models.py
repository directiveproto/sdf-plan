from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class TypedIOField(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    key: str
    json_schema: Optional[Dict[str, Any]] = Field(default=None, alias="schema")


class StepIO(BaseModel):
    inputs: List[TypedIOField] = Field(default_factory=list)
    outputs: List[TypedIOField] = Field(default_factory=list)


class StepStop(BaseModel):
    kind: Literal["string", "dsl"] = "string"
    hint: Optional[str] = None
    expr: Optional[str] = None


class StepPolicy(BaseModel):
    requires_confirm: bool = False
    confirm_prompt: Optional[str] = None
    risk_flags: List[str] = Field(default_factory=list)


class PlanStep(BaseModel):
    id: str
    type: str
    title: str
    intent: str
    inputs: List[str] = Field(default_factory=list)
    outputs: List[str] = Field(default_factory=list)
    depends_on: List[str] = Field(default_factory=list)
    stop_condition: str
    fallback: str
    retry: int = 0
    time_budget_sec: int = 0
    confirm: Optional[str] = None

    stop: Optional[StepStop] = None
    policy: Optional[StepPolicy] = None
    idempotency_key: Optional[str] = None
    io: Optional[StepIO] = None


class LintItem(BaseModel):
    level: Literal["WARN", "ERROR"]
    code: str
    message: str
    step_id: Optional[str] = None


class UsageInfo(BaseModel):
    billable_units: int
    plan_steps: int
    latency_ms: int
    cache_hit: bool = False


class ProvenanceInfo(BaseModel):
    template_version: str
    rules_fired: List[str] = Field(default_factory=list)
    lint_rules_evaluated: List[str] = Field(default_factory=list)


class PolicySummary(BaseModel):
    risk_flags_count: int
    confirm_required_steps_count: int


class PlanSpecEnvelope(BaseModel):
    plan_id: str
    version: str = "sdf.v1.2"
    template_key: str
    confidence: float
    mode_used: str = "deterministic"
    goal_spec: Dict[str, Any] = Field(default_factory=dict)
    steps: List[PlanStep] = Field(default_factory=list)
    lint: List[LintItem] = Field(default_factory=list)
    usage: Optional[UsageInfo] = None
    provenance: Optional[ProvenanceInfo] = None
    policy_summary: Optional[PolicySummary] = None
