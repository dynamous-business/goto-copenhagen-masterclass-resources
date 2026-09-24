---
name: ai-layer-review
description: "Reviews a change to the AI layer itself (CLAUDE.md, AGENTS.md, anything under .claude/, engineering.md, direction.md) the way code gets reviewed: is each new rule a specific choice that earned its place, is the rules file still under budget, should a machine-checkable rule graduate to lint or CI, does a skill diff have a real trigger and wired references. Use whenever a PR or diff touches the AI layer, when the user says 'review the AI layer change', 'review this rule', 'review this skill diff', 'AI layer PR', or before merging any change to rules, skills, hooks, or steering documents, even if they only ask for a normal review. Do NOT use for ordinary code changes; that is piv-review-changes."
argument-hint: "[pr-number | branch | diff range]   (blank = the working tree against HEAD)"
allowed-tools: Read, Grep, Glob, Write, Bash(git *), Bash(gh pr *), Bash(wc *), Bash(ls *)
---

# AI layer review

The AI layer is reviewed like code because it is read on every run: a vague rule costs tokens on every task
and is followed by nobody, a stale rule misleads the agent, and a skill with a weak description never fires.
This skill reviews only the AI-layer part of a change and routes findings by who acts on them.

## 1. Collect the AI-layer diff

**Input:** `$ARGUMENTS`

Resolve the input above (it may be blank), then produce the diff limited to AI-layer paths:

- **No argument:** `git diff HEAD -- CLAUDE.md AGENTS.md CLAUDE.local.md .claude engineering.md direction.md`
  plus untracked files under those paths (`git ls-files --others --exclude-standard -- .claude`).
- **A PR number or URL:** `gh pr diff <N>` filtered to the same paths, plus `gh pr view <N> --json title,body`.
- **A branch or range:** `git diff <range> -- <paths>`.

If the diff touches none of these paths, say so and stop: this skill has nothing to review.

Read every changed AI-layer file in full, not just the hunks, and read the unchanged neighbours it interacts
with: the rules file when a reference changes, the references when the rules file changes, the steering
documents when either changes.

## 2. Apply the checklist

Read `references/checklist.md` and apply every item that fits the kind of file changed. Verify each finding
against the actual files (count the lines, grep for the duplicate, open the referenced file) before reporting
it. Do not report style preferences.

## 3. Route the findings and write the report

Route every finding into exactly one bucket, each item with `file:line` and a one-line fix:

- **AGENT FIXES** - mechanical: over-budget line count, a reference path that does not resolve, a dead file,
  a description written in the wrong voice, a machine-checkable rule that should move to lint or CI with the
  check named.
- **HUMAN DECIDES** - judgment: a rule with no rationale, a rule that contradicts another, a slogan that needs
  a specific choice, a steering-document edit that changes what the project is.
- **HUMAN READS** - load-bearing changes the reviewer must read in full: any edit to `engineering.md` or
  `direction.md`, any change to a hook command, any change to a skill's `allowed-tools`.
- **HUMAN TESTS** - a change only a run can verify: a new hook command, a skill whose behavior changed. Usually
  empty for a layer diff; keep the heading so the report has the same five buckets as `conventions.md`.
- **FYI** - observations with no action.

Save the report to `.claude/code-reviews/ai-layer-<branch-or-pr>.md` with the buckets above, then print it.
If nothing was found: "AI layer review passed. No findings." and still save the report.

Keep human buckets to five items or fewer; if there are more, the change is too big to review as one PR and
that is the first finding.
