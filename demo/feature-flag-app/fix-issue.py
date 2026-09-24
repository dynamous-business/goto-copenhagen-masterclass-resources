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

Configured for the feature-flag exercise (the masterclass "five ways" demo).
Prerequisites: `uv`, a logged-in Claude Code CLI, `gh`, pnpm with both packages installed.
The template this came from: goto-copenhagen-masterclass-resources/automations/fix_issue.py
"""

import subprocess
import sys

from claude_agent_sdk import (
    ClaudeAgentOptions,
    ClaudeSDKClient,
    PermissionResultAllow,
    PermissionResultDeny,
    ResultMessage,
    query,
)

ISSUE = sys.argv[1] if len(sys.argv) > 1 else sys.exit("usage: fix-issue.py <issue>")

# where the checks' config lives — change this first
CHECKS_DIR = "."

CHECKS_CMD = "(cd server && pnpm run build && pnpm run lint && pnpm test) && (cd client && pnpm run build && pnpm run lint)"

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

    # shared/types.ts is the data contract for both packages. A bug fix should
    # never need to change it, so the guard says no, and says why, mid-run.
    NEVER_TOUCH = ("shared/types.ts",)

    if tool_name in ("Edit", "Write") and any(p in path for p in NEVER_TOUCH):
        return PermissionResultDeny(
            message="shared/types.ts is the data contract. Fix the bug without changing it, "
                    "or stop and explain why the contract must change.")
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
    print(f"→ implementing a fix for issue #{ISSUE}")
    async with ClaudeSDKClient(options=options) as implementer:
        await implementer.query(
            f"Study GitHub issue #{ISSUE}. Create a branch fix/issue-{ISSUE}, investigate the fix, "
            "then fix the issue with a regression test. Commit when the checks pass."
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
    print("→ reviewing in a fresh context")
    async for message in query(
        prompt=f"Review the changes for issue #{ISSUE}. "
               "List findings worst-first, BLOCKER or NIT.",
        options=ClaudeAgentOptions(model="sonnet",
                                   allowed_tools=["Read", "Bash"]),
    ):
        if isinstance(message, ResultMessage):      # only the final answer, not every event
            print(message.result)
            print(f"✓ done — issue #{ISSUE} (review cost ${message.total_cost_usd:.2f})")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
