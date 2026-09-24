# Reference examples

| File | What it is |
|---|---|
| `fix_issue.py` | The complete SDK program — the bug-fix loop with the session as an object. |
| `guard_deny_demo.py` | The same guard aimed at a task that *will* try to edit a protected file, so the deny actually fires. `fix_issue.py`'s real fixes never happen to touch one. |
| `claude-python-mechanics.md` | SDK mechanics to consult **after** the topology is settled — patterns to select from, not a program to copy. |

`fix_issue.py` is a complete SDK program: the same bug-fix loop as the headless script, but with the session as an **object** rather than a resumed id. It shows the three things a shell script cannot have — a client that *is* the implementer's context, the project's agent layer loading automatically, and `guard()` being asked about tool calls as they happen and allowed to say no. It is a real working program, not a template: PEP 723 dependencies in the header, so `uv run fix_issue.py 42` needs no venv and no install step.

Read it for the shape, then change two things for your own project. `CHECKS_DIR` and the command inside `run_checks()` are your project's authoritative checks — note that they deliberately stay a subprocess, because a better harness never absorbs your checks. The second is `guard()`: the protected paths there (`alembic/versions`, and a blanket deny on `AskUserQuestion` because nobody is there to answer in a headless run) are example policy, so replace them with what your repository actually needs. Note it normalizes backslashes before matching — a forward-slash-only check silently never fires on Windows. Two mechanics are load-bearing and should survive any rewrite: `drain()` exists because `query()` only *sends* and iterating the response is what drives the turn to completion, and `Edit`/`Write` are kept out of `allowed_tools` precisely so they fall through to the guard instead of being auto-approved.
