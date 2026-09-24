#!/usr/bin/env bash
#
# fix-issue.sh — a whole bug-fix loop, run without you.
#
# Three things a prompt alone cannot do:
#   1. a DETERMINISTIC check between the steps
#   2. failure fed back into the SAME context
#   3. hand-off to a FRESH context
#
# Usage:  ./fix-issue.sh 42

set -euo pipefail

ISSUE="${1:?usage: ./fix-issue.sh <issue-number>}"

# Where the checks' config lives — the first line you change for your project.
CHECKS_DIR="app/backend"

# An unbounded fix loop is money spent on a wall.
MAX_FIX_ATTEMPTS=3

# Auth comes from your login — the subscription, same as interactive. No keys here.

# One non-interactive call. JSON out so we get the session id back.
ask() {
  local prompt="$1"; shift
  claude -p "$prompt" \
    --output-format json \
    "$@"
}

# The deterministic half. No agent involved, no opinions consulted.
run_checks() {
  ( cd "$CHECKS_DIR" \
    && uv run ruff check . \
    && uv run ruff format --check . \
    && uv run mypy . \
    && uv run pytest tests -q )
}

# ── 1. IMPLEMENT ─────────────────────────────────────────────────────────────
# The prompt is just the job — an example prompt; your own skills go here.
# Nothing about checks: the pipeline runs them next regardless.
echo "→ implementing a fix for issue #$ISSUE"
response=$(ask "Study GitHub issue #$ISSUE. Investigate the fix, then fix the issue." \
  --model opus \
  --allowedTools "Read,Edit,Write,Bash")

session=$(jq -r '.session_id' <<<"$response")

# ── 2. VALIDATE — failures go back to the SAME context ───────────────────────
attempt=1
while true; do
  if checks_output=$(run_checks 2>&1); then
    echo "✓ checks pass"
    break
  fi

  if (( attempt > MAX_FIX_ATTEMPTS )); then
    echo "✗ still failing after $MAX_FIX_ATTEMPTS attempts — stopping so a human can look"
    echo "$checks_output" | tail -20
    exit 1
  fi

  echo "→ checks failed (attempt $attempt/$MAX_FIX_ATTEMPTS) — handing the output back"
  ask "The checks failed. Fix them. Here is the exact output:

$checks_output" --resume "$session" --allowedTools "Read,Edit,Write,Bash" >/dev/null

  (( attempt++ ))
done

# ── 3. OPEN THE PR — same context, it remembers what it built ────────────────
echo "→ opening the PR"
ask "Push the branch and open a pull request for issue #$ISSUE." \
  --resume "$session" --allowedTools "Read,Bash" >/dev/null

# ── 4. REVIEW — two FRESH contexts, in parallel ──────────────────────────────
# No --resume on either: neither has seen the implementation.
# claude invokes the review skill by name; codex reads the same file.
# Reviewers write nothing, so they can't collide — &, &, wait.
echo "→ reviewing (two fresh contexts: logic · failure handling)"
ask "/piv-review-changes Review the open pull request for issue #$ISSUE with one
question only: is the logic right? Wrong behavior, broken edge cases, off-by-one
thinking. Ignore style. List findings worst-first. Mark each BLOCKER or NIT.
Write no files — this script captures your answer from stdout." \
  --model sonnet --allowedTools "Read,Bash" \
  | jq -r '.result' > review-logic.md &

codex exec "First read .claude/skills/piv-review-changes/SKILL.md — that is how
we review in this project. Then review the open pull request for issue #$ISSUE
with one question only: what happens when things fail? Missing error handling,
swallowed exceptions, unchecked inputs. Ignore style. List findings worst-first.
Mark each BLOCKER or NIT. Write no files — this script captures your answer
from stdout." > review-errors.md &

wait

# A reviewer producing no output (rate limit, crash, auth failure) is not the
# same as a reviewer finding nothing — silently feeding empty content forward
# would look like a clean bill of health from a panel that only half-ran.
for review_file in review-logic.md review-errors.md; do
  if [[ ! -s "$review_file" ]]; then
    echo "⚠ $review_file came back empty — that reviewer likely failed (rate limit, crash, or auth issue), not found-nothing." >&2
    echo "REVIEWER FAILED TO PRODUCE OUTPUT — do not treat this as a clean review. Investigate and re-run this reviewer before merging; a missing review is not evidence the code is fine." > "$review_file"
  fi
done

# ── 5. FEED BOTH REVIEWS BACK to the implementer ─────────────────────────────
echo "→ addressing the reviews"
final=$(ask "Two reviewers looked at your pull request — one asked whether the
logic is right, one asked what happens when things fail. Their findings are below.

Validate them first — some may be wrong, and you are allowed to disagree in writing.
Fix the BLOCKERs and push. If anything here is unrelated to this PR, don't fix it:
tell me it should be a follow-up issue instead.

## Logic
$(cat review-logic.md)

## Failure handling
$(cat review-errors.md)" --resume "$session" --allowedTools "Read,Edit,Write,Bash")
jq -r '.result' <<<"$final"

# Every JSON response carries its own price tag.
echo "✓ done — issue #$ISSUE (last call cost \$$(jq -r '.total_cost_usd' <<<"$final"))"
