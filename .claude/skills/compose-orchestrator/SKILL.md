---
name: compose-orchestrator
description: Use only when the user explicitly asks to create or evolve an orchestrator skill as a conversational interface for their agentic layer, such as "build an orchestrator for my agentic layer", "create one skill that can run my delivery loop", or "upgrade my orchestrator with this capability". Do not use merely because the user asks to run or coordinate existing work.
---

# Compose an Evolving Orchestrator

Build the smallest useful orchestrator around capabilities the user already trusts. Resolve what the user wants to say to it, map one end-to-end capability for approval, then design each capability contract before writing and proving the orchestrator skill.

## What this composition method is

An orchestrator is one conversational control plane for the user's agentic layer. The user gives it a goal; it invokes named capabilities, assigns work to suitable agents, preserves or resets context deliberately, verifies what comes back, holds gates, and returns a useful digest.

The orchestrator knows how work connects. It does not absorb how every capability works:

```text
ORCHESTRATOR KNOWS
name → input → owner → output → evidence → next owner

WORKER CAPABILITY KNOWS
how to perform the work
```

An orchestrator can eventually control much of an agentic system through one interface. Its first version should expose one coherent, useful route—not every available tool, skill, agent, hook, script, or integration.

## Start small and evolve from evidence

Do not reproduce a production orchestrator for someone creating their first one. Build from capabilities their system has earned.

The first orchestrator should normally coordinate one end-to-end delivery loop for one workstream: accept an issue or equivalent work item, run the user's proven stages, verify the result, stop at one deliberate gate, and return one digest. It should not begin with parallel workstreams, worktree policy, merge queues, standing-decision machinery, persistent run files, detached execution, recovery protocols, or self-improvement loops.

Add a capability only when:

1. the underlying capability works independently;
2. the user can name the limitation its addition solves;
3. its input, output, evidence, authority, and failure path are explicit;
4. the upgraded orchestrator can be tested on a representative run.

Treat “mature orchestrators have it” as insufficient justification.

## Orchestrate, do not implement

Make this the invariant of every generated orchestrator:

- The orchestrator coordinates, launches, steers, verifies, gates, and summarizes.
- Worker agents, named skills, scripts, hooks, CI workflows, or external systems perform domain work.
- The orchestrator composes capabilities by name and contract, not by copying their full instructions into itself.
- The orchestrator does not edit product code, perform the review, investigate the issue, or silently take over another capability's responsibility.
- An agent saying “done” is a claim. A promised artifact, green check, external state, or deterministic command is evidence.

Keep the control plane small. Give it the ability to invoke and observe approved capabilities, not generic access to everything.

## Resolve which agent first

The orchestrator's ideas travel; its mechanism may not. Naming capabilities, contracts, evidence, gates, and a digest are agent-independent. **Whether the orchestrator can launch a worker at all is not.** Claude Code can spawn subagents and observe them; some agents have no sub-agent surface whatsoever, and there an orchestrator has to launch each worker as a separate non-interactive CLI process and treat the artifact it leaves as the only evidence. Settle this before looking anything up.

**Work it out rather than asking first.** You are running inside a coding agent, and that is the default — it is also where the capabilities the user already trusts are installed. Ask only when the answer is genuinely open, and ask once: ask it with `AskUserQuestion` (options: the agent you are running in, recommended, versus the named alternative), not as a prose paragraph:

**Ask this with `AskUserQuestion`, not as a prose paragraph** — it is the first thing the user sees from this skill. First option: the agent you are running in, recommended. Second option: the named alternative, with the condition that would make it the better choice.

Then establish, from that agent's live documentation rather than from memory, what it can actually do:

- Can it launch a worker at all — an in-process subagent, a background task, or only a separate CLI process?
- Can it observe or be notified of completion, or must the orchestrator poll for an artifact?
- Can it continue or steer a worker that is already running, or is respawning the only correction available?
- Can workers invoke named skills, and does the project's context layer reach them?

