#!/bin/bash
#
# baton.sh — the BATON. One skill's artifact starts the next skill, in a
# FRESH context. Runs with "async": true so the finishing session isn't
# held open.
#
# The guard reads STATE, not memory — it can fire a hundred times and act
# once: no artifact → not our event · fix report exists → done (this is
# also the recursion guard) · in-flight marker on disk → already running.

set -uo pipefail

# If the spawned session below dies before reaching `rm -f "$inflight"` (killed,
# crashed, or blocked by an unrelated hook bug), the marker is orphaned and this
# guard would otherwise skip that issue forever — silently, with no error. A
# stale-past-this-long marker is treated as a dead spawn, not a running one.
STALE_MINUTES=15

INPUT=$(cat)
cd "$CLAUDE_PROJECT_DIR"

for artifact in docs/issues/issue-*.md; do
  [ -e "$artifact" ] || exit 0

  n=$(basename "$artifact" .md)
  n=${n#issue-}
  done_marker="docs/issues/fix-report-$n.md"   # piv-implement-issue saves its report here
  inflight="docs/issues/.baton-$n.inflight"

  [ -f "$done_marker" ] && continue

  if [ -f "$inflight" ]; then
    if [ -z "$(find "$inflight" -mmin +$STALE_MINUTES 2>/dev/null)" ]; then
      exit 0   # genuinely still running (or too new to tell) — leave it alone
    fi
    echo "baton: $inflight is stale (>${STALE_MINUTES}m, no fix report) — the prior spawn likely died; retrying" >&2
    rm -f "$inflight"
  fi

  # One event, one hand-off.
  # `< /dev/null`: this hook's own stdin came from Claude Code's async-hook
  # runner, not a terminal — leaving the spawned session to inherit it caused
  # real, reproducible silent stalls (confirmed live: the process just never
  # progressed past its first tool call, with nothing in the logs, twice in a
  # row, and only when spawned this way — a manual `claude -p` run of the
  # exact same command every time worked fine). Give it its own empty stdin.
  touch "$inflight"
  claude -p "/piv-implement-issue $n" \
    --allowedTools "Read,Edit,Write,Bash" \
    < /dev/null \
    > "docs/issues/.baton-$n.log" 2>&1
  rm -f "$inflight"
  exit 0
done

exit 0
