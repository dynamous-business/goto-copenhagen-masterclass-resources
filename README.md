# Agentic Engineering Masterclass: GOTO Copenhagen 2026

**The New Software Development Lifecycle** · Cole Medin · Tuesday 29 September 2026

Almost every developer has an AI coding tool now. Almost nobody has a *system* for getting reliable results from
it, and that gap, not the model, is what separates the people pulling ahead. This masterclass builds that system:
an **AI Layer** in your codebase (rules, skills, subagents, hooks and references) and the loop you run it through
on every ticket.

This repository is the AI Layer we use all day. It is the same one taught in the
[Agentic Coding Course](https://dynamous.ai), and after today it's yours to copy into your own projects.

---

## Setup: paste this into Claude Code

You need a laptop with **Git**, **VS Code** and **[Claude Code](https://code.claude.com)** on a paid plan (Max is
ideal for a full day). Clone this repo, open Claude Code in it, and paste:

```text
Set up my machine for the Agentic Engineering masterclass. Check what's already installed first and only
install what's missing:

1. Node.js 20 or newer
2. pnpm (npm install -g pnpm)
3. uv (https://docs.astral.sh/uv/getting-started/installation/)
4. agent-browser: npm install -g agent-browser, then agent-browser install (add --with-deps on Linux)
5. Git: make sure user.name and user.email are set. If they aren't, ask me for them.

Then clone https://github.com/dynamous-business/nextjs-feature-flag-exercise next to this repo, run
pnpm install in its server/ and client/ folders, and tell me the version of each tool.
```

---

## The day

| Time | Block | What you do |
|---|---|---|
| 09:00-10:30 | **1 · The New SDLC** | The system gap. **Exercise 1:** build a ticket with your current process. Install the AI Layer and prime the codebase |
| 10:45-12:00 | **2 · Setting the Stage** | The PRD, architecture, slicing into tickets, and the R-PIV loop |
| 13:00-14:30 | **3 · R-PIV, hands on** | **Exercise 2:** the *same* ticket, planned, implemented in a fresh session and validated twice. Worktrees while it runs |
| 14:45-17:00 | **4 · Foundations, Evolution, Automation** | Rules, skills and hooks (**Exercise 3**). Evolve the system (**Exercise 4**). Debugging as a workflow. Five ways to say "go". AI-native architecture |

Coffee 10:30-10:45 and 14:30-14:45 · Lunch 12:00-13:00

---

## Before you arrive

Run the setup prompt above, so the room's wifi doesn't have to. That's everything.

---

## The exercises

All three use **[nextjs-feature-flag-exercise](https://github.com/dynamous-business/nextjs-feature-flag-exercise)**,
a small React + Express feature flag dashboard. The application code is identical on every branch:

| Branch | What's there | Exercise |
|---|---|---|
| `exercise-1` | The app and its project docs. **No AI Layer** | **1 · Baseline:** add feature flag filtering (11 acceptance criteria in `TASK.md`) with your current process |
| `exercise-2` | The same app **with this repo's AI Layer** in `.claude/` | **2 · R-PIV:** the *same* ticket, through the loop |
| `exercise-3` | The same as `exercise-2`, with a new `TASK.md` | **3 · Build a skill, then a hook** |

Keep each attempt on its own branch (`git switch -c my-baseline`, commit, then `git switch exercise-2`) so you can
compare them at the end.

### Exercise 1 · Baseline (20 min)

`git switch -c my-baseline` from `exercise-1`, then build the ticket in `TASK.md` the way you'd build it today.
Write down two answers: **how much did you delegate**, and **were you driving, or along for the ride?**

### Exercise 2 · The same ticket, through R-PIV (75 min)

On `exercise-2` (`git switch exercise-2 && git switch -c my-rpiv`):

1. **Prime.** New session. `/prime-codebase`, then paste the ticket from `TASK.md`.
2. **Plan.** `/piv-plan-implementation` with the ticket. Answer its clarifying questions. **Then tighten the
   validation strategy yourself**: it's the highest-leverage edit you'll make all day. Ask for an end-to-end
   check of the UI with `agent-browser`, not just unit tests.
3. **Commit the plan** (`git add .claude/plans && git commit -m "plan: flag filtering"`). It's your rollback point.
4. **Implement in a FRESH session** that gets only the plan: `/piv-implement .claude/plans/<your-plan>.md`
5. **Validate twice.** The agent validates its own work as it goes. Then, in *another* fresh session,
   `/piv-review-changes`. The agent doesn't grade its own homework.
6. While step 4 runs: `/worktree-create` a second ticket and start its plan in parallel.

Then go back to your two answers from Exercise 1.

### Exercise 3 · Build a skill, then a guarantee (35 min)

On `exercise-3`, follow its `TASK.md`: build (or adapt) a skill with `/skills-create`, then a hook with
`/hooks-create`, and prove each one works in both directions.

### Exercise 4 · Evolve the system (15 min)

Back on your Exercise 2 branch, in a fresh session, run `/opportunity-scan` on that run: point it at the plan,
the report, the review and the diff, and tell it what you had to correct. Apply the one change it proposes (a
rule, a skill step, or a hook). Don't fix the code. Fix the system that allowed it.

---

## Install the AI Layer into your own project

Open **your project** in your coding agent and paste this:

```
Copy the Agentic Engineering "AI Layer" into THIS project (my own codebase):

1. Clone https://github.com/dynamous-business/goto-copenhagen-masterclass-resources next to my project
   (I'll want it around for its diagrams and templates).

2. From that clone, copy these into my project root, keeping their exact structure. Copy the folders in full:
   - `.claude/`   (skills, subagents, references, hook templates, CLAUDE.md.template, settings.json.example)
   - `.archon/`   (Archon workflow definitions), only if I use Archon

3. If I don't have a CLAUDE.md yet, don't write one from the template by hand: run the rules-create-global
   skill so the rules come from my codebase. If I do have one, leave it alone.

4. Don't copy anything else or change my existing code, and tell me what you copied.
```

Restart the session (or run `/skills`) and the skills show up. Then make it yours: **the AI Layer is a starting
point, not something to run as-is.** Adapt a skill the moment it does something your way wouldn't
(`/skills-create` has an Adapt mode for exactly that).

> **Hooks ship switched off.** They're real code that runs automatically with your credentials, so nothing fires
> until you create `.claude/settings.json` (start from `.claude/settings.json.example`). Read
> [`.claude/hooks/README.md`](.claude/hooks/README.md) first.

---

## What's in the AI Layer

### The loop

**prime → plan → implement → validate → review → commit → PR**, and, when something goes wrong, **fix the system
that allowed the bug, not just the bug.**

![The two loops](diagrams/Excal-20-The-Two-Loops.png)

### Skills (`.claude/skills/`)

**Prime: load the right context, and only that**

| Skill | What it does |
|---|---|
| `prime-codebase` | Orients the agent in a codebase before planning or implementing |
| `prime-backend` | The same, scoped to API routes, services and the data layer |
| `prime-frontend` | The same, scoped to components, routing, state and styling |

**Plan: intent before implementation**

| Skill | What it does |
|---|---|
| `plan-create-prd` | Interviews you into a problem-first PRD with a falsifiable hypothesis. Intent, never engineering decisions |
| `plan-architecture` | A working session on *how* to build it: approach, stack, data shape, one-way vs two-way doors |
| `piv-slice-epic` | Slices an epic plus its architecture into PIV-sized tickets with a dependency graph |

**The R-PIV loop**

| Skill | What it does |
|---|---|
| `piv-plan-implementation` | Codebase analysis + a short clarifying interview + research, into a one-pass-ready plan |
| `piv-implement` | Executes that plan task by task, validating at every step |
| `piv-validate` | Runs the project's full suite and returns one PASS/FAIL verdict |
| `piv-review-changes` | Pre-commit technical review of what changed, in a fresh context |
| `piv-fix-review-findings` | Triages review findings. You decide what gets fixed now and what's deferred |
| `piv-commit` | One atomic, conventionally-tagged commit |
| `piv-create-pr` | Pushes the branch and opens the PR with a real body |
| `piv-review-pr` | The agentic gate on an open PR: fresh eyes, severity-ranked, posted to GitHub |
| `piv-run-full-loop` | Chains the core loop end to end from a single feature description |

**Issues: diagnose before you fix**

| Skill | What it does |
|---|---|
| `piv-investigate-issue` | Parallel investigation of a GitHub issue into an evidence-backed root-cause analysis |
| `piv-implement-issue` | Implements the fix from that analysis, with a regression test |

**Parallel work**

| Skill | What it does |
|---|---|
| `worktree-create` | One or more git worktrees, each on its own branch, config copied in, dependencies installed |
| `worktree-merge` | Integrates parallel branches through one integration branch, validating after each merge |

**Build and evolve your own AI Layer**

| Skill | What it does |
|---|---|
| `rules-create-global` | Derives a lean global rules file (CLAUDE.md / AGENTS.md) from your codebase in five steps |
| `rules-check-drift` | Checks your rules file still matches the code. Run it before a merge |
| `ai-layer-review` | Reviews a change to the AI Layer itself (rules, skills, hooks, steering docs) the way code gets reviewed |
| `skills-create` | Builds a new skill, or adapts an existing one to work your way |
| `hooks-create` | Turns a plain-English guarantee into a working, tested hook |
| `opportunity-scan` | Scans one run (reactive) or your session logs (proactive) for what to encode next |
| `system-execution-report` | Reflects on a just-finished feature: what was done, divergences, challenges |
| `system-evolution-review` | Classifies how the implementation diverged from its plan and recommends AI Layer fixes |

**Five ways to say "go": automation**

| Skill | What it does |
|---|---|
| `compose-headless-workflow` | Builds a headless `claude -p` script for one of your processes |
| `compose-sdk-workflow` | Builds the same as an Agent SDK program, when a script outgrows the shell |
| `compose-hook-workflow` | Composes a workflow out of lifecycle hooks (react, gate, hand the baton) |
| `compose-ci-workflow` | Builds an agentic GitHub Actions workflow with an explicit trust boundary |
| `compose-orchestrator` | Designs an orchestrator skill: the conversational front door to your whole layer |
| `orchestrate-issues` | A worked orchestrator: investigate → implement → PR → review, through background agents, with gates and a cap |
| `archon-cli` | Drives [Archon](https://github.com/coleam00/Archon) workflows: run, inspect, approve, author |

**Tools the loop reaches for**

| Skill | What it does |
|---|---|
| `agent-browser` | Browser automation, so the agent can test the UI like a user |
| `ast-grep` | Structural code search with AST rules |

Invoke any skill with `/<name>`, or just describe the work and let its description trigger it.

### Subagents (`.claude/agents/`)

| Agent | Use it for |
|---|---|
| `codebase-analyst` | A deep structural read of a codebase or subsystem, with `file:line` references, in its own context |
| `research-agent` | External research (docs, libraries, risks) that comes back as a tight summary |
| `code-reviewer` | A fresh-eyes review of new code before it's committed |
| `system-reviewer` | Reviewing a run against its plan for AI Layer improvements |
| `meta-agent` | Authoring a new subagent, or retuning one, for your project |

### References (`.claude/references/`)

On-demand guides the rules file points to instead of inlining: `conventions.md`, `architecture-patterns.md`,
`vertical-slice-architecture.md`, `backend-api-best-practices.md`, `frontend-component-best-practices.md`, and
`codebase-search-and-lsp.md`. Plus `.claude/CLAUDE.md.template`, the structure `rules-create-global` follows.

### Hooks (`.claude/hooks/`)

| Hook | Event | Shape |
|---|---|---|
| `pre_tool_use.py` | PreToolUse | **Gate:** blocks reading secrets (env files, keys, the process environment) and `rm -rf` |
| `post_tool_use.py` | PostToolUse | **Log:** an audit trail of every tool call |
| `stop-gate.sh` | Stop | **Gate:** the agent can't finish while the checks are red (bounded, so it can't loop) |
| `format-touched.sh` | PostToolUse | **React:** formats each file the moment it's edited |
| `baton.sh` | Stop (async) | **Hand the baton:** one skill's artifact starts the next skill in a fresh session |

The first two are wired in `.claude/settings.json.example`; the last three in
`.claude/hooks/automation-hooks.settings.json`. `stop-gate.sh` and `format-touched.sh` ship configured for the
exercise app (pnpm); change their commands for your project.

### Automation templates

| Where | What |
|---|---|
| [`automations/`](automations/) | `fix-issue.sh` (headless) and `fix_issue.py` (Agent SDK): the same fix loop written both ways, as templates |
| [`automations/github-workflows/`](automations/github-workflows/) | Agents in CI: read-only review, hybrid create, Codex deterministic, release notes. Copy into your own `.github/workflows/` |
| [`.archon/workflows/`](.archon/workflows/) | Archon workflows: the PIV loop, GitHub issue fix, parallel implementation |
| [`templates/steering/`](templates/steering/) | `engineering.md` and `direction.md`: steering documents the plan, implement and review skills read when present |
| [`tooling/mcp/codebase_search.py`](tooling/mcp/codebase_search.py) + [`.mcp.json`](.mcp.json) | A codebase-search MCP server (AST-based `where_is`, `find_references`, `outline`). Needs only `uv` |

### Diagrams (`diagrams/`)

Every diagram from the day, as PNG: the system gap, the AI Layer, the timescales of planning, where rules come
from, epic grounding and slicing, the harness, each primitive, check-trust-automate, the two loops, the ways to
automate, and Archon.

---

## Take it home: three things for Monday

1. **Derive your rules** on your real codebase with `rules-create-global`, then prune them.
2. **Run one real ticket through R-PIV**: plan, fresh-session implement, fresh-session review.
3. **Run one opportunity scan** on that run and encode the one change it finds.

The goal is to use AI coding agents reliably across the entire software development lifecycle.

---

*Cole Medin · [Dynamous](https://dynamous.ai) · cole@dynamous.ai*