A capability the chosen agent does not have is not a design to work around — it is a route to leave out of version one. If the agent cannot steer a running worker, do not design steering; make each stage a bounded launch that leaves an artifact behind. Record the choice and these answers in the decision record: the route, the continuity decisions, and the evidence contracts below all follow from them.

## Get current before designing mechanics

Look up current official documentation for **the chosen agent** before asking tool-, agent-, context-, model-, isolation-, or permission-specific questions or writing the orchestrator.

1. Read that agent's current official documentation for skills, built-in tools, subagents, background execution, messaging or resumption, task state, permissions, and worktree isolation relevant to the approved concept.
2. Distinguish current subagent behavior from agent teams or other coordination surfaces. Do not assume tools, nesting, context inheritance, lifecycle, availability, or experimental status — and never assume one agent's coordination surface exists in another.
3. Verify the current mechanism for invoking named skills from workers, launching work, continuing or steering the same worker, checking status, stopping work, isolating changes, and observing completion.
4. Treat live official documentation and the installed agent version as authoritative. Do not rely on remembered tool names, parameters, defaults, model aliases, limits, or permission behavior.
5. Briefly name the official sources used and flag anything that could not be verified.

Do not inventory the user's agentic layer during this step. Ask the user to name the capabilities they want to expose or provide their paths. Offer to inspect or list candidates only when asked. Inspect only named capabilities until the concept is approved.

## Interaction contract

- Ask only enough questions to make the next decision.
- Preserve supplied answers; never re-ask them.
- Lead every material decision with a recommendation and a reason, then name the meaningful alternative.
- **Use your agent's structured question tool for every decision that forks the design.** In Claude Code that is
  `AskUserQuestion`. Put your recommendation first, the meaningful alternative second, and a one-line consequence
  on each option; let the tool supply "other". If your agent has no such tool, ask the same thing in prose.
- Never present an **undecorated** menu of tools, agents, models, or advanced orchestration patterns. Options are good; bare labels are not. A choice is decidable
  only when each option carries what it costs you.
- Stay in prose for open questions ("what are you trying to automate?") — those have no option set, and a tool
  with invented options would narrow the answer.
- Separate the **capability concept** from implementation mechanics.
- Do not write files until the concept and detailed capability contracts are approved.
- After concept approval, work through one capability and its outgoing handoff at a time.
- Keep a visible capability ledger, non-capability list, and evolving ASCII map.
- Never use a mature example as a template to copy wholesale. Extract principles and fit them to the user's current system.

**Render every such decision as an `AskUserQuestion` call. Do not write it as prose.** The tool is the default shape for a decision in this skill; prose is the fallback.

- **First option** = your recommendation. Label it with the choice; its description is `[reason specific to this system]`.
- **Second option** = the meaningful alternative. Its description is `preferable when [condition]`.
- Add further options only if they are genuinely live. Let the tool supply "other" — never write your own.
- Keep `header` to a couple of words, and give every option a one-line consequence so the user chooses between outcomes, not labels.

Only if your agent has no question tool, fall back to prose:

> **Recommendation:** [choice], because [reason specific to this system]. [Alternative] is preferable when [condition]. Does that fit, or should we adjust it?

## Phase 1 — Define the first useful interface

Begin with the sentence the user wants to say:

> What would you like to be able to tell your orchestrator, and what should it make happen?

Examples include “run our delivery loop on issue 123” or “take this approved plan through review.” Use the user's language rather than imposing a named methodology.

Then ask a small set of plain-language questions:

1. What single end-to-end outcome must the first version deliver to be useful?
2. What input will the user give it, and what should exist when it finishes?
3. Which parts already work reliably when invoked independently?
4. What named skill, agent, script, hook, CI workflow, or external action owns each part?
5. What state or artifact proves the whole run succeeded?
6. Where must it stop and ask the user?
7. What must the final digest contain so the user does not need to read a transcript?
8. **What should the first version explicitly not be capable of yet?**

Avoid implementation tools, parallelism, run-file formats, and model selection at this point. Clarify only gaps that materially change the first capability.

Recommend this baseline unless the user's system calls for something different:

