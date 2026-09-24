---
name: skills-create
description: "Changes an existing Claude Code skill so it works the user's way, and creates new skills from scratch. Use this whenever the user wants to edit, customize, adapt, fix, tune, improve, or \"make mine\" a skill that already exists - INCLUDING when they simply name a skill and describe what it should do differently, without ever saying \"edit a skill\". Triggers: a skill that isn't firing or fires too often, runs commands the project doesn't have, ignores their conventions, never asks them anything, produces the wrong shaped output, or has a bloated SKILL.md. Also use to create a new skill, write a skill, or turn a repeated prompt into one, and when the user invokes /skills-create. The meta-skill: a skill that builds and improves skills."
argument-hint: "[what you want, e.g. 'a skill that runs our release checklist' | 'make piv-plan-implementation interview me first' | 'refactor <path/to/SKILL.md>']"
---

# Skills Create: the meta-skill

A skill that authors and improves skills. Two jobs:

- **Create** a new skill from scratch (or port an existing prompt / command file).
- **Adapt** an existing skill so it works *your* way: retarget its triggering, localize its commands, encode your
  conventions, add an interview, compose subagents or CLIs, shape its output, or split a fat body into references.

Most real work is **adapt**. A skill is rarely wrong on its first day; it drifts as the project moves, or it
arrives generic from a pack and has to be made yours. Treat adapting as the main road, not a cleanup chore.

**It's built the way it teaches:** a lean body that defers detail to `references/`. That's progressive
disclosure, and this skill is its own worked example. **It's all composable markdown:** a skill is a
`SKILL.md` plus optional files the agent loads only when it reaches for them.

## Prescribe the craft, not the content

Be **strict on how a skill is built** and **agnostic on what any given skill, or its output, should contain.**

- **Prescribe (firm, universal):** progressive disclosure, a third-person trigger-rich `description`, an
  imperative lean body, no duplication, every bundled file wired, deliberate invocation control, validation that
  fits the skill type. (See `references/skill-standards.md`.)
- **Do NOT prescribe (the author's call):** the sections a plan / PRD / report should have, the domain vocabulary,
  the output shape, which phases exist. There is no canonical output. Guide the author to a good decision, never
  hand them a fixed one.

Strict on the craft so the author stays free on the content. *(Guide, don't prescribe — and take-vs-build: you
**build** a skill when you own the process and want it to follow YOUR way.)*

## Classify the skill first

Pin the **type** before applying the craft, in either mode. The guidance is proportional, not one-size-fits-all:

| Type | What it is | Apply |
|---|---|---|
| **Workflow** | a multi-step procedure (plan, review, ship) | the full lens incl. verifiable validation gates |
| **Artifact-generator** | produces a document/output | Context-is-King + a *suggested* (never mandated) output shape |
| **Knowledge / reference** | facts the agent consults | Context-is-King + information-dense; **no** phases, **no** validation loop |
| **Tool-wrapper** | drives a script / CLI / API | a deterministic script + sharp triggers; validation = the tool's own exit code |

A skill can blend types, so apply the union of what fits. Never force a workflow's machinery (phases, loops,
output skeletons) onto a knowledge skill. Full detail: `references/skill-standards.md` -> Skill types.

## Step 0: route the request

Read **`$ARGUMENTS`** and decide which job this is. Infer it; only ask when genuinely ambiguous.

| The request | Mode | Follow |
|---|---|---|
| a capability that doesn't exist yet ("a skill that...", "turn this prompt into a skill", `create <name>`) | **Create** | `references/creating-skills.md` |
| anything aimed at a skill that already exists: names one, points at a path, describes a change, reports a misbehavior, or says `refactor <path>` | **Adapt** | `references/adapting-skills.md` |
| genuinely unclear | ask **one** question: a new skill, or a change to one you already have? | |

**Resolve the target before working.** In Adapt mode, locate the actual `SKILL.md` (search `.claude/skills/` and
`~/.claude/skills/`). If the name is a near-miss or matches several, confirm which skill is meant. Never guess at
the target: editing the wrong skill is worse than asking.

Both modes obey the same craft rules, so read `references/skill-standards.md` first.

## Create: quick spine (full detail: `references/creating-skills.md`)

1. **Gather context** - the literal phrases that should trigger it, the task start to finish, the gotchas, the
   patterns to mirror. Ask the user; don't write yet.
