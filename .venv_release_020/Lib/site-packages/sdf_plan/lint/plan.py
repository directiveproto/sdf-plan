from __future__ import annotations

from typing import Any, Dict, List, Set


def lint_plan(plan: Dict[str, Any], max_steps: int, safety_mode: str = "safe") -> List[Dict[str, Any]]:
    steps = plan.get("steps", []) or []
    lint: List[Dict[str, Any]] = []

    if len(steps) > max_steps:
        lint.append(_warn("PLAN_TOO_LONG", f"Plan has {len(steps)} steps; max_steps={max_steps}", None))

    for s in steps:
        sid = s.get("id")
        if not s.get("stop_condition"):
            lint.append(_error("MISSING_STOP_CONDITION", "Missing stop_condition", sid))
        elif _unverifiable_stop_condition(s.get("stop_condition", "")):
            lint.append(_warn("UNVERIFIABLE_STOP", "Stop condition may be hard to verify automatically", sid))
        if not s.get("fallback"):
            lint.append(_error("MISSING_FALLBACK", "Missing fallback", sid))

    if _has_cycle(steps):
        lint.append(_error("CYCLE_DETECTED", "Dependency cycle detected", None))

    out_to_steps: Dict[str, List[str]] = {}
    for s in steps:
        for out in (s.get("outputs") or []):
            out_to_steps.setdefault(str(out), []).append(s.get("id"))
    for out, sids in out_to_steps.items():
        if len(sids) > 1:
            lint.append(_warn("DUPLICATE_OUTPUT_KEY", f"Output key {out} produced by {sids}", sids[0]))

    last_step_id = steps[-1].get("id") if steps else None
    consumed_keys: Set[str] = set()
    for s in steps:
        for k in (s.get("inputs") or []):
            consumed_keys.add(str(k))
    for out, sids in out_to_steps.items():
        if out not in consumed_keys:
            if sids and sids[0] == last_step_id:
                continue
            lint.append(_warn("UNUSED_OUTPUT", f"Output key {out} not consumed downstream", sids[0]))

    for s in steps:
        if s.get("type") == "ACT" and not s.get("idempotency_key"):
            lint.append(_error("ACT_WITHOUT_IDEMPOTENCY", "ACT step is missing idempotency_key", s.get("id")))

    if safety_mode == "safe":
        for s in steps:
            if s.get("type") == "ACT" and _looks_like_external_write(s.get("intent", "")):
                policy = s.get("policy") or {}
                requires_confirm = bool(policy.get("requires_confirm")) or bool(s.get("confirm"))
                if not requires_confirm:
                    lint.append(
                        _error(
                            "WRITE_WITHOUT_CONFIRM",
                            "ACT step appears to have external side effects; confirm gate required",
                            s.get("id"),
                        )
                    )

        act_ids = [s.get("id") for s in steps if s.get("type") == "ACT" and _looks_like_external_write(s.get("intent", ""))]
        if act_ids:
            has_verify = any(s.get("type") in {"VERIFY", "CONFIRM"} for s in steps)
            if not has_verify:
                lint.append(_warn("NO_VERIFY_BEFORE_WRITE", "Plan contains ACT writes but no VERIFY/CONFIRM step", act_ids[0]))

    return lint


def _warn(code: str, msg: str, step_id: str | None) -> Dict[str, Any]:
    return {"level": "WARN", "code": code, "message": msg, "step_id": step_id}


def _error(code: str, msg: str, step_id: str | None) -> Dict[str, Any]:
    return {"level": "ERROR", "code": code, "message": msg, "step_id": step_id}


def _looks_like_external_write(intent: str) -> bool:
    t = intent.lower()
    keywords = [
        "send",
        "email",
        "post",
        "tweet",
        "publish",
        "charge",
        "pay",
        "buy",
        "book",
        "reservation",
        "delete",
        "remove",
        "update",
        "write",
        "commit",
        "submit",
        "upload",
        "transfer",
    ]
    return any(k in t for k in keywords)


def _has_cycle(steps: List[Dict[str, Any]]) -> bool:
    graph: Dict[str, List[str]] = {}
    for s in steps:
        sid = s.get("id")
        if not sid:
            continue
        graph[sid] = list(s.get("depends_on") or [])

    visited: Set[str] = set()
    stack: Set[str] = set()

    def dfs(n: str) -> bool:
        visited.add(n)
        stack.add(n)
        for m in graph.get(n, []):
            if m not in visited:
                if dfs(m):
                    return True
            elif m in stack:
                return True
        stack.remove(n)
        return False

    for node in graph.keys():
        if node not in visited:
            if dfs(node):
                return True
    return False


def _unverifiable_stop_condition(stop_condition: str) -> bool:
    text = (stop_condition or "").strip().lower()
    if not text:
        return True
    if text.startswith("step s") and text.endswith("completed"):
        return True
    if text in {"checks pass", "done", "complete"}:
        return True
    return False
