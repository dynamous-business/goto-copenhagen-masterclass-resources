# AI layer review checklist

Apply the sections that match the files in the diff. Every item names its bucket.

## Rules files (`CLAUDE.md`, `AGENTS.md`, `.claude/rules/*.md`)

- **Budget** (AGENT FIXES): the file is under 200 lines after the change (Anthropic's stated target; longer
  files reduce adherence). Count with `wc -l`. Over budget: name the sections that should move to a
  reference doc, a path-scoped rule, or a skill.
- **A choice, not a slogan** (HUMAN DECIDES): every new rule states a specific decision the agent could act
  on. "Write clean code" and "type safety is critical" are slogans; "derive types with `z.infer`, never
  hand-write parallel interfaces" is a choice.
- **Earned its place** (HUMAN DECIDES): a new rule names, in the PR body or a trailing rationale, the
  failure or decision that produced it. A rule nobody can trace to a failure is a rule nobody will defend
  when it drifts. Ask for the failure, not the rule.
- **Graduation** (AGENT FIXES): a rule a machine could check (indentation, import order, a banned call, a
  required file header, a max line length) belongs in lint, a type, or a CI check, and then leaves the
  file. Name the check that would enforce it.
- **Duplicates and contradictions** (HUMAN DECIDES): grep the rules file, `.claude/rules/`,
  `.claude/references/`, `engineering.md`, and `direction.md` for the same topic. Two rules on one topic
  in two places drift; two that disagree let the agent pick.
- **Truth** (AGENT FIXES): a rule that names a path, command, or file must match the codebase today.
  Verify with `ls` or `grep`.

## Reference docs (`.claude/references/*.md`)

- **Reachable** (AGENT FIXES): something points at it (the rules file, a skill, a hook). A reference nothing
  loads is dead weight.
- **On demand for a reason** (FYI): content that every task needs belongs in the rules file; content one
  task type needs belongs here. Note when the split looks inverted.

## Steering documents (`engineering.md`, `direction.md`)

- **Human-authored** (HUMAN READS): every edit to a steering document is an operator decision. If the PR
  was produced by an agent run, the edit is a proposal; flag it for a human to promote or reject.
- **Judgment, not enforcement** (AGENT FIXES): an `engineering.md` entry that a linter could check should
  graduate out. A `direction.md` entry that is a task, not a direction, belongs in the tracker.
- **Cite-able** (AGENT FIXES): every `direction.md` clause has a `§name` a triage can cite.
- **Drift** (HUMAN DECIDES): an entry contradicted by the current codebase is deleted, not annotated.

## Skills (`.claude/skills/*/SKILL.md` and their folders)

- **Trigger** (AGENT FIXES): the `description` is third person, states what it does and when to use it,
  and carries the literal phrases a user would type. First person or "helps with X" does not fire.
- **Name matches folder** (AGENT FIXES): `name:` equals the directory name.
- **Wired resources** (AGENT FIXES): every file under `references/`, `templates/`, `scripts/` is mentioned
  in `SKILL.md`; every path `SKILL.md` mentions exists.
- **Arguments** (AGENT FIXES): named `arguments:` or `$ARGUMENTS`; no shell-style `$1` (positional args are
  zero-indexed and this is the most common authoring bug).
- **Body budget** (FYI): body under roughly 2,000 words; detail lives in `references/`.
- **Tool grants** (HUMAN READS): any change to `allowed-tools` widens what runs without a prompt, in CI
  too. Read it.

## Hooks (`.claude/settings.json`, `.claude/hooks/*`)

- **Runs real code** (HUMAN READS): every new or changed hook command is read in full, the same way a CI
  script is.
- **Exit codes** (AGENT FIXES): a blocking hook exits 2; exit 1 does not block.
- **Guarded** (HUMAN DECIDES): the hook reads the state of the world before acting (a dirty tree, an
  artifact present), because it fires every time and has no memory.

## The whole change

- **One concern** (HUMAN DECIDES): a PR that changes rules, a skill, and a steering document at once is
  three reviews. Ask for a split when the human buckets exceed five items.
- **Reviewable by anyone who uses the layer** (FYI): the PR body says what changed in the agent's
  behaviour, so a teammate who has never opened `SKILL.md` can still judge it.
