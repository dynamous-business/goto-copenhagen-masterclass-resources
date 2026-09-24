---
name: compose-sdk-workflow
description: Use only when the user explicitly asks to build an automation or agent with a coding agent's SDK, such as "build this with the Claude Agent SDK", "let's automate this using the Agent SDK", or the same request aimed at another agent's SDK.
---

# Compose an Agent SDK Workflow

Turn a real manual process into a runnable, bounded program built on a coding agent's SDK. Resolve the purpose first, propose an ASCII concept for approval, then design each stage and handoff with the user before writing and testing the program.

## What this composition method is

An Agent SDK workflow runs the agent loop inside the user's own process — Python or TypeScript for Claude's `claude-agent-sdk`, whichever languages the chosen agent's SDK supports otherwise. The program can hold sessions, stream events, intercept tool calls as they happen, run deterministic code between agent turns, and expose application-specific state. Agent stages perform work that needs interpretation or judgment; ordinary code owns mechanics, evidence, and bounds.

The user has already selected the SDK method by invoking this skill. Do not compare it against a headless CLI script (`claude -p` or another agent's equivalent), hooks, CI, or an orchestrator unless the user asks. Do not turn the opening into a method-selection exercise.

## Choose agents for meaning, code for mechanics

Counter the common bias toward encoding too much of the workflow as deterministic logic.

- Recommend an **agent** for investigation, interpretation, synthesis, planning, review, adaptation, or any step whose quality must be described rather than computed.
- Recommend **deterministic code** for invoking commands, validating syntax or schemas, checking exit status, moving data, recording artifacts, enforcing retry/time limits, and routing fully known states.
- Recommend a **hybrid** when an agent should do semantic work and an objective command can verify a property afterward.

Keep deterministic control thin. Do not turn semantic judgment into a growing state machine of guesses and special cases. If a step can only be specified by explaining what “good” means, prefer an agent. If success can be completely decided by a command, predicate, or schema, prefer deterministic code.

Examples:

| Work | Recommend | Why |
|---|---|---|
| Investigate a bug | Agent | Requires exploration and interpretation |
| Run tests and determine whether they passed | Agent + deterministic | Let the agent run focused checks while it works; run the full authoritative check deterministically afterward |
| Decide whether a failure is a product bug | Agent | Requires context and judgment |
| Validate structured data against a schema | Deterministic | The contract is fully specified |
| Review a change for subtle logic errors | Agent | Open-ended semantic analysis |
| Deny writes to a protected path | Deterministic SDK control | The policy is precise and must apply at tool-call time |

## Resolve which agent first

This is the one composition method with a hard prerequisite: the agent must ship a real **SDK** — a library that runs the agent loop inside your own process, loads the project's own agent layer, and exposes sessions, events, and tool control. Claude's is `claude-agent-sdk` (Python and TypeScript). That is a narrower field than the CLI-based methods, and some agents have no SDK at all. Settle this before looking anything up: every class name, session object, event field, and permission control below is that SDK's vocabulary.

**Work it out rather than asking first.** You are running inside a coding agent, and that is the default when it ships an SDK. Ask only when the answer is genuinely open, and ask once: ask it with `AskUserQuestion` (options: the agent you are running in, recommended, versus the named alternative), not as a prose paragraph:

**Ask this with `AskUserQuestion`, not as a prose paragraph** — it is the first thing the user sees from this skill. First option: the agent you are running in, recommended. Second option: the named alternative, with the condition that would make it the better choice.

If the agent the user names has **no SDK**, say so plainly instead of improvising one. Shelling out to its CLI from `subprocess` is a headless workflow wearing a library's clothes: recommend `compose-headless-workflow`, or an agent that does ship an SDK. A plain HTTP model API is not an SDK either — no agent loop, no tools, no project-configuration layer, so none of the design below applies to it.

Record the choice in the decision record: the language options, session API, streamed events, tool interception, and dependency vessel all follow from it.

## Get current before designing configuration

Look up the current official documentation for **the chosen agent's SDK** before asking configuration-specific questions or writing the program.

1. Search the web for that SDK's current official overview and the official documentation for each language it supports (for Claude, `claude-agent-sdk` in Python and TypeScript). Restrict configuration claims to that vendor's official documentation and official repositories.
2. Once the user chooses a language, read only that language's current SDK documentation, package metadata, examples, and public types needed for the design.
3. Verify the current package name and version requirements, installation or single-file execution pattern, authentication, project-configuration loading, session/client APIs, one-shot queries, streaming events, model selection, tool and permission controls, callbacks or hooks, structured output, subagents, context/compaction behavior, errors, and limits relevant to this workflow.
4. Treat live official docs and installed package types as authoritative. Do not rely on remembered class names, method signatures, event fields, defaults, model aliases, or billing behavior, and never carry one agent's SDK shape across to another.
5. Briefly name the official sources used and flag anything that could not be verified.

Do not scan the user's repository, dependencies, skills, agents, hooks, or configuration during this step. If the user wants to reuse existing skills, ask them to name the skills or provide their paths. Offer to inspect or list candidates only when asked.

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

Ask a small initial set of plain-language questions. Avoid SDK APIs, models, tool lists, file paths, and dependency configuration at this point.

1. What are you trying to automate or build?
2. What happens manually today?
3. What should start the program, and what should exist when it finishes?
4. Where does judgment currently happen, and which failures must the workflow catch?
5. Where, if anywhere, must a human decide?
6. **What would you like to be observable during the run, and what should remain available afterward?**

Clarify only gaps that materially change the concept. For observability, help distinguish:

- live stage and session status;
- streamed text, tool calls, and selected SDK events;
- decisions summarized at a useful level;
- verification commands and verdicts;
- retry counts, elapsed time, usage, and cost when currently exposed;
- handoffs and artifact locations;
- human gates and requested decisions;
- actionable failures and resumable state;
- a durable final digest.

Recommend this baseline unless the workflow calls for something different: show stage start/completion, tool activity at a useful summary level, deterministic verdicts, retry counts, artifact paths, gates, and failures during the run; retain durable outputs plus a concise final digest afterward. Avoid full transcripts, raw event dumps, or hidden reasoning as routine observability.

## Phase 2 — Propose the concept

Translate the answers into a recommended conceptual decomposition. Label every node as `AGENT`, `CODE`, `HYBRID`, or `HUMAN GATE`. Show meaningful handoffs, session boundaries, and requested observability, but omit exact SDK APIs and low-level configuration.

Use a compact shape such as:

```text
INPUT: GitHub issue
    │
    ▼
[AGENT SESSION] Investigate + implement
    observable: stage status + summarized tool activity
    │ changed worktree
    ▼
[CODE] Run project checks
    observable: command verdicts + attempt 1/3
    │
    ├── red ──► query SAME SESSION with failure evidence
    │
    └── green
          ▼
[AGENT — FRESH QUERY] Review
    observable: review status + report path
          │ review.md
          ▼
[HUMAN GATE] Approve merge
```

Explain why each node is agentic, deterministic, hybrid, or human-held. Explicitly call out any place where deterministic logic would be brittle and an agent is the better fit. Explain each session continuation or reset in terms of memory versus independence.

Ask the user to approve or iterate on the concept. Accept additions, removals, reordered stages, different gates, different session boundaries, and different observability. Do not proceed until the conceptual flow is settled.

> **Ask this with `AskUserQuestion`.** This is a fork in the design, not an open question, so it belongs in the tool rather than in prose. Put your recommendation first, the meaningful alternative second, and a one-line consequence on each option; let the tool supply "other". Only fall back to prose if your agent has no such tool.

## Phase 3 — Choose the language and dependency vessel

After concept approval, ask which of the chosen SDK's supported languages to build in — for Claude's SDK, **Python** or **TypeScript**. Always recommend one from information the user has supplied; do not scan the project to decide. If the SDK supports only one language, say so and skip the question rather than offering a choice that does not exist.

- Recommend the language already used by the surrounding product when the SDK program belongs inside it.
- For a standalone automation with no surrounding-language constraint, recommend the language the user is most comfortable maintaining.

Then ask how dependencies should be carried:

- **Python default:** recommend a portable `uv` single-file script with inline dependencies. Ask whether the user instead wants a normal project virtual environment with dependencies installed into it.
- **TypeScript default:** recommend the current official Bun/Bunx single-file pattern with inline or automatically resolved dependencies. Ask whether the user instead wants dependencies installed as project `node_modules`.

Verify the exact supported command and metadata syntax from the current SDK and runtime documentation before writing. Do not assume remembered `uv`, `bun`, or `bunx` behavior. Record the approved language, runtime, dependency vessel, target path, and supported runtime version.

## Phase 4 — Design the input contract

Resolve the program boundary:

- What invokes the program?
- What exact inputs does it receive?
- Which inputs are required or optional?
- How are inputs supplied?
- What minimal validation belongs at the boundary?
- What happens when input is missing or invalid?

Recommend the smallest stable input contract. Prefer identifiers or paths over duplicating large source content when the first stage can retrieve or read the authoritative source.

Record the approved contract and update the flow.

## Phase 5 — Design one stage and handoff at a time

> **Ask this with `AskUserQuestion`.** This is a fork in the design, not an open question, so it belongs in the tool rather than in prose. Put your recommendation first, the meaningful alternative second, and a one-line consequence on each option; let the tool supply "other". Only fall back to prose if your agent has no such tool.

For each stage in order, resolve its stage contract before moving to the next.

### Stage contract

1. **Goal** — What problem does this stage solve?
2. **Input** — What exact value, artifact, event, or application state does it receive?
3. **Executor** — Existing skill, direct agent query, deterministic function/command, or hybrid?
4. **Session** — Persistent SDK client/session or fresh one-shot query, and why?
5. **Model** — Which currently supported model fits the judgment required?
6. **Tools and permissions** — What is the least privilege needed for the work?
7. **In-process control** — Must the program inspect, modify, approve, or deny any tool call as it happens?
8. **Output** — What value, event, or artifact does the stage hand to the next stage?
9. **Completion evidence** — How can the program verify the stage completed?
10. **Live observability** — Which SDK events should be translated into useful operator output?
11. **Durable record** — What should remain afterward, if anything?
12. **Failure behavior** — What evidence is returned, where does control go, and may the stage retry?
13. **Bounds** — Attempts, turns, time, parallelism, context growth, usage, or cost limits that apply.

For every executor choice, recommend agent, deterministic, or hybrid and explain the classification. When the user wants an existing skill, ask for its name. Inspect its file only if the user supplies a path or asks for help locating it. When no suitable skill exists, recommend either a direct query or a separately authored skill based on reuse: use a direct query for a narrow one-off stage; recommend a skill for a process the user expects to reuse or improve independently.

Recommend in-process tool interception only for a real runtime need: enforcing a precise policy, requesting application approval, modifying tool input, injecting context, or observing a call before it executes. Do not add callbacks merely because the SDK supports them.

### Handoff contract

After approving the stage, resolve the outgoing handoff:

- What crosses the boundary?
- Is it an in-memory value/event or durable file/artifact?
- Does the recipient need the full artifact or a focused summary?
- Does the next stage need memory or independence?
- Does it reuse a persistent client/session or start a fresh query?
- What objective condition, if any, gates the handoff?
- What part of the handoff should be observable?

Recommend a **persistent session** for correction loops or sequential work that benefits from remembered intent. Recommend a **fresh query/session** for independent review, adversarial checking, or a genuinely separate responsibility. Do not treat fresh context as universally better.

Recommend an **in-memory value/event** for cheap, same-process handoffs that do not need inspection or recovery. Recommend a **file/artifact** when the handoff must cross processes, support parallel work, remain reviewable, provide resumable state, or serve as completion evidence.

After each approval, show progress:

```text
✓ Input: issue number
✓ Stage 1: investigate [agent, persistent client]
  Output: investigation result
  Observable: start/end + summarized tool activity

→ Stage 2: implement [designing now]
○ Stage 3: validate
○ Stage 4: review [fresh query]
○ Gate: merge approval
```

## Phase 6 — Review the complete design

Present the final ASCII flow plus a compact table of stage contracts. Check the composition before writing:

- Every stage has one clear goal.
- Semantic work has not been forced into brittle deterministic logic.
- Deterministic checks sit outside agent claims where objective evidence exists.
- Every handoff has an explicit value, event, or artifact.
- Every persistent or fresh session choice has a reason.
- In-process interception exists only where it adds real control.
- SDK events are converted into intentional observability rather than dumped raw.
- Every loop and unattended call is bounded.
- Human gates sit at deliberate seams.
- Secrets never enter prompts, source literals, logs, or artifacts.

Ask for final design approval. If the user changes the design, update the flow and affected stage contracts before building.

> **Ask this with `AskUserQuestion`.** This is a fork in the design, not an open question, so it belongs in the tool rather than in prose. Put your recommendation first, the meaningful alternative second, and a one-line consequence on each option; let the tool supply "other". Only fall back to prose if your agent has no such tool.

## Phase 7 — Build the program

Create the approved Python or TypeScript artifact using the current official SDK APIs and the approved dependency vessel. Preserve nearby user files and configuration.

A complete worked example lives in `references/fix_issue.py` — read it before writing the program.

Keep the program focused on:

- validating inputs;
- configuring the SDK with the approved model, tools, permissions, and project-layer behavior;
- owning persistent clients and fresh queries according to the approved session design;
- draining or consuming SDK responses correctly;
- translating selected events into the approved observability signals;
- intercepting tool calls only where approved;
- running deterministic commands itself;
- carrying values and artifacts between stages;
- enforcing bounds and surfacing actionable errors;
- stopping at human gates rather than inventing approval.

Do not silently add stages, retries, fallbacks, repository scans, hooks, subagents, or permissions that were not approved. Do not ask an agent stage to claim an objective check passed when the program can run that check directly.

## Phase 8 — Prove the workflow

Validate safely before reporting completion:

1. Verify the selected runtime and dependency mechanism.
2. Install or resolve only the approved SDK dependency, using the approved vessel.
3. Run syntax, formatting, type, or import checks appropriate to the selected language.
4. Exercise input validation and deterministic functions without invoking a paid agent call when possible.
5. Run the smallest safe representative workflow with the user's approval if it can incur material cost or mutate meaningful state.
6. Verify the success path, one deliberate failure path, retry bounds, session behavior, tool interception, output artifacts, and requested observability.
7. Check that logs and artifacts contain no credentials, raw event noise, or unnecessary transcript content.

If a live run is unsafe, costly, or unavailable, validate everything possible locally and state precisely what remains unverified. Never report a workflow as proven from inspection alone.

## Final report

Return:

- the program path and run command;
- the final ASCII composition;
- the language and dependency vessel;
- the stage/session/handoff decisions in concise form;
- what is observable live and what remains durable;
- the official documentation and SDK/runtime versions used;
- tests performed and their results;
- anything unverified;
- the few settings or lines the user is most likely to customize.
