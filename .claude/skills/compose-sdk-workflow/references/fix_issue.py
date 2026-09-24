#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["claude-agent-sdk", "rich"]
# ///
"""
fix_issue.py — ONE stage of the headless fix-issue loop (compose-headless-workflow's fix-issue.sh), translated to the Agent SDK.

The dependencies live in the header above (PEP 723): one file, no venv,
no install step — `uv run fix_issue.py 42` anywhere uv exists. `rich` is
in that same header for exactly one reason: readable terminal output
costs one more line here, not a project setup.

Three things a shell script cannot have:
  1. the session is an OBJECT — the client below IS the implementer's context
  2. your .claude/ layer loads automatically
  3. guard() is asked about tool calls AS THEY HAPPEN, and can say no

Deliberately unchanged: the checks stay a subprocess. Either they exit 0
or they don't. A better harness never absorbs your checks.
"""

import subprocess
import sys
import warnings

from claude_agent_sdk import (
    AssistantMessage,
    CanUseToolShadowedWarning,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    PermissionResultAllow,
    PermissionResultDeny,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    query,
)
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

# Read/Bash are broadly allowed on purpose — only Edit/Write are meant to
# fall through to guard() — so the SDK's warning about that is expected,
# not a sign of a real problem. Silence it instead of letting it print.
warnings.filterwarnings("ignore", category=CanUseToolShadowedWarning)

# The default Windows console codepage can't encode the checkmark below or
# any emoji pulled in from issue text — without this, the script crashes on
# its own status output before it ever finishes. Harmless on platforms that
# are already UTF-8.
sys.stdout.reconfigure(encoding="utf-8")

# legacy_windows=False: Rich's default Win32-console writer bypasses the
# UTF-8 reconfigure above and crashes on the arrow character below on some
# Windows consoles. Forcing the ANSI code path instead fixes it — verified
# by reproducing the crash and confirming this line resolves it.
console = Console(legacy_windows=False)

ISSUE = sys.argv[1] if len(sys.argv) > 1 else sys.exit("usage: fix_issue.py <issue>")

CHECKS_DIR = "app/backend"   # where the checks' config lives — change this first
MAX_FIX_ATTEMPTS = 3         # an unbounded fix loop is money spent on a wall


def run_checks() -> tuple[bool, str]:
    """The deterministic half — no agent involved, no opinions consulted."""
    result = subprocess.run(
        "uv run ruff check . && uv run mypy . && uv run pytest tests -q",
        shell=True, cwd=CHECKS_DIR, capture_output=True, text=True,
    )
    return result.returncode == 0, result.stdout + result.stderr


async def guard(tool_name, tool_input, context):
    """Asked about a tool call WHILE it happens — a script reads the diff after.

    A broadly-allowed tool is auto-approved BEFORE this guard is consulted,
    so Edit/Write stay out of allowed_tools and fall through to here."""
    # Headless — nobody is here to answer an interactive question. Left
    # unguarded, the model can call this (often right after being denied
    # something) and the run stalls waiting for a human who'll never answer.
    if tool_name == "AskUserQuestion":
        console.print(
            "  [bold red]✗ DENIED[/bold red] [yellow]AskUserQuestion[/yellow]"
            "[dim] — headless, no one to answer[/dim]"
        )
        return PermissionResultDeny(
            message="headless run, no one is here to answer — decide yourself and note the assumption"
        )
    # Windows reports file_path with backslashes — a forward-slash check
    # would silently never match there. Normalize before comparing.
    path = str(tool_input.get("file_path", "")).replace("\\", "/")
    if tool_name in ("Edit", "Write") and "alembic/versions" in path:
        return PermissionResultDeny(message="migrations are hand-written here")
    return PermissionResultAllow()


# One color per kind of thing a tool call does — reading, writing, running a
# command, or reaching into the .claude/ layer (the auto-load moment gets
# its own color on purpose, so it visibly stands out when it happens).
_TOOL_STYLES = {
    "Read": "cyan", "Grep": "cyan", "Glob": "cyan", "WebFetch": "cyan", "WebSearch": "cyan",
    "Edit": "yellow", "Write": "yellow", "MultiEdit": "yellow",
    "Bash": "magenta", "PowerShell": "magenta",
    "Skill": "bold green", "Task": "bold green",
}
_DETAIL_KEYS = ("file_path", "command", "pattern", "description", "subagent_type", "prompt", "url", "path")
_MAX_DETAIL_LEN = 80


