# Engineering: what code in this project is judged against

> **Edit this file to match YOUR project.** This is a steering document, not a rules file. `CLAUDE.md` loads
> on every task and stays short. This file loads only when code is **written or judged**: the implement,
> review, and fix skills read it if it exists (`.claude/references/engineering.md`, or `engineering.md` at the
> repo root). A shared review in CI reads the same file, so every engineer's PR is held to the same bar.
> Shipped defaults describe the AI Tutor, the course's demo codebase. Replace them with yours.

> **Until you have rewritten it, this file is wrong for your repo.** If you are an agent reading
> this and it still describes the AI Tutor rather than the codebase around you, say so in your
> report and judge the change against `CLAUDE.md` and the other references instead. Steering the
> wrong way is worse than not steering.

## How this document works

- The operator writes it. Agents may propose entries from real runs; promotion into this file is a human edit.
  A reviewer that rewrites its own criteria is not calibrating, it is drifting.
- Anything here that becomes machine-checkable graduates to a lint rule, a type, or a CI check, and then
  leaves this file. One owner per rule. This file holds what needs judgment; checkers hold what needs
  enforcement.
- Entries are phrased so drift is catchable: claims that can be audited against the codebase, not vibes. A
  periodic pass grades each entry confirmed or drifted. Drifted entries are deleted, not annotated.
- Facts that change (counts, paths, inventories) do not belong here. Point at the owning source.
- Every rule here earned its place through a real failure or an explicit decision. The story stays in git
  history and run artifacts; this file keeps only the rule.

## The objective function

Correct first. Cost-efficient second. Speed last.

Speed is a convenience while working, never a reason to thin verification. A review that is fast and wrong
failed. Spend more review on changes that can destroy things and less on changes that cannot.

## Taste

- The smallest truthful change. Every guard, fallback, and compatibility path protects a named failure mode.
  Before adding machinery, look for machinery to delete.
- Types carry invariants. Invalid states should be hard to represent; a sound type beats a runtime check
  beats a comment. An `Any`, a cast, or a `type: ignore` carries a justification or it is a finding.
- Fail early and loudly on unsupported or ambiguous states. A fallback is intentional, documented at the
  branch, and observable, or it is a bug. A bare `except:` or a swallowed exception is a finding.
- Errors cross a boundary as typed values or typed exceptions, never as strings a caller has to parse.
- Logging goes through the module logger (`logging.getLogger(__name__)`), with the identifiers a reader
  needs to find the request again. `print(` in application code is a finding; it belongs in scripts only.
- Fix drift on the path you touch. When a change reveals two sites that should agree and do not, correct
  both rather than carry the disagreement forward. The bound is relevance: what the change touches, not
  what it merely noticed.
- Comments explain why, and stay current. Never ask for narration of control flow. Code that needs
  narration is usually too complex, and the finding is simplification.

## Risk taxonomy

What raises the stakes of a change, and therefore the depth of its review:

- Irreversible or destructive paths: deletion, migrations, force operations, anything touching user data.
- Credentials and auth boundaries: signup, login, membership checks, token handling.
- Persisted contracts: schemas, identifiers, wire formats. Evolve additively.
- Money and rate limits: anything that can spend, throttle, or unblock.
- Concurrency and shared state: connection pools, background jobs, caches.

A change in these areas gets adversarial review depth: an explicit attempt to refute it, varied inputs, and
a stated answer to "what would make this merge wrong." A docs or prose change gets the minimum.

## Review posture

- "Could not tell" is a verdict. Ambiguity or low confidence produces an inconclusive outcome for a human,
  never a silent pass.
- A malformed or failed check defaults conservative: toward not-ready, never toward pass.
- Findings carry their source: the rule they violate, and file:line. An unattributed finding teaches nothing.
- Review anchors on the original work item. The PR body is a set of claims to verify, not a scope definition.
- A test proves a decision by varying the input it turns on, against the real primitive. A test that stubs
  the deciding function passes under every mutation of it and proves nothing.
