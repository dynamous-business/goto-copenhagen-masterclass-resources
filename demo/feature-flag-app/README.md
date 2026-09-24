# Demo kit: debugging as a workflow + five ways to say go

The live demos from the afternoon, and a worked example of the `automations/` templates configured for a real
project. `fix-issue.sh` and `fix-issue.py` here are those templates with every marker filled in for the
feature-flag app.

**Run everything from the root of a clean `main` checkout of
[nextjs-feature-flag-exercise](https://github.com/dynamous-business/nextjs-feature-flag-exercise)**, with this
repo cloned next to it. The scripts stay outside that repo so the fix branches and PRs they create contain only
the fix.

Every demo works a **real bug** in this app, filed as a GitHub issue on this repo:

| Issue | Bug | Demo |
|---|---|---|
| #1 | Can't create `dark-mode` in development because it exists in production (409) | **Debugging:** investigate, then fix |
| #2 | Whitespace-only owner and description are accepted | **1 · Headless** script |
| #3 | A rollout of 42.5% is accepted | **2 · Agent SDK** program |
| #4 | Empty and duplicate tags are accepted | **3 · Hooks** (the baton) |
| #5 | You can create a flag that has already expired | **5 · Orchestrator** |
| PR from #2 | | **4 · CI** review on the pull request |

Before any demo, in the exercise repo: `git switch main && git pull`, `cd server && pnpm install && cd ../client && pnpm install`,
then `gh auth status`. Below, `KIT=../goto-copenhagen-masterclass-resources/demo/feature-flag-app`.

## Debugging as a workflow (issue #1)

```
/piv-investigate-issue 1      # parallel exploration, 5 Whys, RCA to docs/issues/issue-1.md + a comment on #1
/piv-implement-issue 1        # fresh session: drift-check the RCA, fix, regression test, docs/issues/fix-report-1.md
```

What to point at: the RCA names two causes, the `UNIQUE` constraint on `name` in `server/src/db/schema.ts` and the
name-only lookup in `createFlag` / `updateFlag`. The fix makes uniqueness per name + environment. The regression
test creates `dark-mode` in both environments.

## Five ways to say go

**1 · Headless** (`fix-issue.sh`, a `claude -p` script)
```bash
$KIT/fix-issue.sh 2
```
Implement, then the real checks run with **no agent involved**. Failures go back to the same session (max 3), then it
opens a PR and two fresh reviewers look at it in parallel. Point at: `run_checks()` is the gate, and `--resume`
keeps the context.

**2 · Agent SDK** (`fix-issue.py`, the same loop as a program)
```bash
$KIT/fix-issue.py 3
```
Point at: the session is an object (no session ids), the `.claude/` layer loads by itself, and `guard()` is asked
about each edit *as it happens*: it refuses any edit to `shared/types.ts` and says why.

**3 · Hooks** (the baton: one skill's artifact starts the next)
```bash
cp .claude/hooks/automation-hooks.settings.json .claude/settings.json
```
Then, in Claude Code: `/piv-investigate-issue 4`. When that session stops, `baton.sh` sees
`docs/issues/issue-4.md` with no fix report and starts `/piv-implement-issue 4` in a fresh `claude -p`. Show
`docs/issues/.baton-4.log` filling up. Point at: nobody asked for the second step. **Remove
`.claude/settings.json` afterwards**; the Stop hooks fire on every session in this repo.

**4 · CI** (`.github/workflows/claude-review.yml`, already on `main`)
Open the PR that demo 1 created. The review posted itself when the PR opened. Comment `@claude-review` for another
pass. Point at: the repo is the trigger, and `contents: read` is the trust boundary.

**5 · Orchestrator**
```
/orchestrate-issues 5
```
One skill runs investigate, then implement (copy `fix-issue.py` to the repo root first, uncommitted: the skill calls `./fix-issue.py`), then PR, then review, as background agents
with gates and a cap, and sends one digest. Point at: "an agent saying done is a claim; a green PR is a fact". The
Archon equivalent is `archon workflow run archon-fix-github-issue` with the same issue.

## Resetting between rehearsals

Close the PRs **without merging** and delete their branches, reopen the issues, then `git switch main && git clean -fd docs/issues`
and remove any `.claude/settings.json` or `fix-issue.py` you copied in. Never merge a demo PR into `main`: `main` is
what attendees clone.
