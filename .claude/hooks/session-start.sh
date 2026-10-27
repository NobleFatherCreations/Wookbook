#!/bin/bash
set -euo pipefail

# SessionStart hook for Wookbook project
# Ensures critical context files are available in every new session

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"

echo "📖 Checking project context files..."

[ -f "$PROJECT_DIR/CLAUDE.md" ] && echo "✓ CLAUDE.md (project instructions)" || echo "⚠ CLAUDE.md not found"
[ -f "$PROJECT_DIR/MEMORY.md" ] && echo "✓ MEMORY.md (cross-session memory)" || echo "⚠ MEMORY.md not found"
[ -f "$PROJECT_DIR/BOOKS.md" ] && echo "✓ BOOKS.md (book reference)" || echo "⚠ BOOKS.md not found"

echo "export CLAUDE_PROJECT_DIR=\"$PROJECT_DIR\"" >> "${CLAUDE_ENV_FILE:-.env}"
# Sequential Thinking MCP at user scope, so it is there whatever folder a chat opens in. A server added here
# takes effect when the session next starts or resumes; the environment setup script does the same before the
# first start. Idempotent and never fails the hook.
# (`claude mcp get` would also match the repo's own .mcp.json entry, so just add at user scope; "already exists" is fine.)
if command -v claude >/dev/null 2>&1; then
  claude mcp add --scope user sequential-thinking -- npx -y @modelcontextprotocol/server-sequential-thinking@2.0.0 >/dev/null 2>&1 \
    && echo "✓ Sequential Thinking MCP registered (user scope)" || echo "✓ Sequential Thinking MCP already registered"
fi

echo "✓ Session initialized"
