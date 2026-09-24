---
name: compose-headless-workflow
description: Use only when the user explicitly asks to build a headless coding-agent script driven by a non-interactive CLI call, such as "build a headless Claude Code script for X", "automate this with claude -p", or the same request aimed at Codex, Gemini CLI, PI or another agent.
---

# Compose a Headless Workflow

Turn a real manual process into a runnable, bounded headless workflow. Resolve the purpose first, propose an ASCII concept for approval, then design each stage and handoff with the user before writing and testing the script.

## What this composition method is

A headless workflow uses non-interactive coding-agent calls inside an ordinary script. The script starts stages, carries values or artifacts between them, runs objective checks, enforces bounds, and exposes useful runtime state. Agent stages perform work that needs interpretation or judgment.

The only agent-specific prerequisite is an installed and authenticated CLI for whichever agent was chosen above. Do not require an SDK, an API client, or a separate application framework. Default to a readable Bash script unless the user requests another host language.

## Choose agents for meaning, code for mechanics

Counter the common bias toward encoding too much of the workflow as deterministic logic.

- Recommend an **agent** for investigation, interpretation, synthesis, planning, review, adaptation, or any step whose quality must be described rather than computed.
- Recommend **deterministic code** for invoking commands, validating syntax or schemas, checking exit status, moving data, recording artifacts, enforcing retry/time limits, and routing fully known states.
- Recommend a **hybrid** when an agent should do semantic work and an objective command can verify a property afterward.

Keep the script thin. Do not turn semantic judgment into a growing state machine of guesses and special cases. If a step can only be specified by explaining what “good” means, prefer an agent. If success can be completely decided by a command, predicate, or schema, prefer deterministic code.

Examples:

| Work | Recommend | Why |
|---|---|---|
| Investigate a bug | Agent | Requires exploration and interpretation |
| Run tests and determine whether they passed | Agent + deterministic | Let the agent run focused checks while it works; run the full authoritative check deterministically afterward |
| Decide whether a failure is a product bug | Agent | Requires context and judgment |
| Validate JSON against a schema | Deterministic | The contract is fully specified |
| Review a change for subtle logic errors | Agent | Open-ended semantic analysis |
| Ensure a review artifact exists | Deterministic | A simple state check is sufficient |

## Resolve which agent first

Everything below is agent-shaped: the invocation form, session continuation, structured output, model selection and tool scoping all differ per agent. Settle this before looking anything up.

**Work it out rather than asking first.** You are running inside a coding agent, and that is the default. Claude Code's is `claude -p`; Codex, Gemini CLI, PI, opencode and others each have their own non-interactive form. Ask only when the answer is genuinely open, and ask once. **This is the first thing the user sees from this skill, so ask it with `AskUserQuestion`, not as a prose paragraph.** First option: the agent you are running in, recommended, because it is installed and authenticated here. Second option: the named alternative, preferable when the workflow has to run where that one already lives.

The chosen agent's non-interactive CLI is the **only** agent-specific prerequisite. Do not require an SDK, an API client, or a separate application framework. Record the choice in the decision record: every flag, session mechanism and output format below follows from it.

If the user wants the workflow to be portable across agents, keep each invocation behind one small function (the `ask()` shape) so swapping agents is a one-function change rather than a rewrite.

## Get current before designing configuration

Look up the current official documentation for **the chosen agent's** headless/non-interactive operation before asking configuration-specific questions or writing the script.

1. Search the web for that agent's current official documentation covering headless or programmatic use. Restrict configuration claims to that vendor's official documentation and official repositories.
2. Confirm relevant behavior against the installed CLI's help when implementation begins. Do not inventory the user's wider setup.
3. Verify the current forms of non-interactive invocation, session continuation, structured output, model selection, tool/permission scoping, authentication, limits, and exit behavior needed by this workflow.
4. Treat live official docs and installed CLI help as authoritative. Do not rely on remembered flags, model aliases, JSON fields, defaults, or pricing behavior.
5. Briefly name the official sources used and flag anything that could not be verified.

Do not scan the user's repository, skills, agents, hooks, or configuration during this step. If the user wants to reuse existing skills, ask them to name the skills or provide their paths. Offer to inspect or list candidates only when asked.

## Interaction contract

- Ask only enough questions to make the next decision.
- Preserve answers already supplied; never re-ask them.
- Lead every material decision with a recommendation and a reason. Then name the meaningful alternative and let the user approve or adjust it.
- **Use your agent's structured question tool for every decision that forks the design.** In Claude Code that is
  `AskUserQuestion`. Put your recommendation first, the meaningful alternative second, and a one-line consequence
  on each option; let the tool supply "other". If your agent has no such tool, ask the same thing in prose.
