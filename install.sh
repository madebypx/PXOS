#!/usr/bin/env bash
# PXOS Installer & Updater
#
# Basic installation:
#   curl -sSL https://raw.githubusercontent.com/madebypx/PXOS/main/install.sh | bash
#
# Upgrade an existing project to latest PXOS version:
#   curl -sSL https://raw.githubusercontent.com/madebypx/PXOS/main/install.sh | bash -s -- --update
#
# With flags:
#   bash -s -- --update                (safely updates AI_BASE.md, specs template, and IDE rules)
#   bash -s -- --version               (prints current PXOS version)
#   bash -s -- --full                  (also installs ROADMAP.md and SPRINT.md)
#   bash -s -- --ide cursor            (also installs workspace IDE rules)
#   bash -s -- --ide claude            (also installs CLAUDE.md in project root)
#   bash -s -- --ide gemini            (also installs GEMINI.md in project root)
#   bash -s -- --ide copilot           (also installs .github/copilot-instructions.md)
#   bash -s -- --ide windsurf          (also installs .windsurf/rules/pxos.md)
#   bash -s -- --global --ide cursor   (installs IDE rules globally, not per-project)

set -e

PXOS_VERSION="2.4.0"
PXOS_REPO="https://raw.githubusercontent.com/madebypx/PXOS/main"
TARGET_DIR=".ai"
FULL=false
IDE=""
GLOBAL=false
UPDATE=false

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
    --version|-v)
      echo "PXOS v${PXOS_VERSION}"
      exit 0
      ;;
    --update|--upgrade|-u)
      UPDATE=true
      shift
      ;;
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

# ─── Download function (skip if exists unless updating) ────────────────────────
download_file() {
  local src="$1"
  local dest="$2"
  local overwrite="${3:-false}"

  if [[ -f "$dest" && "$overwrite" == false ]]; then
    warn "Skipping $(basename "$dest") — already exists."
    return
  fi

  mkdir -p "$(dirname "$dest")"
  if [[ -f "$src" ]]; then
    cp "$src" "$dest"
  else
    curl -sSL "${PXOS_REPO}/${src}" -o "$dest"
  fi

  if [[ "$overwrite" == true && -f "$dest" ]]; then
    ok "Updated $dest"
  else
    ok "Created $dest"
  fi
}

# ─── Merge/append function (appends or replaces PXOS block) ─────────────────────
append_pxos_block() {
  local dest="$1"
  local content="$2"
  local START_MARKER="<!-- pxos:start -->"
  local END_MARKER="<!-- pxos:end -->"

  mkdir -p "$(dirname "$dest")"

  if [[ -f "$dest" ]]; then
    if grep -qF "$START_MARKER" "$dest"; then
      # Replace existing PXOS block
      awk -v start="$START_MARKER" -v end="$END_MARKER" -v repl="$content" '
        $0 ~ start { printing=0; print start "\n" repl "\n" end; next }
        $0 ~ end   { printing=1; next }
        !printing && !found_start { if ($0 ~ start) { found_start=1 } }
        printing { print }
      ' "$dest" > "${dest}.tmp" 2>/dev/null || true

      if [[ -s "${dest}.tmp" ]]; then
        mv "${dest}.tmp" "$dest"
        ok "Updated PXOS rules block in $dest"
        return
      else
        rm -f "${dest}.tmp"
      fi
    fi

    printf '\n\n---\n\n%s\n%s\n%s\n' "$START_MARKER" "$content" "$END_MARKER" >> "$dest"
    ok "Appended PXOS rules to $dest"
  else
    printf '%s\n%s\n%s\n' "$START_MARKER" "$content" "$END_MARKER" > "$dest"
    ok "Created $dest"
  fi
}

# ─── Main Execution ───────────────────────────────────────────────────────────
echo ""
if [[ "$UPDATE" == true ]]; then
  echo "${BOLD}Upgrading PXOS to v${PXOS_VERSION}...${RESET}"
else
  echo "${BOLD}Installing PXOS v${PXOS_VERSION}...${RESET}"
fi
echo ""

