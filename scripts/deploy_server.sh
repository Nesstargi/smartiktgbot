#!/usr/bin/env bash
set -euo pipefail

BRANCH="main"
REMOTE="origin"
SKIP_BUILD=0
DRY_RUN=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --branch)
      BRANCH="${2:?missing value for --branch}"
      shift 2
      ;;
    --remote)
      REMOTE="${2:?missing value for --remote}"
      shift 2
      ;;
    --skip-build)
      SKIP_BUILD=1
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

run_cmd() {
  echo "> $*"
  if [[ "$DRY_RUN" -eq 1 ]]; then
    return 0
  fi
  "$@"
}

if [[ ! -d .git ]]; then
  echo "This folder is not a git repository. Clone the project from git first." >&2
  exit 1
fi

if ! command -v git >/dev/null 2>&1; then
  echo "git is not installed or not available in PATH." >&2
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "docker is not installed or not available in PATH." >&2
  exit 1
fi

if [[ ! -f .env ]]; then
  echo "Warning: .env was not found in the repository root. Docker Compose may fail to start." >&2
fi

if [[ -n "$(git status --porcelain --untracked-files=no)" ]]; then
  echo "Tracked local changes detected. Commit, stash, or revert them before deployment." >&2
  exit 1
fi

CURRENT_BRANCH="$(git branch --show-current)"
if [[ -z "$CURRENT_BRANCH" ]]; then
  echo "Could not determine the current git branch." >&2
  exit 1
fi

run_cmd git fetch "$REMOTE" "$BRANCH"

if [[ "$CURRENT_BRANCH" != "$BRANCH" ]]; then
  run_cmd git checkout "$BRANCH"
fi

run_cmd git pull --ff-only "$REMOTE" "$BRANCH"

COMPOSE_ARGS=(compose up -d)
if [[ "$SKIP_BUILD" -ne 1 ]]; then
  COMPOSE_ARGS+=(--build)
fi

run_cmd docker "${COMPOSE_ARGS[@]}"
run_cmd docker compose ps

echo
echo "Deployment finished."
