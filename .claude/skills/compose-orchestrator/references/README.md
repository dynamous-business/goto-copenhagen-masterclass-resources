# Reference example

| File | What it is |
|---|---|
| `orchestrate-issues-SKILL.md` | The orchestrator itself — the same file shipped as the `orchestrate-issues` skill. |
| `fix-issue.py` | The vessel it calls: investigate + implement + a deterministic validation loop, then stops and hands off to fresh PR and review agents. |

`orchestrate-issues-SKILL.md` is a real working orchestrator, not a template — and it is worth reading mostly for how **short** it is. It runs one issue pipeline end to end (investigate, implement, PR, review) by naming capabilities it does not implement, and it says out loud which worker is fresh and which is the same one. Everything else in it is a rule the first version earned: check the authority before reporting a stage done, because an agent saying "done" is a claim and a green PR is a fact; steer a drifting agent rather than respawning it; stop at merge unless a standing decision covers it; at most three workstreams in parallel, and a stage that stalls twice is escalated, not restarted.

Change two things for your own system. The **capability names** are the whole contract — `investigate`, `implement`, `pr`, `review`, `opportunity-scan` and the `./fix-issue.py` vessel (in this folder) are this repository's, so substitute the skills and scripts you have already run independently and trust. The second is the **gate and the cap**: where the orchestrator must stop and ask you, and how many workstreams may run at once, are decisions about your risk tolerance, not defaults to inherit. Resist copying more than this: the file is small on purpose, and a first orchestrator that arrives with parallelism, run files, and recovery protocols has skipped the evidence that would justify them.
