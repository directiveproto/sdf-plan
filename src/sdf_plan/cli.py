from __future__ import annotations

import argparse
import json
from pathlib import Path

from sdf_plan.lint import lint_plan
from sdf_plan.policy import classify_tool, load_tool_risk_map


def _cmd_lint(args: argparse.Namespace) -> int:
    raw = json.loads(Path(args.plan_path).read_text(encoding="utf-8"))
    findings = lint_plan(
        raw,
        max_steps=int(args.max_steps),
        safety_mode=str(args.safety_mode),
    )
    print(json.dumps(findings, indent=2))
    return 1 if any(f.get("level") == "ERROR" for f in findings) else 0


def _cmd_classify(args: argparse.Namespace) -> int:
    risk_map = load_tool_risk_map(version=args.version)
    cls = classify_tool(args.tool, risk_map)
    print(
        json.dumps(
            {
                "tool": args.tool,
                "category": cls.category,
                "risk_flags": list(cls.risk_flags),
                "map_version": args.version,
            },
            indent=2,
        )
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sdf-plan", description="SDF Plan CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    lint_p = sub.add_parser("lint", help="Lint a PlanSpec-like JSON file")
    lint_p.add_argument("plan_path", help="Path to plan JSON file")
    lint_p.add_argument("--max-steps", type=int, default=12)
    lint_p.add_argument("--safety-mode", default="safe")
    lint_p.set_defaults(func=_cmd_lint)

    classify_p = sub.add_parser("classify", help="Classify a tool name")
    classify_p.add_argument("--tool", required=True)
    classify_p.add_argument("--version", default="v2", choices=["v1", "v2"])
    classify_p.set_defaults(func=_cmd_classify)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))

