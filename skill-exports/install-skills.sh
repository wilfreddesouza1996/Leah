#!/bin/bash
# Install LiveNote and PaperFetcher skills into Claude Code
# Usage: ./install-skills.sh [target_dir]
#
# Examples:
#   ./install-skills.sh                    # installs to ~/.claude/skills/
#   ./install-skills.sh /path/to/repo/.claude/skills  # installs to a project

set -euo pipefail

TARGET="${1:-$HOME/.claude/skills}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Installing skills to: $TARGET"

# LiveNote
mkdir -p "$TARGET/livenote"
cp "$SCRIPT_DIR/livenote/SKILL.md" "$TARGET/livenote/SKILL.md"
echo "  ✓ LiveNote installed"

# PaperFetcher
mkdir -p "$TARGET/paper-fetcher"
cp "$SCRIPT_DIR/paper-fetcher/SKILL.md" "$TARGET/paper-fetcher/SKILL.md"
echo "  ✓ PaperFetcher installed"

echo ""
echo "Done! Skills installed to $TARGET"
echo ""
echo "To use them:"
echo "  /LiveNote      - Transform lecture notes into academic documents"
echo "  /PaperFetcher  - Extract and fetch paper references"
