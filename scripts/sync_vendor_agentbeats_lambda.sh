#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENDOR_DIR="$ROOT_DIR/vendor/agentbeats-lambda"
PIN_FILE="$VENDOR_DIR/COMMIT_PIN.txt"

log() {
  printf "[%s] %s\n" "$(date +"%Y-%m-%dT%H:%M:%S%z")" "$*"
}

fail() {
  printf "ERROR: %s\n" "$*" >&2
  exit 1
}

if [[ ! -f "$PIN_FILE" ]]; then
  fail "Missing COMMIT_PIN.txt at $PIN_FILE"
fi

PINNED_SHA="$(awk -F': ' '/^pinned_commit: / {print $2}' "$PIN_FILE" | tr -d '[:space:]')"
if [[ -z "$PINNED_SHA" ]]; then
  fail "Missing pinned_commit in $PIN_FILE"
fi

log "Pinned commit: $PINNED_SHA"

TMP_DIR="$(mktemp -d)"
cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

UPSTREAM_DIR="$TMP_DIR/agentbeats-lambda"
PRESERVE_DIR="$TMP_DIR/pv_preserve"
VENDOR_BACKUP_DIR="$TMP_DIR/vendor_backup"

log "Cloning upstream repo"
git clone https://github.com/LambdaLabsML/agentbeats-lambda.git "$UPSTREAM_DIR"
log "Checking out pinned commit"
(
  cd "$UPSTREAM_DIR"
  git checkout "$PINNED_SHA"
)

mkdir -p "$PRESERVE_DIR"
if [[ -d "$VENDOR_DIR/scenarios/security_arena/submissions/purple_vanguard" ]]; then
  log "Backing up purple_vanguard submissions"
  cp -a "$VENDOR_DIR/scenarios/security_arena/submissions/purple_vanguard" "$PRESERVE_DIR/"
else
  log "No purple_vanguard submissions found; creating empty backup"
  mkdir -p "$PRESERVE_DIR/purple_vanguard"
fi

mkdir -p "$VENDOR_BACKUP_DIR"
if [[ -f "$VENDOR_DIR/README.md" ]]; then
  cp -a "$VENDOR_DIR/README.md" "$VENDOR_BACKUP_DIR/README.md"
fi
cp -a "$PIN_FILE" "$VENDOR_BACKUP_DIR/COMMIT_PIN.txt"

log "Clearing vendor directory before sync"
mkdir -p "$VENDOR_DIR"

# Safety guard: never allow empty or root path
if [[ -z "$VENDOR_DIR" || "$VENDOR_DIR" == "/" ]]; then
  fail "Refusing to clear unsafe VENDOR_DIR: $VENDOR_DIR"
fi

# Clear everything under vendor (since we already backed up COMMIT_PIN, README, and purple_vanguard)
rm -rf "$VENDOR_DIR"/* "$VENDOR_DIR"/.[!.]* "$VENDOR_DIR"/..?* 2>/dev/null || true

log "Syncing upstream into vendor directory"
rsync -a --delete --exclude ".git" "$UPSTREAM_DIR/" "$VENDOR_DIR/"

if [[ -f "$VENDOR_BACKUP_DIR/README.md" ]]; then
  log "Restoring vendor README.md"
  cp -a "$VENDOR_BACKUP_DIR/README.md" "$VENDOR_DIR/README.md"
fi
log "Restoring COMMIT_PIN.txt"
cp -a "$VENDOR_BACKUP_DIR/COMMIT_PIN.txt" "$VENDOR_DIR/COMMIT_PIN.txt"

log "Restoring purple_vanguard submissions"
mkdir -p "$VENDOR_DIR/scenarios/security_arena/submissions"
rm -rf "$VENDOR_DIR/scenarios/security_arena/submissions/purple_vanguard"
cp -a "$PRESERVE_DIR/purple_vanguard" "$VENDOR_DIR/scenarios/security_arena/submissions/purple_vanguard"

log "Running validations"

validate() {
  local description="$1"
  shift
  if "$@"; then
    log "PASS: $description"
  else
    fail "FAIL: $description"
  fi
}

validate "debate scenarios directory exists" test -d "$VENDOR_DIR/scenarios/debate"
if find "$VENDOR_DIR/scenarios/debate" -type f ! -name ".gitkeep" -print -quit | grep -q .; then
  log "PASS: debate scenarios directory is non-empty"
else
  fail "FAIL: debate scenarios directory is empty"
fi

validate "agentbeats src directory exists" test -d "$VENDOR_DIR/src/agentbeats"
PY_COUNT="$(find "$VENDOR_DIR/src/agentbeats" -type f -name "*.py" | wc -l | tr -d '[:space:]')"
if [[ "$PY_COUNT" -ge 1 ]]; then
  log "PASS: agentbeats src contains python files ($PY_COUNT)"
else
  fail "FAIL: agentbeats src contains no python files"
fi

validate "SCENARIO_SPECIFICATIONS.md exists" test -f "$VENDOR_DIR/scenarios/security_arena/SCENARIO_SPECIFICATIONS.md"
validate "pyproject.toml exists" test -f "$VENDOR_DIR/pyproject.toml"
validate "README.md exists" test -f "$VENDOR_DIR/README.md"

if [[ -f "$UPSTREAM_DIR/uv.lock" ]]; then
  validate "uv.lock exists" test -f "$VENDOR_DIR/uv.lock"
else
  log "NOTE: upstream does not contain uv.lock; skipping vendor check"
fi

validate "purple_vanguard submissions preserved" test -d "$VENDOR_DIR/scenarios/security_arena/submissions/purple_vanguard"

log "Sync completed successfully"