if [[ "$GLOBAL" == false ]]; then
  log "Configuring ${TARGET_DIR}/"
  
  if [[ "$UPDATE" == true ]]; then
    # In update mode, safely update universal rules and modular spec templates
    download_file "templates/.ai/AI_BASE.md"               "${TARGET_DIR}/AI_BASE.md" true
    download_file "templates/.ai/specs/TEMPLATE_SPEC.md"   "${TARGET_DIR}/specs/TEMPLATE_SPEC.md" true
    # Scaffolding research and audits directories and guide/index without overwriting existing
    mkdir -p "${TARGET_DIR}/research" "${TARGET_DIR}/audits"
    download_file "templates/.ai/research/INDEX.md"         "${TARGET_DIR}/research/INDEX.md" false
    download_file "templates/.ai/audits/README.md"          "${TARGET_DIR}/audits/README.md" false
    log "Preserved PROJECT_CONTEXT.md, DECISION_LOG.md, and all active specs."
  else
    download_file "templates/.ai/AI_BASE.md"               "${TARGET_DIR}/AI_BASE.md"
    download_file "templates/.ai/PROJECT_CONTEXT.md"       "${TARGET_DIR}/PROJECT_CONTEXT.md"
    download_file "templates/.ai/CURRENT_SPEC.md"          "${TARGET_DIR}/CURRENT_SPEC.md"
    download_file "templates/.ai/DECISION_LOG.md"          "${TARGET_DIR}/DECISION_LOG.md"
    download_file "templates/.ai/specs/TEMPLATE_SPEC.md"   "${TARGET_DIR}/specs/TEMPLATE_SPEC.md"
    download_file "templates/.ai/research/INDEX.md"         "${TARGET_DIR}/research/INDEX.md"
    download_file "templates/.ai/audits/README.md"          "${TARGET_DIR}/audits/README.md"
  fi
fi

# ─── Optional planning files ──────────────────────────────────────────────────
if [[ "$FULL" == true ]]; then
  log "Installing optional planning files..."
  download_file "templates/ROADMAP.md" "ROADMAP.md"
  download_file "templates/SPRINT.md"  "SPRINT.md"
fi

# ─── Auto-detect IDE ──────────────────────────────────────────────────────────
if [[ -z "$IDE" ]]; then
  if [[ -d ".cursor" ]]; then
    IDE="cursor"
  elif [[ -d ".windsurf" ]]; then
    IDE="windsurf"
  elif [[ -f "CLAUDE.md" ]]; then
    IDE="claude"
  elif [[ -f "GEMINI.md" ]]; then
    IDE="gemini"
  elif [[ -f ".github/copilot-instructions.md" ]]; then
    IDE="copilot"
  fi
fi

# ─── IDE rules ─────────────────────────────────────────────────────────────────
if [[ -n "$IDE" ]]; then
  IDE_RULES_CONTENT=$(cat "templates/rules/pxos.md" 2>/dev/null || curl -sSL "${PXOS_REPO}/templates/rules/pxos.md" 2>/dev/null || cat "${TARGET_DIR}/AI_BASE.md" 2>/dev/null)

  case "$IDE" in
    cursor)
      RULES_FILE=".cursor/rules/pxos.mdc"
      [[ "$GLOBAL" == true ]] && RULES_FILE="${HOME}/.cursor/rules/pxos.mdc"
      mkdir -p "$(dirname "$RULES_FILE")"
      printf '%s\n' "---" "alwaysApply: true" "---" "" "$IDE_RULES_CONTENT" > "$RULES_FILE"
      ok "Configured Cursor rules at ${RULES_FILE}"
      ;;
    windsurf)
      RULES_FILE=".windsurf/rules/pxos.md"
      [[ "$GLOBAL" == true ]] && RULES_FILE="${HOME}/.windsurf/rules/pxos.md"
      mkdir -p "$(dirname "$RULES_FILE")"
      printf '%s\n' "$IDE_RULES_CONTENT" > "$RULES_FILE"
      ok "Configured Windsurf rules at ${RULES_FILE}"
      ;;
    claude)
      RULES_FILE="CLAUDE.md"
      [[ "$GLOBAL" == true ]] && RULES_FILE="${HOME}/.claude/CLAUDE.md"
      append_pxos_block "$RULES_FILE" "$IDE_RULES_CONTENT"
      ;;
    gemini)
      RULES_FILE="GEMINI.md"
      [[ "$GLOBAL" == true ]] && RULES_FILE="${HOME}/.gemini/GEMINI.md"
      append_pxos_block "$RULES_FILE" "$IDE_RULES_CONTENT"
      ;;
    copilot)
      RULES_FILE=".github/copilot-instructions.md"
      append_pxos_block "$RULES_FILE" "$IDE_RULES_CONTENT"
      ;;
  esac
fi

# ─── Done ─────────────────────────────────────────────────────────────────────
echo ""
if [[ "$UPDATE" == true ]]; then
  echo "${BOLD}${GREEN}PXOS upgraded to v${PXOS_VERSION}.${RESET}"
else
  echo "${BOLD}${GREEN}PXOS v${PXOS_VERSION} installed.${RESET}"
fi
echo ""

if [[ "$GLOBAL" == false ]]; then
  echo "  Next steps:"
  echo "  1. Check ${BOLD}.ai/AI_BASE.md${RESET} for updated operating rules."
  echo "  2. Run ${BOLD}/start${RESET} in any branch or worktree to auto-resolve specs."
  echo "  3. Use ${BOLD}/audit${RESET} for codebase health and ${BOLD}/decision${RESET} for ADRs."
else
  echo "  Global IDE rules configured for v${PXOS_VERSION}."
fi
echo ""
echo "  Docs: https://github.com/madebypx/PXOS"
echo ""