def _print_tool_call(block: ToolUseBlock) -> None:
    """One clean, colored line per tool call. Different tools name their
    interesting field differently, so try the common ones in order — and
    cut whatever's found to one line, since a multi-line Bash heredoc or a
    long prompt would otherwise dump its whole body into the console."""
    detail = ""
    for key in _DETAIL_KEYS:
        value = block.input.get(key)
        if value:
            detail = str(value).splitlines()[0].strip()
            if len(detail) > _MAX_DETAIL_LEN:
                detail = detail[: _MAX_DETAIL_LEN - 1] + "…"
            break
    style = _TOOL_STYLES.get(block.name, "white")
    label = f"[{style}]{block.name}[/{style}]"
    console.print(f"  [dim]→[/dim] {label}" + (f"[dim]: {detail}[/dim]" if detail else ""))


async def drain(client: ClaudeSDKClient) -> float:
    """query() only SENDS. Iterating receive_response() is what drives the
    turn to completion — forget this and the run silently does nothing.
    Prints each tool call as it happens — the only way to actually SEE the
    .claude/ auto-load claim, since a skill firing is just a Read of its
    SKILL.md, not anything the SDK announces on its own. Returns this
    turn's cost — the implementer's spend is otherwise never surfaced
    anywhere, since only the review call below prints its own."""
    cost = 0.0
    async for message in client.receive_response():
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ToolUseBlock):
                    _print_tool_call(block)
        if isinstance(message, ResultMessage) and message.total_cost_usd:
            cost = message.total_cost_usd
    return cost


async def main() -> None:
    # The implementer. The client IS the session — no session ids, no --resume.
    # Nothing points at our skills or rules: the .claude/ layer loads automatically.
    # allowed_tools is Read+Bash only, so Edit/Write fall through to guard().
    options = ClaudeAgentOptions(
        model="opus",
        allowed_tools=["Read", "Bash"],
        can_use_tool=guard,
    )
    console.print(Rule(f"[bold blue]implementing a fix for issue #{ISSUE}[/bold blue]"))
    implementer_cost = 0.0
    async with ClaudeSDKClient(options=options) as implementer:
        await implementer.query(
            f"Study GitHub issue #{ISSUE}. Investigate the fix, then fix the issue."
        )
        implementer_cost += await drain(implementer)

        # Same bounded loop as the shell version — failures go back into the
        # SAME context, because it remembers what it just wrote.
        for attempt in range(1, MAX_FIX_ATTEMPTS + 1):
            ok, output = run_checks()
            if ok:
                console.print("[bold green]✓ checks pass[/bold green]")
                break
            console.print(
                f"[bold yellow]→ checks failed ({attempt}/{MAX_FIX_ATTEMPTS})[/bold yellow] — handing back"
            )
            await implementer.query(f"The checks failed. Fix them:\n\n{output}")
            implementer_cost += await drain(implementer)
        else:
            console.print("[bold red]✗ still failing — stopping so a human can look[/bold red]")
            sys.exit(1)

    # The review: one-shot, nothing carried over — the missing --resume,
    # as a function call. Cheaper model: reading a diff doesn't need the strong brain.
    console.print(Rule(f"[bold blue]reviewing the fix for issue #{ISSUE}[/bold blue]"))
    review_text = ""
    review_cost = 0.0
    async for message in query(
        prompt=f"Review the changes for issue #{ISSUE}. "
               "List findings worst-first, BLOCKER or NIT.",
        options=ClaudeAgentOptions(model="sonnet",
                                   allowed_tools=["Read", "Bash"]),
    ):
        if isinstance(message, AssistantMessage):
            # Overwrite, don't append: the model narrates in short text
            # fragments between tool calls ("let's check X now") on the
            # way to the actual review — appending them all runs sentences
            # together with no separator. The LAST text this turn produces
            # is the finished review; that's the only one worth keeping.
            text_parts = [b.text for b in message.content if isinstance(b, TextBlock)]
            if text_parts:
                review_text = "\n\n".join(text_parts)
            for block in message.content:
                if isinstance(block, ToolUseBlock):
                    _print_tool_call(block)
        elif isinstance(message, ResultMessage) and message.total_cost_usd:
            review_cost = message.total_cost_usd

    console.print(Panel(review_text.strip(), title="review", border_style="blue", padding=(1, 2)))

    total = implementer_cost + review_cost
    console.print(Panel(
        f"issue #{ISSUE}\n"
        f"implementer  [cyan]${implementer_cost:.2f}[/cyan]\n"
        f"review       [cyan]${review_cost:.2f}[/cyan]\n"
        f"total        [bold green]${total:.2f}[/bold green]",
        title="[bold green]✓ done[/bold green]", border_style="green",
    ))


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
