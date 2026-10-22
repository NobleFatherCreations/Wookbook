#!/bin/bash
set -euo pipefail

# SessionStart hook for Wookbook project
# Ensures critical context files are available in every new session

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"

echo "📖 Checking project context files..."

[ -f "$PROJECT_DIR/CLAUDE.md" ] && echo "✓ CLAUDE.md (project instructions)" || echo "⚠ CLAUDE.md not found"
[ -f "$PROJECT_DIR/MEMORY.md" ] && echo "✓ MEMORY.md (cross-session memory)" || echo "⚠ MEMORY.md not found"
[ -f "$PROJECT_DIR/BOOKS.md" ] && echo "✓ BOOKS.md (book reference)" || echo "⚠ BOOKS.md not found"

echo "🔎 find-skills is installed (.claude/skills/find-skills). STANDING RULE: at the start of every coding thread, invoke the find-skills skill via the Skill tool, and use it whenever a task might be served by an installable skill (npx skills find <query>)."

echo "export CLAUDE_PROJECT_DIR=\"$PROJECT_DIR\"" >> "${CLAUDE_ENV_FILE:-.env}"
echo "✓ Session initialized"
