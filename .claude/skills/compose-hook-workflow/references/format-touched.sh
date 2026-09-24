#!/bin/bash
#
# format-touched.sh — the REACT hook. After every Edit/Write, the touched
# Python file comes out formatted. The event guarantees what a rule can
# only ask.
#
# Formatting is a courtesy, never a blocker: this hook always exits 0.
# Even if it wanted to complain, PostToolUse cannot block — the tool has
# already run. exit 2 there only shows stderr to the agent.

set -uo pipefail

FILE=$(jq -r '.tool_input.file_path // empty' 2>/dev/null || true)

[ -n "$FILE" ] || exit 0
case "$FILE" in
  *.py) ;;
  *) exit 0 ;;
esac

# The example project's formatter config lives in app/backend (a Python backend).
cd "$CLAUDE_PROJECT_DIR/app/backend" 2>/dev/null || exit 0

# A real, checkable log line every time this actually fires — the hook has
# no other visible trace (always exits 0, no output to the agent), and
# "the file happens to be formatted" is circumstantial, not proof.
mkdir -p "$CLAUDE_PROJECT_DIR/.claude/hooks/.react-log"
echo "$(date '+%Y-%m-%d %H:%M:%S') formatted: $FILE" >> "$CLAUDE_PROJECT_DIR/.claude/hooks/.react-log/format-touched.log"

uv run ruff format "$FILE" >/dev/null 2>&1

exit 0