- one workstream at a time;
- one proven delivery loop;
- background workers only where they improve the interface;
- deliberate worker continuity and fresh review context;
- authoritative completion evidence;
- one consequential human gate;
- a concise status surface and final digest;
- one simple stall bound.

Do not assume “end to end” includes an automatic fix/re-review cycle, retry, merge, release, or deploy. Ask whether each is already part of the user's trusted loop before including it; otherwise stop with evidence and a recommendation at that seam.

## Phase 2 — Check capability readiness

Before placing a component behind the orchestrator, establish its readiness without running it yet.

For every named component ask:

```text
Can it be invoked by name or a stable command?
Does it accept a stable input?
Does it produce a recognizable output?
Can completion be verified independently of its own claim?
Does failure return actionable evidence?
Has the user run and trusted it independently?
```

Classify each component:

- **PROVEN** — stable enough to orchestrate now.
- **PROVISIONAL** — usable with a human gate or explicit verification.
- **NOT READY** — missing a stable contract or independent evidence.

Recommend building the first route from proven components. A provisional component may be included when the user accepts its gate and failure behavior. Do not hide a not-ready capability inside the orchestrator; recommend pausing to stabilize it separately.

When the user supplies a capability path or asks for discovery, inspect only what is necessary to learn its invocation, input, output, permissions, completion evidence, and failure contract. Do not ingest its entire implementation into the future orchestrator.

## Phase 3 — Propose the capability concept

Translate the answers into the smallest useful capability map. Label nodes as `USER`, `ORCHESTRATOR`, `WORKER`, `CAPABILITY`, `EVIDENCE`, or `HUMAN GATE`. Show context boundaries, evidence, requested observability, and explicit non-capabilities. Omit exact tool calls and configuration until approval.

Use a compact shape such as:

```text
[USER]
“Run our delivery loop on issue X”
    │
    ▼
[ORCHESTRATOR]
coordinate only; one workstream
    │
    ▼
[WORKER — FRESH] invoke investigate capability
    │ investigation artifact
    ▼
[WORKER — FRESH] invoke implement capability
    │ changed branch + validation evidence
    ▼
[SAME WORKER] invoke create-PR capability
    │ PR URL
    ▼
[WORKER — FRESH] invoke review capability
    │ review artifact + CI verdict
    ▼
[HUMAN GATE] approve merge
    │
    ▼
[ORCHESTRATOR] final digest
```

Explain:

- why this is the smallest route that is genuinely useful;
- what the orchestrator coordinates and what workers own;
- why each worker continues or starts fresh;
- what crosses every handoff;
- what proves each stage and the complete run succeeded;
- where the human remains principal;
- what is observable during the run and retained afterward;
- which capabilities are deliberately deferred.

Recommend fresh context for independent review and genuinely new semantic responsibility. Recommend the same worker for correction loops or adjacent work that benefits from repository and intent continuity. Do not treat either as universally better.

Present an explicit capability boundary:

```text
CAN NOW
- run one delivery loop from one work item
- verify artifacts, PR state, and checks
- stop at the merge gate
- return one digest

NOT YET
- coordinate parallel workstreams
- run automatic correction or re-review loops
- merge automatically
- resolve cross-branch conflicts
- resume after the orchestrator session ends
- change the agentic layer
```

Ask the user to approve or iterate on the concept and boundary. Do not proceed until both are settled.

> **Ask this with `AskUserQuestion`.** This is a fork in the design, not an open question, so it belongs in the tool rather than in prose. Put your recommendation first, the meaningful alternative second, and a one-line consequence on each option; let the tool supply "other". Only fall back to prose if your agent has no such tool.

## Phase 4 — Design one capability contract at a time

> **Ask this with `AskUserQuestion`.** This is a fork in the design, not an open question, so it belongs in the tool rather than in prose. Put your recommendation first, the meaningful alternative second, and a one-line consequence on each option; let the tool supply "other". Only fall back to prose if your agent has no such tool.

Resolve capabilities in causal order. Do not configure the whole orchestrator in one questionnaire.

### Capability contract

