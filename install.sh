#!/usr/bin/env bash
# PXOS Installer
# Usage: curl -sSL https://raw.githubusercontent.com/rodrigospena/PXOS/main/install.sh | bash
# Or with flags:
#   bash install.sh --full        (includes ROADMAP.md and SPRINT.md)
#   bash install.sh --ide cursor  (also generates Cursor rules)
#   bash install.sh --ide windsurf
#
# Flags can be combined:
#   curl -sSL .../install.sh | bash -s -- --full --ide cursor

set -e

PXOS_REPO="https://raw.githubusercontent.com/rodrigospena/PXOS/main"
TARGET_DIR=".ai"
FULL=false
IDE=""

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
    --full) FULL=true; shift ;;
    --ide)  IDE="$2"; shift 2 ;;
    *)      warn "Unknown flag: $1"; shift ;;
  esac
done

# ─── Check deps ───────────────────────────────────────────────────────────────
if ! command -v curl &>/dev/null; then
  echo "Error: curl is required but not installed." >&2
  exit 1
fi

# ─── Download function ────────────────────────────────────────────────────────
download_file() {
  local src="$1"
  local dest="$2"

  if [[ -f "$dest" ]]; then
    warn "Skipping $(basename "$dest") — already exists. Delete it first to reinstall."
    return
  fi

  mkdir -p "$(dirname "$dest")"
  curl -sSL "${PXOS_REPO}/${src}" -o "$dest"
  ok "Created $dest"
}

# ─── Core .ai/ files ──────────────────────────────────────────────────────────
echo ""
echo "${BOLD}Installing PXOS...${RESET}"
echo ""

log "Setting up ${TARGET_DIR}/"
download_file "templates/.ai/AI_BASE.md"         "${TARGET_DIR}/AI_BASE.md"
download_file "templates/.ai/PROJECT_CONTEXT.md" "${TARGET_DIR}/PROJECT_CONTEXT.md"
download_file "templates/.ai/CURRENT_SPEC.md"    "${TARGET_DIR}/CURRENT_SPEC.md"
download_file "templates/.ai/DECISION_LOG.md"    "${TARGET_DIR}/DECISION_LOG.md"

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
  fi
fi

# ─── IDE rules ───────────────────────────────────────────────────────────────────
if [[ -n "$IDE" ]]; then
  AI_BASE_CONTENT=$(cat "${TARGET_DIR}/AI_BASE.md" 2>/dev/null || curl -sSL "${PXOS_REPO}/templates/.ai/AI_BASE.md")

  case "$IDE" in
    cursor)
      RULES_DIR=".cursor/rules"
      RULES_FILE="${RULES_DIR}/pxos.mdc"
      log "Generating Cursor rules at ${RULES_FILE}..."
      mkdir -p "$RULES_DIR"
      if [[ -f "$RULES_FILE" ]]; then
        warn "Skipping ${RULES_FILE} — already exists."
      else
        printf '%s\n' "---" "alwaysApply: true" "---" "" "$AI_BASE_CONTENT" > "$RULES_FILE"
        ok "Created ${RULES_FILE}"
      fi
      ;;
    windsurf)
      RULES_DIR=".windsurf/rules"
      RULES_FILE="${RULES_DIR}/pxos.md"
      log "Generating Windsurf rules at ${RULES_FILE}..."
      mkdir -p "$RULES_DIR"
      if [[ -f "$RULES_FILE" ]]; then
        warn "Skipping ${RULES_FILE} — already exists."
      else
        printf '%s\n' "$AI_BASE_CONTENT" > "$RULES_FILE"
        ok "Created ${RULES_FILE}"
      fi
      ;;
    *)
      warn "Unknown IDE: ${IDE}. Supported: cursor, windsurf"
      ;;
  esac
fi

# ─── Done ─────────────────────────────────────────────────────────────────────
echo ""
echo "${BOLD}${GREEN}PXOS installed.${RESET}"
echo ""
echo "  Next steps:"
echo "  1. Fill in ${BOLD}.ai/PROJECT_CONTEXT.md${RESET} with your project facts."
echo "  2. Before each session, update ${BOLD}.ai/CURRENT_SPEC.md${RESET} with the current task."
echo "  3. Start your AI session with the opener in the README."
echo ""
echo "  Docs: https://github.com/rodrigospena/PXOS"
echo ""
