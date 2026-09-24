# GitHub Actions — Agents in CI

These **GitHub Actions workflows** run agents *outside your terminal* — in CI,
triggered by PR comments, issues, or tags.

CI/CD is the simpler form of "agents running outside your IDE": more familiar
than a workflow engine, a natural stepping stone before Archon. Once an agent
can act on a `@claude` mention in a PR, the leap to full workflow orchestration
(`.archon/workflows/`) makes sense.

These are **templates**: they live here, not in `.github/workflows/`, so they never run on this repo. Copy the
ones you want into your own project's `.github/workflows/`.

## The three trust patterns

GitHub-Action agents differ in *how much* of the flow the agent owns:

1. **Claude hybrid** (`claude-create.yml`) — the agent implements and pushes a
   draft PR; a human still reviews and merges. The agent never owns that last step.
2. **Claude read-only** (`claude-review.yml`) — the agent reads the diff and
   comments. `contents: read` — it cannot touch the branch at all.
3. **Codex deterministic** (`codex-create-deterministic.yml`) — the workflow YAML
   owns every git operation; the agent *only* edits files. The most constrained,
   most predictable pattern.

## The workflows

| File | Trigger | What it does |
|------|---------|--------------|
| `claude-create.yml` | `@claude` comment on an issue/PR, or `@claude` in a new issue body | Claude implements the requested change and opens a draft PR (hybrid trust). |
| `claude-review.yml` | PR opened / `ready_for_review`, or `@claude-review` comment | Runs the `piv-review-pr` skill on the PR and posts the review as a comment (read-only). |
| `codex-create-deterministic.yml` | `@codex-create <request>` comment on an issue | Codex deterministic pattern — the YAML owns git + PR creation, the agent only writes code. |
| `release-notes.yml` | A `v*` tag is pushed (or run manually) | Claude generates release notes from the commits since the previous tag and publishes a GitHub Release. |

Every trigger is gated by `author_association` (`OWNER` / `MEMBER` /
`COLLABORATOR`) so only trusted contributors can invoke an agent — forks and
drive-by commenters cannot.

## Security setup

These workflows need API tokens stored as **GitHub Actions secrets** — never
committed:

- `CLAUDE_CODE_OAUTH_TOKEN` — for the Claude workflows. Generate with
  `claude setup-token`.
- `OPENAI_API_KEY` — for the Codex workflow.

Add them under **Settings → Secrets and variables → Actions**.