1. **User intent** — What request should cause the orchestrator to select this capability?
2. **Owned outcome** — What single result does the capability own?
3. **Readiness** — Proven, provisional, or not ready, with evidence?
4. **Invocation** — Which named skill, agent, command, automation, or external action runs it?
5. **Input** — What exact identifier, value, artifact, or repository state does it receive?
6. **Worker** — Same worker, fresh worker, or no agent, and why?
7. **Model** — Does the capability own its model choice, or must the orchestrator select one?
8. **Tools and permissions** — What is the least capability the worker and orchestrator need?
9. **Output** — What exact value, artifact, branch, PR, check, or state comes back?
10. **Completion evidence** — What authority verifies it rather than trusting self-report?
11. **Next owner** — Who receives responsibility afterward?
12. **Live observability** — What status should the user see, and when?
13. **Durable record** — What remains after the handoff?
14. **Failure behavior** — What evidence returns, who decides, and may it retry?
15. **Bound** — Turns, attempts, time, or another current limit?

Recommend the executor, context, evidence, authority, observability, and bound for each capability. If a named skill or agent already owns model and tool choices, do not duplicate those decisions in the orchestrator unless it must override them for a clear reason.

### Handoff rule

For every handoff decide:

- what crosses the boundary;
- whether it is a focused value or durable artifact;
- whether the next owner needs the full artifact or a summary plus path;
- whether the next owner should inherit context or begin independently;
- what objective state gates the transfer;
- what the orchestrator records and tells the user.

Prefer artifacts for responsibilities that cross workers, need review, support recovery, or serve as evidence. Prefer focused values for cheap same-run transfers that need no later inspection. Do not make a transcript the handoff contract.

### Verification and gate rule

For each “done” claim ask:

> What can the orchestrator observe outside the worker's own report that makes this true?

Use the appropriate authority: required artifact, git state, PR state, CI result, issue state, deterministic validation, external API, or human confirmation. When no authority exists, classify the result as a self-report and recommend either adding verification or retaining a gate.

Keep the user as principal. The first orchestrator should stop at the selected consequential seam rather than invent standing decisions or infer approval from silence.

### Digest contract

Design the digest as the primary interface, not an afterthought. Ask what the user must know to trust and act without opening every worker transcript.

Recommend including:

- input and final outcome;
- capability status in one line each;
- links or paths to authoritative artifacts;
- deterministic checks and external verdicts;
- deviations, retries, and unresolved risks;
- the exact decision required from the user;
- recommended next action.

Let the user choose quiet execution, milestone updates, or richer live status. Default to milestone status plus one final digest; avoid narrating every worker action.

After each approval, show progress:

```text
✓ Interface: “run our delivery loop on issue X”
✓ Capability 1: investigate [fresh worker]
  Output: investigation artifact; verified by required sections

→ Capability 2: implement [designing now]
○ Capability 3: create PR
○ Capability 4: independent review
○ Gate: merge approval
○ Digest
```

## Phase 5 — Design the orchestrator's own capabilities

Only after the route is approved, decide what the orchestrator itself needs.

Normally recommend the minimum current abilities to:

- invoke the approved worker capabilities by name;
- launch and observe workers;
- continue or steer the same worker when the approved design requires it;
- read authoritative completion evidence;
- stop or bound stalled work;
- ask the user at the selected gate;
- return milestone status and the final digest.

Do not grant generic product-code editing. If a durable run record is not part of the first concept, do not add write access merely because a mature orchestrator might use it. Scope tools and permissions to coordination and evidence.

Choose the orchestrator model using current official options. Recommend a model capable of reliable multi-step coordination and judgment; use cheaper worker models where their capability contracts allow it. Do not force one model across the entire system.

## Phase 6 — Record the evolution path

Create an evolution ledger without implementing deferred levels:

```text
LEVEL 1 — One useful loop
Sequential delivery, evidence, one gate, digest

LEVEL 2 — Live control
Background execution, status, steering, bounded stalls

LEVEL 3 — Earned autonomy
Standing decisions for repeatedly approved gates

LEVEL 4 — Parallel work
Independent workstreams, isolation, dependency/conflict map

LEVEL 5 — Integration
Merge ordering, rebasing, conflict routing, post-merge verification

LEVEL 6 — Durable operation
Run records, resume, detached execution, recovery

LEVEL 7 — System evolution
Inspect failed runs and propose agentic-layer improvements
```

