# Purple Vanguard Scenario Manifest — Schema v1

This document defines the **Purple Vanguard Scenario Manifest — Schema v1**. Each scenario must include a manifest file at:

`scenarios/<scenario_id>/artifacts/manifest.yaml`

## Required fields

- **schema_version**: string, must be `v1`.
- **scenario_id**: string, must match the scenario folder name and verifier CLI argument.
- **title**: string, human-readable scenario title.
- **attack_type**: string, short category label.
- **description**: string, concise summary of the scenario.
- **capabilities**: list of strings describing available artifact capabilities.
- **required_artifacts**: mapping of capability -> list of artifact paths (relative to `artifacts/`).

## Optional fields

- **extract**: list of extraction rules (see below).
- **contacts**: list of strings or structured contact objects.
- **tags**: list of strings.

## Extract rules (optional)

Each entry in `extract` is an object with:

- **id** (required): stable identifier for the extracted value.
- **kind** (required): one of `yaml_path`, `yaml_keys`, `glob_list`, `text_regex`.
- **source** (required): path (or glob pattern) relative to `artifacts/`.
- **path** (optional): dotted path for YAML traversal (required for `yaml_path` and `yaml_keys`).
- **select** (optional): for `yaml_path`, project a field from each item when the extracted
  value is a list of dictionaries (e.g., `select: version`).
- **pattern** (optional): regex pattern (required for `text_regex`).
- **group** (optional): regex capture group (default `1`).
- **required** (optional): boolean, defaults to `true`.

### Extract kinds

- **yaml_path**: parse YAML at `source` and extract a value using `path` (e.g., `entries.mychart.0.version`).
  If `select` is provided and the extracted value is a list of dictionaries, return
  a list of each item's selected field.
- **yaml_keys**: parse YAML at `source` and list keys under `path`.
- **glob_list**: list files matching the `source` glob pattern.
- **text_regex**: apply regex `pattern` to the text file at `source` and extract `group`.

## Verifier contract

The Phase-3 Step-1 verifier must:

1. Validate required fields and invariants:
   - `schema_version` equals `v1`.
   - `manifest.scenario_id` matches the scenario directory and CLI argument.
   - `capabilities` is a list of strings.
   - `required_artifacts` keys are a subset of `capabilities`.
2. Validate required artifacts:
   - All paths are relative to `artifacts/`.
   - Files exist and are readable.
   - Directories exist and contain at least one file.
3. Run deep checks for declared capabilities (no external commands, no network).
4. Execute extract rules:
   - Unknown extract kinds must **fail** with a clear error.
   - Unknown capabilities must **warn** and continue.
   - If a required extraction fails, verification **fails**.
5. Emit `artifacts_map.json` with authoritative identifiers for later phases.

## Example manifest (BadBlueprint)

```yaml
schema_version: v1
scenario_id: badblueprint
title: BadBlueprint
attack_type: financial_supply_chain_attack
description: Supply-chain scenario focused on tampered Helm artifacts and prompts.
capabilities:
  - prompts
  - helm_repo
  - helm_chart
required_artifacts:
  prompts:
    - prompts/
  helm_repo:
    - helm_repo/index.yaml
  helm_chart:
    - chart/Chart.yaml
    - chart/values.yaml
    - chart/templates/
extract:
  - id: helm_chart.name
    kind: yaml_path
    source: chart/Chart.yaml
    path: name
  - id: helm_chart.version
    kind: yaml_path
    source: chart/Chart.yaml
    path: version
  - id: helm_repo.entries
    kind: yaml_keys
    source: helm_repo/index.yaml
    path: entries
  - id: helm_repo.versions
    kind: yaml_path
    source: helm_repo/index.yaml
    path: entries.cluster-observability-stack
    select: version
  - id: prompts.files
    kind: glob_list
    source: prompts/*.md
```
