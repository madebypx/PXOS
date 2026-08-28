#!/usr/bin/env bash
# PXOS Task Helper (POSIX Bash)
# Lightweight git worktree and modular spec manager for PXOS multi-agent development.
#
# Usage:
#   ./scripts/pxos-task.sh new <branch-name> [task-id]
#   ./scripts/pxos-task.sh list
#   ./scripts/pxos-task.sh clean <branch-name>

set -e

BOLD=$(tput bold 2>/dev/null || echo '')
GREEN=$(tput setaf 2 2>/dev/null || echo '')
CYAN=$(tput setaf 6 2>/dev/null || echo '')
YELLOW=$(tput setaf 3 2>/dev/null || echo '')
RED=$(tput setaf 1 2>/dev/null || echo '')
RESET=$(tput sgr0 2>/dev/null || echo '')

log()  { echo "${CYAN}[PXOS-TASK]${RESET} $1"; }
ok()   { echo "${GREEN}[PXOS-TASK]${RESET} $1"; }
warn() { echo "${YELLOW}[PXOS-TASK]${RESET} $1"; }
err()  { echo "${RED}[PXOS-TASK]${RESET} $1" >&2; }

COMMAND="$1"
BRANCH="$2"
TASK_ID="${3:-T-01}"

case "$COMMAND" in
  new)
    if [[ -z "$BRANCH" ]]; then
      err "Missing branch name. Usage: ./scripts/pxos-task.sh new <branch-name> [task-id]"
      exit 1
    fi

    # Sanitize branch for folder name (replace slashes with hyphens for worktree folder)
    DIR_NAME=$(echo "$BRANCH" | tr '/' '-')
    TREES_DIR="../trees"
    TARGET_PATH="${TREES_DIR}/${DIR_NAME}"
    SPEC_SUFFIX=$(echo "$BRANCH" | sed -E 's/^(feat|fix|chore|refactor)\///')
    SPEC_FILE=".ai/specs/SPEC-${SPEC_SUFFIX}.md"

    log "Creating new parallel worktree for branch '${BRANCH}'..."
    mkdir -p "$TREES_DIR"

    # Create git worktree
    if git show-ref --quiet --heads "$BRANCH"; then
      git worktree add "$TARGET_PATH" "$BRANCH"
    else
      git worktree add -b "$BRANCH" "$TARGET_PATH"
    fi

    # Create modular spec if it does not exist
    if [[ ! -f "$SPEC_FILE" ]]; then
      mkdir -p ".ai/specs"
      if [[ -f "templates/.ai/specs/TEMPLATE_SPEC.md" ]]; then
        cp "templates/.ai/specs/TEMPLATE_SPEC.md" "$SPEC_FILE"
      elif [[ -f ".ai/specs/TEMPLATE_SPEC.md" ]]; then
        cp ".ai/specs/TEMPLATE_SPEC.md" "$SPEC_FILE"
      else
        touch "$SPEC_FILE"
      fi

      # Seed task metadata in spec
      sed -i.bak "s/\[Task ID\]/${TASK_ID}/g" "$SPEC_FILE" 2>/dev/null || true
      sed -i.bak "s/\[Task Title\]/${SPEC_SUFFIX}/g" "$SPEC_FILE" 2>/dev/null || true
      sed -i.bak "s/\[e.g. feat\/auth-oauth\]/${BRANCH}/g" "$SPEC_FILE" 2>/dev/null || true
      rm -f "${SPEC_FILE}.bak"
      ok "Created modular spec at ${SPEC_FILE}"
    fi

    ok "Worktree successfully prepared at: ${TARGET_PATH}"
    echo ""
    echo "  ${BOLD}Next steps:${RESET}"
    echo "  1. Open workspace in worktree: ${BOLD}cd ${TARGET_PATH}${RESET}"
    echo "  2. Launch your AI tool/agent in that folder (e.g. cursor ., claude, gemini)."
    echo "  3. Run ${BOLD}/start${RESET} — the agent will auto-resolve '${SPEC_FILE}'."
    echo ""
    ;;

  list)
    log "Active Git Worktrees:"
    git worktree list
    ;;

  clean)
    if [[ -z "$BRANCH" ]]; then
      err "Missing branch name. Usage: ./scripts/pxos-task.sh clean <branch-name>"
      exit 1
    fi

    DIR_NAME=$(echo "$BRANCH" | tr '/' '-')
    TARGET_PATH="../trees/${DIR_NAME}"

    if [[ -d "$TARGET_PATH" ]]; then
      log "Removing worktree at ${TARGET_PATH}..."
      git worktree remove "$TARGET_PATH" --force || true
      ok "Worktree removed."
    else
      warn "Worktree path ${TARGET_PATH} does not exist."
    fi
    ;;

  *)
    echo "${BOLD}PXOS Task Manager${RESET}"
    echo ""
    echo "Usage:"
    echo "  ./scripts/pxos-task.sh new <branch-name> [task-id]   Create a new worktree and modular spec"
    echo "  ./scripts/pxos-task.sh list                         List all active worktrees"
    echo "  ./scripts/pxos-task.sh clean <branch-name>          Remove an active worktree"
    echo ""
    ;;
esac
