#!/usr/bin/env bash
# PXOS Installer
#
# Basic usage:
#   curl -sSL https://raw.githubusercontent.com/rodrigospena/PXOS/main/install.sh | bash
#
# With flags:
#   bash -s -- --full                  (also installs ROADMAP.md and SPRINT.md)
#   bash -s -- --ide cursor            (also installs workspace IDE rules)
#   bash -s -- --ide claude            (also installs CLAUDE.md in project root)
#   bash -s -- --ide gemini            (also installs GEMINI.md in project root)
#   bash -s -- --ide copilot           (also installs .github/copilot-instructions.md)
#   bash -s -- --ide windsurf          (also installs .windsurf/rules/pxos.md)
#   bash -s -- --global --ide cursor   (installs IDE rules globally, not per-project)
#
# Flags can be combined:
#   curl -sSL .../install.sh | bash -s -- --full --ide cursor

set -e

PXOS_REPO="https://raw.githubusercontent.com/rodrigospena/PXOS/main"
TARGET_DIR=".ai"
FULL=false
IDE=""
GLOBAL=false

# ─── Colors ───────────────────────────────────────────────────────────────────
BOLD=$(tput bold 2>/dev/null || echo '')
GREEN=$(tput setaf 2 2>/dev/null || echo '')
CYAN=$(tput setaf 6 2>/dev/null || echo '')
YELLOW=$(tput setaf 3 2>/dev/null || echo '')
RESET=$(tput sgr0 2>/dev/null || echo '')

log()  { echo "${CYAN}[PXOS]${RESET} $1"; }
ok()   { echo "${GREEN}[PXOS]${RESET} $1"; }
warn() { echo "${YELLOW}[PXOS]${RESET} $1"; }

# ─── Parse flags ──────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --full)   FULL=true; shift ;;
    --global) GLOBAL=true; shift ;;
    --ide)    IDE="$2"; shift 2 ;;
    *)        warn "Unknown flag: $1"; shift ;;
  esac
done

# ─── Check deps ───────────────────────────────────────────────────────────────
if ! command -v curl &>/dev/null; then
  echo "Error: curl is required but not installed." >&2
  exit 1
fi

# ─── Download function (skip if exists) ────────────────────────────────────────
download_file() {
  local src="$1"
  local dest="$2"

  if [[ -f "$dest" ]]; then
    warn "Skipping $(basename "$dest") — already exists."
    return
  fi

  mkdir -p "$(dirname "$dest")"
  curl -sSL "${PXOS_REPO}/${src}" -o "$dest"
  ok "Created $dest"
}

# ─── Merge/append function (appends PXOS block if not already present) ────────────
append_pxos_block() {
  local dest="$1"
  local content="$2"
  local MARKER="<!-- pxos:start -->"

  if [[ -f "$dest" ]]; then
    if grep -qF "$MARKER" "$dest"; then
      warn "PXOS block already present in $dest — skipping."
      return
    fi
    # Append to existing file
    printf '\n\n---\n\n%s\n%s\n' "$MARKER" "$content" >> "$dest"
    ok "Appended PXOS rules to $dest"
  else
    # Create new file
    mkdir -p "$(dirname "$dest")"
    printf '%s\n%s\n' "$MARKER" "$content" > "$dest"
    ok "Created $dest"
  fi
}

# ─── Core .ai/ files ──────────────────────────────────────────────────────────
echo ""
echo "${BOLD}Installing PXOS...${RESET}"
echo ""

if [[ "$GLOBAL" == false ]]; then
  log "Setting up ${TARGET_DIR}/ (workspace)"
  download_file "templates/.ai/AI_BASE.md"         "${TARGET_DIR}/AI_BASE.md"
  download_file "templates/.ai/PROJECT_CONTEXT.md" "${TARGET_DIR}/PROJECT_CONTEXT.md"
  download_file "templates/.ai/CURRENT_SPEC.md"    "${TARGET_DIR}/CURRENT_SPEC.md"
  download_file "templates/.ai/DECISION_LOG.md"    "${TARGET_DIR}/DECISION_LOG.md"
fi

# ─── Optional planning files ──────────────────────────────────────────────────
if [[ "$FULL" == true ]]; then
  log "Installing optional planning files..."
  download_file "templates/ROADMAP.md" "ROADMAP.md"
  download_file "templates/SPRINT.md"  "SPRINT.md"
fi

