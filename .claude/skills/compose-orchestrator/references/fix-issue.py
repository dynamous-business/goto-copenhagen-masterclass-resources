#!/usr/bin/env python3
"""
fix-issue.py — investigate and implement a fix, with a deterministic validation
loop, then stop. Scoped down from fix-issue.sh on purpose: this script owns only
the part a prompt alone can't do reliably —

  1. a DETERMINISTIC check between investigate/implement and "done"
  2. failure fed back into the SAME context (the fix loop)

— and stops there. PR creation and review are NOT this script's job anymore:
hand off to a fresh agent for those (the orchestrator's own pr/review stages,
or run them yourself). That's a fresh context reviewing work it didn't write,
same law as everywhere else in this act.

Auth comes from your login — the subscription, same as interactive. No keys here.

Usage: ./fix-issue.py 42
"""

from __future__ import annotations

import json
import subprocess
import sys

# Windows' default console codepage (cp1252) can't encode the → glyphs below,
# raising UnicodeEncodeError the first time a print() hits one. Force UTF-8 on
# stdout/stderr so this runs the same on Windows as everywhere else, rather
# than relying on the caller to set PYTHONIOENCODING=utf-8.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Where the checks' config lives — the first line you change for your project.
CHECKS_DIR = "app/backend"

# An unbounded fix loop is money spent on a wall.
MAX_FIX_ATTEMPTS = 3


def ask(prompt: str, *extra_args: str) -> dict:
    """One non-interactive call. JSON out so we get the session id back."""
    result = subprocess.run(
        ["claude", "-p", prompt, "--output-format", "json", *extra_args],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def run_checks() -> tuple[bool, str]:
    """The deterministic half. No agent involved, no opinions consulted."""
    proc = subprocess.run(
        "uv run ruff check . && uv run ruff format --check . "
        "&& uv run mypy . && uv run pytest tests -q",
        shell=True,
        cwd=CHECKS_DIR,
        capture_output=True,
        text=True,
    )
    return proc.returncode == 0, proc.stdout + proc.stderr


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("usage: ./fix-issue.py <issue-number>")
    issue = sys.argv[1]

    # ── 1. IMPLEMENT (investigate + fix, one call) ───────────────────────────
    # The prompt is just the job — an example prompt; your own skills go here.
    # Nothing about checks: step 2 runs them regardless.
    print(f"→ implementing a fix for issue #{issue}")
    response = ask(
        f"Study GitHub issue #{issue}. Investigate the fix, then fix the issue.",
        "--model",
        "opus",
        "--allowedTools",
        "Read,Edit,Write,Bash",
    )
    session = response["session_id"]

    # ── 2. VALIDATE — failures go back to the SAME context ───────────────────
    attempt = 1
    while True:
        ok, output = run_checks()
        if ok:
            print("✓ checks pass")
            break

        if attempt > MAX_FIX_ATTEMPTS:
            print(f"✗ still failing after {MAX_FIX_ATTEMPTS} attempts — stopping so a human can look")
            print("\n".join(output.splitlines()[-20:]))
            sys.exit(1)

        print(f"→ checks failed (attempt {attempt}/{MAX_FIX_ATTEMPTS}) — handing the output back")
        ask(
            f"The checks failed. Fix them. Here is the exact output:\n\n{output}",
            "--resume",
            session,
            "--allowedTools",
            "Read,Edit,Write,Bash",
        )
        attempt += 1

    # ── STOP. No PR, no review — that's the next agent's job, not this script's.
    print(
        f"✓ done — issue #{issue} implemented and validated locally, on its branch. "
        f"Hand off to a fresh agent for the pr and review stages next."
    )


if __name__ == "__main__":
    main()
