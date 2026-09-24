# Archon Workflows

YAML DAG workflows for the [Archon](https://github.com/coleam00/Archon) workflow
engine. Each file is a directed graph of nodes — AI prompts, bash steps, and
sub-workflows — that Archon runs with worktree isolation.

Run one with:

```bash
archon workflow run <name> --branch <branch-name> "<your request>"
```

| Workflow | What it does | Use when |
|----------|--------------|----------|
| `piv-loop` | Interactive Plan → Implement → Validate loop with a human in the loop at the Explore, Plan-review, and Validate gates. | You want guided, reviewable development of one feature or bug fix. |
| `parallel-implementation` | Splits a feature into file-disjoint lanes, builds each in its own git worktree concurrently, then merges and validates the whole. | A feature decomposes into independent slices and you want wall-clock speed. |
| `github-issue-fix` | Classifies a GitHub issue, researches it, implements the fix, opens a draft PR, runs a smart multi-agent review, self-fixes findings, and reports back to the issue. | You want an issue taken from triage to reviewed draft PR autonomously. |

`piv-loop` and `parallel-implementation` are fully self-contained (inline prompts).
`github-issue-fix` references Archon's bundled `archon-*` commands for its research,
validation, and review nodes.
