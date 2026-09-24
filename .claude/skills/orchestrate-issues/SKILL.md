---
name: orchestrate-issues
description: Run the issue pipeline end to end — investigate, implement, PR, review — through background agents, with gates, a cap, and a digest. Send it one issue or several; it runs them in parallel and reports once.
---

# Orchestrate Issues

Send an agent this prompt exactly, where X is the input: run the investigate skill on X.
When the investigation is done, send a new agent: run the implement skill on the artifact.
When the implementation is done, send the SAME agent: now run the pr skill.
When the PR is up, send a NEW agent: run the review skill on it.

Send me one digest when everything is done. Don't narrate while things run.
I might send you more of these — run them in parallel.

## The vessel

For investigate and implement, run ./fix-issue.py X instead — it validates its own fix in a
deterministic loop before handing back. It's a script, not a persistent agent, so there's no
session to resume: unlike above, send a NEW agent for the pr skill too, then continue as before.
Before reporting a PR done, wait for its CI check to finish.

## The upgrade pass

- Run stages as background agents; completion comes to you as a notification.
- If a stage is off course, message the SAME agent with a correction — steering beats respawning.
- Before reporting a stage done, check the authority: the PR exists, the checks are green, the artifact
  landed. An agent saying "done" is a claim; a green PR is a fact.
- At every merge or destructive step: if a standing decision covers it, act and record it; if not, send me a
  short digest and wait.
- At most three workstreams in parallel. A stage that stalls twice gets stopped and escalated, not restarted.
- A dead agent sends no notification at all — waiting for one is not a detection method. If a dispatched stage
  has produced no notification and no new evidence (a file, a commit, a reply) for about 20 minutes, check its
  status directly rather than keep waiting. Treat that silence as the first stall, the same as an explicit
  failure — it counts toward the cap above.
- The 20 minutes is a limit, not an opening offer — don't extend it because the agent seems close. Giving it
  "a bit more time" past that mark isn't patience, it's the second stall arriving late.
- The status check itself can go unanswered too — a truly dead agent won't respond to that either. Give the
  check its own short timeout (a few minutes, not another 20); silence on the check confirms the stall, it
  doesn't restart the clock. If the second stall is a check that never answers, stop retrying and finish the
  workstream yourself from whatever real work it already produced — don't send a third message into a process
  that's gone.

## When it goes wrong

If a workstream fails its gate twice or stalls, run the opportunity-scan on that run's artifacts — include
the symptom and what ran — and put its proposals in the digest. Never change the AI layer without my go.
