#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["claude-agent-sdk"]
# ///
"""
fix_issue.py — ONE stage of the `fix-issue.sh` fix loop, translated to the Agent SDK.

The dependencies live in the header above (PEP 723): one file, no venv,
no install step — `uv run fix_issue.py 42` anywhere uv exists.

Three things a shell script cannot have:
  1. the session is an OBJECT — the client below IS the implementer's context
  2. your .claude/ layer loads automatically
  3. guard() is asked about tool calls AS THEY HAPPEN, and can say no

Deliberately unchanged: the checks stay a subprocess. Either they exit 0
or they don't. A better harness never absorbs your checks.

--- TEMPLATE ---------------------------------------------------------------
This is a REFERENCE TEMPLATE, not a runnable script. Copy it to your own repo
root and replace every `<<< CONFIGURE: ... >>>` marker below before running.

Configure before first run:
  1. CHECKS_DIR   - the directory your checks run in
  2. CHECKS_CMD   - your project's real check chain
  3. guard()      - your own never-touch paths (the `migrations/` rule is an
                    example, not a default)
Prerequisites: `uv`, and a logged-in Claude Code CLI. The PEP 723 header above
installs `claude-agent-sdk` for you, so there is nothing else to install.
----------------------------------------------------------------------------
"""

import subprocess
import sys

from claude_agent_sdk import (
    ClaudeAgentOptions,
    ClaudeSDKClient,
    PermissionResultAllow,
    PermissionResultDeny,
    query,
)

ISSUE = sys.argv[1] if len(sys.argv) > 1 else sys.exit("usage: fix_issue.py <issue>")

# where the checks' config lives — change this first
# <<< CONFIGURE: the directory your checks run in, relative to this script.
#     e.g. "app/backend", "packages/api", or "." if they run at the repo root. >>>
CHECKS_DIR = "<<< CONFIGURE: path/to/your/checks/dir >>>"

# <<< CONFIGURE: YOUR project's real check chain — the same commands you'd run
#     before opening a PR. Each one MUST exit non-zero on failure; that exit
#     code is the entire gate. A check that prints "FAILED" and exits 0 makes
#     this loop a no-op.
#     e.g.  "npm run lint && npm run typecheck && npm test"
#           "make lint && make test"
#           "uv run ruff check . && uv run mypy . && uv run pytest -q"        >>>
CHECKS_CMD = "<<< CONFIGURE: your-lint && your-typecheck && your-tests >>>"

MAX_FIX_ATTEMPTS = 3         # an unbounded fix loop is money spent on a wall


def run_checks() -> tuple[bool, str]:
    """The deterministic half — no agent involved, no opinions consulted."""
    result = subprocess.run(
        CHECKS_CMD,
        shell=True, cwd=CHECKS_DIR, capture_output=True, text=True,
    )
    return result.returncode == 0, result.stdout + result.stderr


async def guard(tool_name, tool_input, context):
    """Asked about a tool call WHILE it happens — a script reads the diff after.

    A broadly-allowed tool is auto-approved BEFORE this guard is consulted,
    so Edit/Write stay out of allowed_tools and fall through to here."""
    path = str(tool_input.get("file_path", ""))

    # <<< CONFIGURE: YOUR never-touch paths go here. The `migrations/` rule
    #     below is an EXAMPLE of the shape, not a default — replace it with the
    #     paths that are hand-written or generated in your project (schema
    #     migrations, vendored code, lockfiles, infra manifests, secrets).
    #     Add one clause per rule; the deny message is handed back to the agent
    #     verbatim, so say WHY and it will adapt instead of retrying.          >>>
    NEVER_TOUCH = ("migrations/",)  # <<< CONFIGURE: replace with your own >>>

    if tool_name in ("Edit", "Write") and any(p in path for p in NEVER_TOUCH):
        return PermissionResultDeny(message="migrations are hand-written here")
    return PermissionResultAllow()


async def drain(client: ClaudeSDKClient) -> None:
    """query() only SENDS. Iterating receive_response() is what drives the
    turn to completion — forget this and the run silently does nothing."""
    async for _message in client.receive_response():
        pass


async def main() -> None:
    # The implementer. The client IS the session — no session ids, no --resume.
    # Nothing points at our skills or rules: the .claude/ layer loads automatically.
    # allowed_tools is Read+Bash only, so Edit/Write fall through to guard().
    options = ClaudeAgentOptions(
        model="opus",
        allowed_tools=["Read", "Bash"],
        can_use_tool=guard,
    )
    async with ClaudeSDKClient(options=options) as implementer:
        await implementer.query(
            f"Study GitHub issue #{ISSUE}. Investigate the fix, then fix the issue."
        )
        await drain(implementer)

        # Same bounded loop as the shell version — failures go back into the
        # SAME context, because it remembers what it just wrote.
        for attempt in range(1, MAX_FIX_ATTEMPTS + 1):
            ok, output = run_checks()
            if ok:
                print("✓ checks pass")
                break
            print(f"→ checks failed ({attempt}/{MAX_FIX_ATTEMPTS}) — handing back")
            await implementer.query(f"The checks failed. Fix them:\n\n{output}")
            await drain(implementer)
        else:
            sys.exit("✗ still failing — stopping so a human can look")

    # The review: one-shot, nothing carried over — the missing --resume,
    # as a function call. Cheaper model: reading a diff doesn't need the strong brain.
    async for message in query(
        prompt=f"Review the changes for issue #{ISSUE}. "
               "List findings worst-first, BLOCKER or NIT.",
        options=ClaudeAgentOptions(model="sonnet",
                                   allowed_tools=["Read", "Bash"]),
    ):
        print(message)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