# ─── Auto-detect IDE (if --ide not passed) ───────────────────────────────────
if [[ -z "$IDE" ]]; then
  if [[ -d ".cursor" ]]; then
    warn "Detected Cursor project. Run with --ide cursor to also install rules."
  elif [[ -d ".windsurf" ]]; then
    warn "Detected Windsurf project. Run with --ide windsurf to also install rules."
  elif [[ -f "CLAUDE.md" ]]; then
    warn "Detected Claude Code project. Run with --ide claude to also install rules."
  elif [[ -f "GEMINI.md" ]]; then
    warn "Detected Gemini CLI project. Run with --ide gemini to also install rules."
  elif [[ -f ".github/copilot-instructions.md" ]]; then
    warn "Detected GitHub Copilot project. Run with --ide copilot to also install rules."
  fi
fi

# ─── IDE rules ───────────────────────────────────────────────────────────────────
if [[ -n "$IDE" ]]; then
  AI_BASE_CONTENT=$(cat "${TARGET_DIR}/AI_BASE.md" 2>/dev/null || curl -sSL "${PXOS_REPO}/templates/.ai/AI_BASE.md")

  case "$IDE" in
    cursor)
      if [[ "$GLOBAL" == true ]]; then
        RULES_FILE="${HOME}/.cursor/rules/pxos.mdc"
        log "Installing Cursor rules globally at ${RULES_FILE}..."
      else
        RULES_FILE=".cursor/rules/pxos.mdc"
        log "Installing Cursor rules (workspace) at ${RULES_FILE}..."
      fi
      mkdir -p "$(dirname "$RULES_FILE")"
      if [[ -f "$RULES_FILE" ]]; then
        warn "Skipping ${RULES_FILE} — already exists."
      else
        printf '%s\n' "---" "alwaysApply: true" "---" "" "$AI_BASE_CONTENT" > "$RULES_FILE"
        ok "Created ${RULES_FILE}"
      fi
      ;;
    windsurf)
      if [[ "$GLOBAL" == true ]]; then
        RULES_FILE="${HOME}/.windsurf/rules/pxos.md"
        log "Installing Windsurf rules globally at ${RULES_FILE}..."
      else
        RULES_FILE=".windsurf/rules/pxos.md"
        log "Installing Windsurf rules (workspace) at ${RULES_FILE}..."
      fi
      mkdir -p "$(dirname "$RULES_FILE")"
      if [[ -f "$RULES_FILE" ]]; then
        warn "Skipping ${RULES_FILE} — already exists."
      else
        printf '%s\n' "$AI_BASE_CONTENT" > "$RULES_FILE"
        ok "Created ${RULES_FILE}"
      fi
      ;;
    claude)
      if [[ "$GLOBAL" == true ]]; then
        RULES_FILE="${HOME}/.claude/CLAUDE.md"
        log "Installing Claude Code rules globally at ${RULES_FILE}..."
      else
        RULES_FILE="CLAUDE.md"
        log "Installing Claude Code rules (workspace) at ${RULES_FILE}..."
      fi
      append_pxos_block "$RULES_FILE" "$AI_BASE_CONTENT"
      ;;
    gemini)
      if [[ "$GLOBAL" == true ]]; then
        RULES_FILE="${HOME}/.gemini/GEMINI.md"
        log "Installing Gemini CLI rules globally at ${RULES_FILE}..."
      else
        RULES_FILE="GEMINI.md"
        log "Installing Gemini CLI rules (workspace) at ${RULES_FILE}..."
      fi
      append_pxos_block "$RULES_FILE" "$AI_BASE_CONTENT"
      ;;
    copilot)
      if [[ "$GLOBAL" == true ]]; then
        warn "GitHub Copilot does not support global instructions via file. Use workspace only."
      else
        RULES_FILE=".github/copilot-instructions.md"
        log "Installing GitHub Copilot rules (workspace) at ${RULES_FILE}..."
        append_pxos_block "$RULES_FILE" "$AI_BASE_CONTENT"
      fi
      ;;
    *)
      warn "Unknown IDE: ${IDE}. Supported: cursor, windsurf, claude, gemini, copilot"
      ;;
  esac
fi

# ─── Done ─────────────────────────────────────────────────────────────────────
echo ""
echo "${BOLD}${GREEN}PXOS installed.${RESET}"
echo ""
if [[ "$GLOBAL" == false ]]; then
  echo "  Next steps:"
  echo "  1. Fill in ${BOLD}.ai/PROJECT_CONTEXT.md${RESET} with your project facts."
  echo "  2. Before each session, update ${BOLD}.ai/CURRENT_SPEC.md${RESET} with the current task."
  echo "  3. Start your AI session with the opener in the README."
else
  echo "  IDE rules installed globally. PXOS will apply to all projects in this IDE."
  echo "  To also set up a specific project, run the installer again without --global."
fi
echo ""
echo "  Docs: https://github.com/rodrigospena/PXOS"
echo ""