For every next candidate, record:

- the observed limitation that would justify it;
- evidence to collect from current runs;
- the new authority or risk it introduces;
- the test that must pass before keeping it.

Do not treat the level numbers as mandatory architecture. Remove irrelevant levels and add domain-specific ones when the user's system evolves differently.

## Phase 7 — Review the complete design

Present the final ASCII map, capability ledger, explicit non-capabilities, digest contract, and evolution ledger. Check before writing:

- The first interface controls one coherent end-to-end capability.
- Every component is proven or deliberately gated as provisional.
- The orchestrator coordinates but does not perform domain work.
- Capabilities are composed by stable name and contract.
- Every handoff has explicit input, output, next owner, and evidence.
- Worker continuity and fresh context each have a reason.
- Completion is verified against authority wherever possible.
- The orchestrator has only coordination and evidence permissions it needs.
- A consequential human gate remains at the chosen seam.
- Every loop, retry, and worker is bounded.
- The digest lets the user act without reading transcripts.
- Deferred capabilities have not leaked into implementation.

Ask for final design approval. If the user changes the design, update affected contracts and boundaries before building.

> **Ask this with `AskUserQuestion`.** This is a fork in the design, not an open question, so it belongs in the tool rather than in prose. Put your recommendation first, the meaningful alternative second, and a one-line consequence on each option; let the tool supply "other". Only fall back to prose if your agent has no such tool.

## Phase 8 — Build the orchestrator skill

Confirm the target path and name, then create or update the orchestrator in whatever vessel the chosen agent loads by name — a portable `SKILL.md` for Claude Code, or that agent's equivalent instruction file — with only the resources the approved design needs. Preserve unrelated files and user changes.

A complete worked example lives in `references/orchestrate-issues-SKILL.md` — read it before writing the orchestrator.

Write the orchestrator in the user's language and terminology. Include:

- the interface and accepted inputs;
- the orchestrate-don't-implement role contract;
- the approved route and named capabilities;
- worker continuity and fresh-context decisions;
- handoff and completion-evidence contracts;
- the gate, escalation, and failure rules;
- live status and digest behavior;
- bounds;
- explicit non-capabilities.

Implement only against current official tool behavior. Do not copy a production orchestrator, capability implementations, project-specific paths, storage conventions, exact validation commands, merge policy, or advanced lifecycle machinery unless the user's approved design requires them.

Do not silently add parallelism, worktrees, background execution, steering, standing decisions, auto-merge, persistence, detached processes, self-improvement, or broad permissions.

## Phase 9 — Prove the first capability

Validate progressively:

1. Validate the generated skill's frontmatter, structure, references, and current tool names.
2. Confirm every named capability exists and its actual contract matches the orchestrator's assumption.
3. Exercise input validation, missing capability, malformed/missing artifact, worker failure, stall bound, and gate behavior without meaningful mutation where possible.
4. Run one representative end-to-end input with user approval when it can consume model quota, create branches or PRs, contact external systems, or mutate meaningful state.
5. Verify worker continuity/reset behavior, authoritative evidence, milestone observability, escalation, final digest, and explicit stop at the human gate.
6. Confirm the orchestrator did not implement domain work or invoke deferred capabilities.

If a live run is unsafe or unavailable, validate everything possible and state precisely what remains unverified. Never report the orchestrator as proven from inspection alone.

Use failures from the first real runs to propose the next narrow evolution. Do not automatically modify the orchestrator or agentic layer.

## Final report

Return:

- the orchestrator skill path;
- the final ASCII capability map;
- the capability contracts and readiness classifications;
- explicit current and deferred capabilities;
- context continuity, evidence, gate, bound, and digest decisions;
- the chosen agent, the official documentation, and the installed agent version used;
- validation and live tests performed with results;
- anything unverified;
- the next capability to consider only if current-run evidence justifies it.