- Never present an **undecorated** menu of configuration choices. Options are good; bare labels are not. A choice is decidable
  only when each option carries what it costs you.
- Stay in prose for open questions ("what are you trying to automate?") — those have no option set, and a tool
  with invented options would narrow the answer.
- Separate the **concept** from the **implementation details**.
- Do not write files until the concept and detailed stage design are approved.
- After concept approval, work through one stage and its outgoing handoff at a time. Do not make the user configure every stage in one large questionnaire.
- Keep a visible decision record and update the ASCII flow as decisions land.

**Render every such decision as an `AskUserQuestion` call. Do not write it as prose.** The tool is the default shape for a decision in this skill; prose is the fallback.

- **First option** = your recommendation. Label it with the choice; its description is `[reason specific to this workflow]`.
- **Second option** = the meaningful alternative. Its description is `preferable when [condition]`.
- Add further options only if they are genuinely live. Let the tool supply "other" — never write your own.
- Keep `header` to a couple of words, and give every option a one-line consequence so the user chooses between outcomes, not labels.

Only if your agent has no question tool, fall back to prose:

> **Recommendation:** [choice], because [reason specific to this workflow]. [Alternative] is preferable when [condition]. Does that fit, or should we adjust it?

## Phase 1 — Resolve the why

Ask a small initial set of plain-language questions. Avoid flags, models, tool lists, file paths, and session mechanics at this point.

1. What are you trying to automate?
2. What happens manually today?
3. What should start the workflow, and what should exist when it finishes?
4. Where does judgment currently happen, and which failures must the workflow catch?
5. Where, if anywhere, must a human decide?
6. **What would you like to be observable during the run, and what should remain available afterward?**

Clarify only gaps that materially change the concept. For observability, help distinguish:

- live stage status;
- decisions summarized at a useful level;
- verification commands and verdicts;
- retry counts, elapsed time, and cost when available;
- handoffs and artifact locations;
- human gates and requested decisions;
- actionable failures and resumable state;
- a durable final digest.

Recommend this baseline unless the workflow calls for something different: show stage start/completion, deterministic verdicts, retry counts, artifact paths, gates, and failures during the run; retain durable outputs plus a concise final digest afterward. Avoid full transcripts or hidden reasoning as routine observability.

## Phase 2 — Propose the concept

Translate the answers into a recommended conceptual decomposition. Label every node as `AGENT`, `CODE`, `HYBRID`, or `HUMAN GATE`. Show meaningful handoffs and the requested observability, but omit exact flags and low-level configuration.

Use a compact shape such as:

```text
INPUT: GitHub issue
    │
    ▼
[AGENT] Investigate
    observable: stage status + investigation path
    │ investigation.md
    ▼
[AGENT] Implement
    observable: stage status + changed-files summary
    │ changed worktree
    ▼
[CODE] Run project checks
    observable: command verdicts + attempt 1/3
    │
    ├── red ──► return evidence to implementer
    │
    └── green
          ▼
[AGENT — FRESH] Review
    observable: review status + report path
          │ review.md
          ▼
[HUMAN GATE] Approve merge
```

Explain why each node is agentic, deterministic, hybrid, or human-held. Explicitly call out any place where deterministic logic would be brittle and an agent is the better fit.

Ask the user to approve or iterate on the concept. Accept additions, removals, reordered stages, different gates, and different observability. Do not proceed until the conceptual flow is settled.

> **Ask this with `AskUserQuestion`.** This is a fork in the design, not an open question, so it belongs in the tool rather than in prose. Put your recommendation first, the meaningful alternative second, and a one-line consequence on each option; let the tool supply "other". Only fall back to prose if your agent has no such tool.

## Phase 3 — Design the input contract

Start the detailed pass with the workflow boundary:

- What invokes the script?
- What exact inputs does it receive?
- Which inputs are required or optional?
- How are inputs supplied?
- What minimal validation belongs at the boundary?
- What happens when input is missing or invalid?

Recommend the smallest stable input contract. Prefer identifiers or paths over duplicating large source content when the first stage can retrieve or read the authoritative source.

Record the approved contract and update the flow.

## Phase 4 — Design one stage and handoff at a time

> **Ask this with `AskUserQuestion`.** This is a fork in the design, not an open question, so it belongs in the tool rather than in prose. Put your recommendation first, the meaningful alternative second, and a one-line consequence on each option; let the tool supply "other". Only fall back to prose if your agent has no such tool.

For each stage in order, resolve its stage contract before moving to the next.

### Stage contract

