# Conventions — how this project ships work

> **Edit this file to match YOUR way of working.** This is the one place your ship-step conventions live, and
> **three layers enforce it from this single source:**
> 1. **The skills read it at run time** — `piv-commit` and `piv-create-pr` follow the rules below, so the agent
>    writes your way instead of a generic default.
> 2. **The regex asserts** in `evals/cases.yaml` are derived from the **mechanical** rules here — the cheap,
>    deterministic guard on form.
> 3. **The judge rubrics** quote the **judgment** rules here — the substance grade.
>
> When you change a convention, update the matching assert. The skills stay general and portable; what's
> specific to this project lives here, travels with the repo, and is inherited by anyone who clones it.
>
> Shipped defaults = Cole's house style. Replace them with yours.

## commit

**Mechanical (regex-checkable):**
- Subject line uses a conventional tag: `feat|fix|docs|refactor|test|chore(scope)?:` — imperative, ≤72 chars.
- No AI attribution anywhere in the message: no "Generated with", no "Co-Authored-By: Claude".

**Judgment (rubric for the judge):** <!-- #commit-quality -->
- The message describes THIS diff — what changed and why — not a generic summary. A reader who sees only the
  message should predict roughly which files changed and not be surprised by the body of the diff.
- Subject says what the change does, body (when present) says why it was needed.

## pr

**Mechanical (regex-checkable):**
- PR body contains the sections: `## Summary`, `## What changed`, `## Validation`.
- No AI attribution in the body.

**Judgment (rubric for the judge):** <!-- #pr-quality -->
- The Summary explains WHY this change exists (the intent), not just what it touches.
- Validation states what was actually run/verified — not aspirational.

## review

**Mechanical (regex-checkable):**
- The report routes every item into one of: AGENT FIXES / HUMAN DECIDES / HUMAN READS / HUMAN TESTS / FYI.
- Every item carries a `file:line` reference. Human buckets hold 3–5 items max.

**Judgment (rubric for the judge):** <!-- #review-routing -->
- HUMAN READS points at genuinely load-bearing code for THIS diff (auth, money, data integrity, public
  contracts) — not a random sample of touched files.
- Nothing auth- or security-adjacent sits in AGENT FIXES.
