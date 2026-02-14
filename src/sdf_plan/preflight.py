from __future__ import annotations

from functools import wraps
from typing import Any, Callable, Dict, List

from sdf_plan.lint import lint_plan


class LintError(ValueError):
    def __init__(self, findings: List[Dict[str, Any]]):
        self.findings = findings
        super().__init__("Plan failed lint preflight.")


def _run_preflight(plan: Dict[str, Any], max_steps: int, safety_mode: str, fail_on_error: bool) -> List[Dict[str, Any]]:
    findings = lint_plan(plan, max_steps=max_steps, safety_mode=safety_mode)
    if fail_on_error and any(item.get("level") == "ERROR" for item in findings):
        raise LintError(findings)
    return findings


def preflight_lint(
    plan_or_fn: Dict[str, Any] | Callable[..., Dict[str, Any]] | None = None,
    *,
    max_steps: int = 12,
    safety_mode: str = "safe",
    fail_on_error: bool = True,
):
    """Run lint directly or use as a decorator.

    Direct call:
      preflight_lint(plan, max_steps=12)

    Decorator:
      @preflight_lint(max_steps=12)
      def build_plan(...): ...
    """
    if plan_or_fn is None:
        def decorator(fn: Callable[..., Dict[str, Any]]):
            return preflight_lint(fn, max_steps=max_steps, safety_mode=safety_mode, fail_on_error=fail_on_error)

        return decorator

    if callable(plan_or_fn):
        fn = plan_or_fn

        @wraps(fn)
        def wrapped(*args, **kwargs):
            plan = fn(*args, **kwargs)
            _run_preflight(plan, max_steps=max_steps, safety_mode=safety_mode, fail_on_error=fail_on_error)
            return plan

        return wrapped

    return _run_preflight(plan_or_fn, max_steps=max_steps, safety_mode=safety_mode, fail_on_error=fail_on_error)
