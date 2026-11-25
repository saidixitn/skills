#!/usr/bin/env bash
# ==============================================================================
# Installer for Sai Dixit's Agent Skills (@saidixitn/skills)
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/saidixitn/skills/main/install.sh | bash -s <skill-name>
#   curl -fsSL https://raw.githubusercontent.com/saidixitn/skills/main/install.sh | bash -s --all
# ==============================================================================

set -e

REPO_RAW="https://raw.githubusercontent.com/saidixitn/skills/main"
TARGET_DIR="${AGENT_SKILLS_DIR:-$HOME/.gemini/config/skills}"

mkdir -p "$TARGET_DIR"

install_skill() {
  local skill="$1"
  local dest="$TARGET_DIR/$skill"
  echo "Installing skill: $skill into $dest..."
  mkdir -p "$dest"
  curl -fsSL "$REPO_RAW/skills/$skill/SKILL.md" -o "$dest/SKILL.md"
  echo " Skill '$skill' installed successfully!"
}

if [ "$1" = "--all" ] || [ -z "$1" ]; then
  echo " Installing all skills to $TARGET_DIR..."
  SKILLS=(
    "google-sheets"
    "mongodb"
    "animations"
    "website-builder"
    "minimal-design"
    "server-handling"
    "automated-backups"
    "cloudflare-proxy"
    "api-builder"
    "web-scraper"
    "domain-monitor"
    "email-reports"
    "analytics-tracker"
    "bigquery"
    "data-pipelines"
    "seo-automation"
    "mobile-apps"
    "api-testing"
    "macos-apps"
    "agent-rules"
  )
  for s in "${SKILLS[@]}"; do
    install_skill "$s"
  done
  echo " All skills successfully installed!"
else
  install_skill "$1"
fi
