# Steering documents (templates)

Two long-form documents the plan, implement and review skills read **only when they exist**, so they cost
nothing on the tasks that don't need them:

| File | Read by | What it holds |
|---|---|---|
| `engineering.md` | `piv-implement`, `piv-implement-issue`, `piv-review-changes`, `piv-review-pr` | What code in this project is judged against. Review findings cite its rules by name |
| `direction.md` | `piv-plan-implementation`, `plan-architecture`, `piv-slice-epic` | What the project is and is not. A request that conflicts with a clause gets flagged, citing the clause, instead of planned around |

These ship with the course's demo codebase (the AI Tutor) filled in as a worked example. **Rewrite them for
your project** before copying them to `.claude/references/`; until then they would steer the agent wrong,
which is why they don't live in `.claude/` here. `.claude/skills/ai-layer-review` reviews changes to them like
code.
