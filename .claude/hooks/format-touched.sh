#!/bin/bash
#
# format-touched.sh — the REACT hook. After every Edit/Write, the touched
# TypeScript file comes out lint-fixed. The event guarantees what a rule can
# only ask.
#
# Formatting is a courtesy, never a blocker: this hook always exits 0.
# Even if it wanted to complain, PostToolUse cannot block — the tool has
# already run. exit 2 there only shows stderr to the agent.

set -uo pipefail

INPUT=$(cat)
FILE=$(printf '%s' "$INPUT" | sed -n 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')

[ -n "$FILE" ] || exit 0
case "$FILE" in
  *.ts|*.tsx) ;;
  *) exit 0 ;;
esac

# CHANGE THIS to your project's formatter. Wired for the feature-flag exercise:
# each package (server/, client/) has its own ESLint config, so run it from there.
case "$FILE" in
  */server/*) PKG="$CLAUDE_PROJECT_DIR/server" ;;
  */client/*) PKG="$CLAUDE_PROJECT_DIR/client" ;;
  *) exit 0 ;;
esac
cd "$PKG" 2>/dev/null || exit 0

# A real, checkable log line every time this actually fires — the hook has
# no other visible trace (always exits 0, no output to the agent), and
# "the file happens to be formatted" is circumstantial, not proof.
mkdir -p "$CLAUDE_PROJECT_DIR/.claude/hooks/.react-log"
echo "$(date '+%Y-%m-%d %H:%M:%S') formatted: $FILE" >> "$CLAUDE_PROJECT_DIR/.claude/hooks/.react-log/format-touched.log"

pnpm exec eslint --fix "$FILE" >/dev/null 2>&1

exit 0