2. **Plan the resources** - what repeats -> `scripts/`; what informs the work -> `references/`; what shapes the
   output -> `templates/`; what you don't own or what changes upstream -> cite a path/URL; what only exists at
   runtime -> gather it (ask the user, read git/codebase).
3. **Scaffold** - copy `templates/SKILL.template.md` to `.claude/skills/<name>/SKILL.md`; add `references/` and
   `templates/` only as the plan needs.
4. **Write the spine first** - third-person trigger-rich `description`, imperative lean body, detail pushed to
   references. Get it *triggering* before you write the references.
5. **Validate and iterate** - `references/validation.md` (checklist -> trigger test -> run it for real).

## Adapt: quick spine (full detail: `references/adapting-skills.md`)

1. **Read the target and keep a baseline.** Read the whole `SKILL.md` and its bundled files before proposing
   anything. Preserve the original so the change can be compared and reverted: a git commit if the repo is clean,
   otherwise a copy alongside it.
2. **Interview.** Do not start editing from a one-line ask. Ask the four questions below.
3. **Route to a change pattern** using the table. Name the pattern out loud so the author knows what is changing
   and why.
4. **Make the smallest change that does it.** Edit in place, and preserve everything the author didn't ask to
   change. If the skill genuinely needs a rewrite, say so and get agreement before starting one.
5. **Verify the change is real** against the case from question 4, then run `references/validation.md`.

### The interview (ask these, in this order)

1. **What happened, or what's missing?** Get the concrete case: the run where it went wrong, or the thing it
   never does. "Show me the last time it disappointed you" beats any abstract answer.
2. **What should it have done instead?** This is *their* way, the part only they know. Push for specifics: the
   actual command, the actual convention, the actual question it should have asked first.
3. **Always, or just this once?** A rule the skill should always follow belongs in the skill. A one-off belongs
   in the prompt. Not every correction earns a permanent line.
4. **How will we know it worked?** The case to re-run at step 5. Without this there is no verification, only hope.

Ask only what's missing. If `$ARGUMENTS` already answers a question, skip it and say so.

### Change patterns (route the interview's answers here)

| The symptom | Pattern | Where the change lands |
|---|---|---|
| never fires, or fires on the wrong requests | **Retarget** | `description` / `when_to_use` / invocation flags |
| runs commands that don't exist in this project | **Localize** | body: real commands, real paths, real working directory |
| ignores how this team actually does things | **Encode conventions** | body: an explicit constraints section |
| guesses instead of asking the calls that matter | **Add an interview** | body: a question gate before it commits |
| explores inline, or ignores a tool it should drive | **Compose** | body: dispatch subagents, a CLI, or an MCP tool |
| right process, wrong shaped output | **Shape the output** | `templates/` + a mandatory-read line |
| body is long and most of it is rarely needed | **Split and trim** | `references/` (see `references/refactoring-skills.md`) |

Patterns combine. Apply the ones the interview actually surfaced, and no more.

> **The #1 adapt risk: rewriting more than was asked.** The author knows this skill and chose most of what's in
> it. Silent changes to the parts they were happy with destroy their trust faster than the original flaw did.
> Change what the interview justified, leave the rest, and report exactly what moved.

## When to build, and when to adapt

Build a new skill when you **own a process** and want the agent to follow *your* way of it, repeatedly: the
take-vs-build rule. A rough threshold is the Rule of Three, so once you've prompted the same thing about
three times, bank it. Don't build for a one-off, or for a tool whose owner already ships a good skill.

**Prefer adapting to creating when something close already exists.** A pack skill that is eighty percent right and
already wired into a loop is worth more than a new skill that is perfect and wired into nothing. Create a rival
only when the capability is genuinely different, never just because the existing one is generic: generic is the
starting point you adapt. Two skills competing for the same trigger is worse than one imperfect skill.

## Resources

- `references/skill-standards.md` - the craft rules: skill types, anatomy, context sources, frontmatter spec,
  progressive disclosure, writing voice, no-duplication, "structure implies a maintainer", wiring, portability.
- `references/creating-skills.md` - the full create runbook (incl. porting an existing prompt or command file).
- `references/adapting-skills.md` - the full adapt runbook: the interview, every change pattern in detail, and
  how to verify a change is real.
- `references/refactoring-skills.md` - the split-and-trim pattern in depth, with a before/after.
- `references/validation.md` - the validation gates (structure, description, body, disclosure, change
  verification, trigger test).
- `templates/SKILL.template.md` - the lean SKILL.md skeleton to scaffold from.
