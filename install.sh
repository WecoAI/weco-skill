#!/usr/bin/env bash
set -e

# Weco Skill Installer
# Installs the Weco optimization skill for Claude Code and/or Cursor

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_FILE="$SCRIPT_DIR/SKILL.md"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}Weco Skill Installer${NC}"
echo ""

if [[ ! -f "$SKILL_FILE" ]]; then
    echo -e "${RED}Error: SKILL.md not found in $SCRIPT_DIR${NC}"
    exit 1
fi

# Ask which agent(s) to install for
echo "Which AI coding assistant do you use?"
echo "  1) Claude Code"
echo "  2) Cursor"
echo "  3) Both"
echo ""
read -p "Enter choice [1-3]: " choice

install_claude() {
    local dest_dir="$HOME/.claude/skills/weco"

    echo -e "${BLUE}Installing for Claude Code...${NC}"

    # Create skills directory
    mkdir -p "$dest_dir"

    # Copy skill files
    cp "$SKILL_FILE" "$dest_dir/SKILL.md"
    echo -e "  ${GREEN}✓${NC} Installed SKILL.md"

    # Copy CLAUDE.md (trigger snippet for Claude Code)
    cp "$SCRIPT_DIR/snippets/claude.md" "$dest_dir/CLAUDE.md"
    echo -e "  ${GREEN}✓${NC} Installed CLAUDE.md"

    # Copy references directory if it exists
    if [[ -d "$SCRIPT_DIR/references" ]]; then
        cp -r "$SCRIPT_DIR/references" "$dest_dir/"
        echo -e "  ${GREEN}✓${NC} Installed references/"
    fi

    # Copy assets directory if it exists
    if [[ -d "$SCRIPT_DIR/assets" ]]; then
        cp -r "$SCRIPT_DIR/assets" "$dest_dir/"
        echo -e "  ${GREEN}✓${NC} Installed assets/"
    fi

    echo -e "  ${GREEN}✓${NC} Installed to $dest_dir"
    echo -e "${GREEN}Claude Code installation complete!${NC}"
}

install_cursor() {
    local skills_dir="$HOME/.cursor/skills/weco"
    local cursor_rules_dir="$HOME/.cursor/rules"
    local trigger_file="$cursor_rules_dir/weco.mdc"

    echo -e "${BLUE}Installing for Cursor...${NC}"

    # Create directories
    mkdir -p "$skills_dir"
    mkdir -p "$cursor_rules_dir"

    # Copy trigger file to Cursor rules directory (as .mdc)
    cp "$SCRIPT_DIR/snippets/cursor.md" "$trigger_file"
    echo -e "  ${GREEN}✓${NC} Installed trigger to $trigger_file"

    # Copy skill files to skills directory
    cp "$SKILL_FILE" "$skills_dir/SKILL.md"
    echo -e "  ${GREEN}✓${NC} Installed SKILL.md"

    # Copy references directory if it exists
    if [[ -d "$SCRIPT_DIR/references" ]]; then
        cp -r "$SCRIPT_DIR/references" "$skills_dir/"
        echo -e "  ${GREEN}✓${NC} Installed references/"
    fi

    # Copy assets directory if it exists
    if [[ -d "$SCRIPT_DIR/assets" ]]; then
        cp -r "$SCRIPT_DIR/assets" "$skills_dir/"
        echo -e "  ${GREEN}✓${NC} Installed assets/"
    fi

    echo -e "  ${GREEN}✓${NC} Skill files installed to $skills_dir"
    echo -e "${GREEN}Cursor installation complete!${NC}"
}

case $choice in
    1)
        install_claude
        ;;
    2)
        install_cursor
        ;;
    3)
        install_claude
        echo ""
        install_cursor
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}Installation complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Open a project with code you want to optimize"
echo "  2. Ask your AI assistant to 'make this faster' or 'optimize this function'"
echo "  3. The Weco skill will guide the optimization process"
echo ""
echo "For more info, see: https://weco.ai/docs"