1. **Goal** — What problem does this stage solve?
2. **Input** — What exact value, artifact, or repository state does it receive?
3. **Executor** — Existing skill, direct prompt, deterministic command, or hybrid?
4. **Context** — New session or continued session, and why?
5. **Model** — Which currently supported model fits the judgment required?
6. **Tools** — What is the least privilege needed for the work?
7. **Output** — What does the stage hand to the next stage?
8. **Completion evidence** — How can the workflow verify the stage completed?
9. **Live observability** — What should be visible while it runs, and where?
10. **Durable record** — What should remain afterward, if anything?
11. **Failure behavior** — What evidence is returned, where does control go, and may the stage retry?
12. **Bounds** — Attempts, turns, time, parallelism, or cost limits that apply.

For every executor choice, recommend agent, deterministic, or hybrid and explain the classification. When the user wants an existing skill, ask for its name. Inspect its file only if the user supplies a path or asks for help locating it. When no suitable skill exists, recommend either a direct prompt or a separately authored skill based on reuse: use a direct prompt for a narrow one-off stage; recommend a skill for a process the user expects to reuse or improve independently.

### Handoff contract

After approving the stage, resolve the outgoing handoff:

- What crosses the boundary?
- Is it an ephemeral value or durable file/artifact?
- Does the recipient need the full artifact or a focused summary?
- Does the next stage need memory or independence?
- Is the next call a continuation of the same session or a fresh session?
- What objective condition, if any, gates the handoff?
- What part of the handoff should be observable?

Recommend a **continued context** for correction loops or sequential work that benefits from remembered intent. Recommend a **fresh context** for independent review, adversarial checking, or a genuinely separate responsibility. Do not treat fresh context as universally better.

Recommend a **value** for cheap, same-run handoffs that do not need inspection or recovery. Recommend a **file/artifact** when the handoff must cross processes, support parallel work, remain reviewable, provide resumable state, or serve as completion evidence.

After each approval, show progress:

```text
✓ Input: issue number
✓ Stage 1: investigate [agent, fresh]
  Output: investigation.md
  Observable: start/end + artifact path

→ Stage 2: implement [designing now]
○ Stage 3: validate
○ Stage 4: review
○ Gate: merge approval
```

## Phase 5 — Review the complete design

Present the final ASCII flow plus a compact table of stage contracts. Check the composition before writing:

- Every stage has one clear goal.
- Semantic work has not been forced into brittle deterministic logic.
- Deterministic checks sit outside agent claims where objective evidence exists.
- Every handoff has an explicit value or artifact.
- Every context continuation or reset has a reason.
- Every stage has useful live observability and actionable failure output.
- Every loop and unattended call is bounded.
- Human gates sit at deliberate seams.
- Secrets never enter prompts, script literals, logs, or artifacts.

Ask for final design approval. If the user changes the design, update the flow and affected stage contracts before building.

> **Ask this with `AskUserQuestion`.** This is a fork in the design, not an open question, so it belongs in the tool rather than in prose. Put your recommendation first, the meaningful alternative second, and a one-line consequence on each option; let the tool supply "other". Only fall back to prose if your agent has no such tool.

## Phase 6 — Build the script

Confirm the output path, then create a readable Bash script by default. Use another host language only when requested. Preserve nearby user files and configuration.

A complete worked example lives in `references/fix-issue.sh` — read it before writing the script.

Implement using the syntax verified from current official docs and installed CLI help. Keep the script focused on:

- validating inputs;
- invoking the approved agent stages;
- capturing only the structured fields the workflow needs;
- continuing or starting sessions according to the approved context design;
- running deterministic commands itself;
- carrying values and artifacts between stages;
- emitting the approved observability signals;
- enforcing bounds and returning useful exit codes;
- stopping at human gates rather than inventing approval.

Do not silently add stages, retries, fallbacks, repository scans, or permissions that were not approved. Do not ask an agent stage to claim an objective check passed when the script can run that check directly.

## Phase 7 — Prove the workflow

Validate safely before reporting completion:

1. Confirm the chosen agent's CLI is installed and inspect its current help for every used flag.
2. Run a shell syntax check.
3. Exercise input validation without invoking a paid agent call when possible.
4. Run the smallest safe representative workflow with the user's approval if it can incur material cost or mutate meaningful state.
5. Verify the success path, one deliberate failure path, retry bounds, context behavior, output artifacts, and requested observability.
6. Check that logs and artifacts contain no credentials or unnecessary transcript content.

If a live run is unsafe, costly, or unavailable, validate everything possible locally and state precisely what remains unverified. Never report a workflow as proven from inspection alone.

## Final report

Return:

- the script path;
- the final ASCII composition;
- the stage/context/handoff decisions in concise form;
- what is observable live and what remains durable;
- the official documentation and installed CLI version used;
- tests performed and their results;
- anything unverified;
- the few settings or lines the user is most likely to customize.
