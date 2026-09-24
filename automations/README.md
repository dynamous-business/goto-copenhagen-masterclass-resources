# Automations - the four shapes

Everything in the AI Layer so far runs because *you* are sitting there. Automation is what you reach for when
the loop should run without you: on a schedule, on a git event, on a comment in a pull request, or across
several issues at once while you do something else.

There are four shapes it can take. They are not a ladder, and a real system usually ends up with more than one.

| Shape | Runs | Reach for it when | Live example |
|---|---|---|---|
| **1. Headless script** | Your terminal, cron, anywhere a shell runs | You want the loop as a *script*: stages you can read top to bottom, a deterministic check between them, and a hard cap on retries | [`fix-issue.sh`](fix-issue.sh) (template) |
| **2. SDK program** | Your terminal, or inside a larger app | The script has outgrown a shell: you need the session as an object, real data structures, or a say in tool calls *as they happen* | [`fix_issue.py`](fix_issue.py) (template) |
| **3. Hooks** | Automatically, on a lifecycle event | Something must happen *every single time* and the agent must not get a vote | [`.claude/hooks/`](../.claude/hooks/) |
| **4. CI** | GitHub Actions, on a push, PR, comment, or tag | The trigger belongs to the repo rather than to your machine, and the result should land where the team already looks | [`github-workflows/`](github-workflows/) |

## Choosing between them

**Script vs SDK** is the only pair that's genuinely a choice about the same job. Start with the script. Move to
the SDK when you find yourself parsing JSON to keep track of a session, passing structured data between stages,
or wanting to approve and deny individual tool calls mid-turn. `fix-issue.sh` and `fix_issue.py` are the same
loop written both ways, deliberately, so the difference is visible line by line.

**Hooks are not an alternative to either.** A hook is the layer underneath: it fires on the agent's lifecycle
events, so it applies to interactive sessions, scripts, SDK programs, and CI runs alike. A rule asks the agent
to behave; a hook guarantees it. See [`.claude/hooks/README.md`](../.claude/hooks/README.md).

**CI is about the trigger, not the agent.** The same work moves to GitHub Actions when it should fire on a
`@claude` comment or a tag instead of on you typing. The trade is that CI has no memory of your machine and no
human in the room, so the trust boundary has to be explicit in the YAML. The four workflows in
[`github-workflows/`](github-workflows/) show three different answers to how much of the flow the agent is
allowed to own.

Above all four sits the **orchestrator**: a skill that runs the whole pipeline through background agents,
with gates, a cap, and a digest. See [`.claude/skills/orchestrate-issues/`](../.claude/skills/orchestrate-issues/).

## Composing your own

Each shape has a `compose-*` skill that walks you through building one for a real process of yours, rather
than adapting somebody else's example:

- [`compose-headless-workflow`](../.claude/skills/compose-headless-workflow/) - a `claude -p` script
- [`compose-sdk-workflow`](../.claude/skills/compose-sdk-workflow/) - an Agent SDK program
- [`compose-hook-workflow`](../.claude/skills/compose-hook-workflow/) - a lifecycle hook
- [`compose-ci-workflow`](../.claude/skills/compose-ci-workflow/) - a CI workflow
- [`compose-orchestrator`](../.claude/skills/compose-orchestrator/) - an orchestrating skill

## The two files here are templates

`fix-issue.sh` and `fix_issue.py` are **reference templates, not runnable scripts**. They are here to be read
and copied, in the same spirit as `.claude/CLAUDE.md.template`. Every project-specific value has been replaced
with a marker that looks like this:

```
<<< CONFIGURE: ... >>>
```

To use one: copy it to **your own repo root**, then replace every marker before the first run. Each script's
header block lists exactly what needs configuring and what it expects to be installed. The two that matter in
both files are the same two: the directory your checks run in, and your project's real check chain.

The check chain is the load-bearing part. Those commands are the entire gate between "the agent says it fixed
it" and "it is fixed", so they must be the same checks you'd run before opening a pull request, and each one
must **exit non-zero on failure**. A check that prints `FAILED` and exits 0 turns the whole loop into theatre.

Left unconfigured, both templates fail loudly rather than pretending to pass. That's on purpose.
