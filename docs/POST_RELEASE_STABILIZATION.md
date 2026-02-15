# Post-Release Stabilization (v0.2.x)

## Objective
Stabilize ToolGate-first adoption with fast parser and policy fixes while avoiding adapter over-expansion.

## Day 10+ Checklist

1. Monitor parser shape gaps.
- Track issues where OpenAI/generic payload variants fail normalization.
- Add fixtures before adding parser branches.

2. Monitor policy default friction.
- Review user reports of false-positive blocking.
- Prefer policy tuning/docs updates before behavior changes.

3. Patch release policy.
- Use `0.2.1` for parser compatibility and low-risk fixes.
- Keep adapter additions out of patch releases unless critical.

4. Adapter scope discipline.
- Keep official support focused on LangGraph in `0.2.x` until usage justifies expansion.
- CrewAI/LangChain remain next milestones, not release blockers.

5. Regression guard.
- Every fix requires:
  - contract tests
  - relevant integration tests
  - adapter contract tests (if adapter path affected)

## Exit Criteria
- Early adopters integrate without custom forks.
- Common tool-call payload variants normalize without manual patches.
- No critical regressions in ToolGate contract behavior.
