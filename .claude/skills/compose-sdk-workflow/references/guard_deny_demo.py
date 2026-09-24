#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["claude-agent-sdk", "rich"]
# ///
"""
guard_deny_demo.py — the in-process guard, denying something, on camera.

fix_issue.py's own real fixes never happen to touch a migration file, so
the deny never has anything to fire on there. This is the same guard,
the same idea, aimed at a task that WILL try to edit one — a separate,
deliberate beat, not a build-story. Cheap: one small prompt, no issue
investigation, no checks loop.
"""

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
)
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

warnings.filterwarnings("ignore", category=CanUseToolShadowedWarning)
sys.stdout.reconfigure(encoding="utf-8")
console = Console(legacy_windows=False)

_TOOL_STYLES = {"Read": "cyan", "Grep": "cyan", "Glob": "cyan", "Edit": "yellow", "Write": "yellow", "Bash": "magenta", "PowerShell": "magenta"}


def _print_tool_call(block: ToolUseBlock) -> None:
    for key in ("file_path", "command", "pattern"):
        value = block.input.get(key)
        if value:
            detail = str(value).splitlines()[0].strip()
            style = _TOOL_STYLES.get(block.name, "white")
            console.print(f"  [dim]→[/dim] [{style}]{block.name}[/{style}][dim]: {detail}[/dim]")
            return
    console.print(f"  [dim]→[/dim] {block.name}")


async def guard(tool_name, tool_input, context):
    """The exact guard from fix_issue.py — same code, same rule."""
    # Headless — nobody is here to answer an interactive question. Left
    # unguarded, the model can call this after being denied something
    # and the run stalls waiting for a human who will never respond.
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
        console.print(
            f"  [bold red]✗ DENIED[/bold red] [yellow]{tool_name}[/yellow][dim]: {path}[/dim]"
            f" [dim]— migrations are hand-written here[/dim]"
        )
        return PermissionResultDeny(message="migrations are hand-written here")
    return PermissionResultAllow()


async def main() -> None:
    options = ClaudeAgentOptions(
        model="opus",
        allowed_tools=["Read", "Bash"],
        can_use_tool=guard,
    )
    console.print(Rule("[bold blue]the guard, live[/bold blue]"))
    cost = 0.0
    async with ClaudeSDKClient(options=options) as client:
        await client.query(
            "Add a one-line comment at the top of the oldest file in "
            "app/backend/alembic/versions/ explaining what it does."
        )
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, ToolUseBlock):
                        _print_tool_call(block)
                    if isinstance(block, TextBlock) and block.text.strip():
                        console.print(f"  [dim]{block.text.strip()}[/dim]")
            if isinstance(message, ResultMessage) and message.total_cost_usd:
                cost = message.total_cost_usd
    console.print(Panel(f"cost  [cyan]${cost:.2f}[/cyan]", title="[bold green]✓ done[/bold green]", border_style="green"))


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
