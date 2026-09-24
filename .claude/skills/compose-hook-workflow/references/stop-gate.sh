#!/bin/bash
#
# stop-gate.sh — the GATE. Fires when the agent thinks it's done (Stop).
# Green → allowed to finish. Red → blocked, with the failure as the reason.
#
# The mechanism is the same one pre_tool_use.py uses: **exit 2 blocks**.
# Per the hooks docs, exit 2 on a Stop event "prevents Claude from stopping"
# and continues the conversation, and the blocking reason is read from stderr.
# Note the translation: your checkers exit 1 on failure, and exit 1 does NOT
# block — only exit 2 does. Converting one to the other is the whole job.
#
# The guard reads STATE, not memory: a clean worktree means nothing was built,
# so there is nothing to gate.

set -uo pipefail

INPUT=$(cat)

cd "$CLAUDE_PROJECT_DIR" || exit 0
if ! git status --porcelain | grep -q .; then
  exit 0   # clean tree — nothing was built, nothing to gate
fi

# ── The bound ────────────────────────────────────────────────────────────────
# `stop_hook_active` is true whenever this Stop was itself triggered by a
# previous block — but it is a boolean, not a count, and it goes true on the
# very FIRST retry and stays true after. Treating "active" as "let it through"
# (an earlier version of this script did) means the gate blocks exactly once
# per session and then waves through every retry after, checks red or not —
# verified live: a session that never touched a file was still allowed to
# finish with a failing test sitting in the tree. The harness gives no count
# to bound on, so — same as everywhere else in this phase — the script bounds
# itself: a small per-session counter on disk, the same shape as baton.sh's
# in-flight marker, because a hook has no memory and has to read state.
MAX_GATE_ATTEMPTS=3
session_id=$(echo "$INPUT" | jq -r '.session_id // "unknown"')
state_dir=".claude/hooks/.gate-state"
mkdir -p "$state_dir"
counter_file="$state_dir/$session_id.count"
attempt=$(( $(cat "$counter_file" 2>/dev/null || echo 0) + 1 ))

# ── The checks — the same ones the headless fix-issue script runs ─────────────────────────────
if checks_output=$(cd app/backend && uv run ruff check . && uv run mypy . && uv run pytest tests -q 2>&1); then
  rm -f "$counter_file"
  exit 0   # green — allowed to finish
fi

if [ "$attempt" -ge "$MAX_GATE_ATTEMPTS" ]; then
  rm -f "$counter_file"
  {
    echo "Still red after $MAX_GATE_ATTEMPTS attempts — letting the stop through so a human can look. Last output:"
    echo
    echo "$checks_output" | tail -30
  } >&2
  exit 0   # the bound giving up on purpose, not the checks passing
fi

echo "$attempt" > "$counter_file"

# ── Red checks → block the stop, failure as the reason ───────────────────────
# stderr is what the agent is told. exit 2 is what stops it finishing.
{
  echo "The checks failed (attempt $attempt/$MAX_GATE_ATTEMPTS). Fix them before finishing. Output:"
  echo
  echo "$checks_output" | tail -30
} >&2
exit 2
