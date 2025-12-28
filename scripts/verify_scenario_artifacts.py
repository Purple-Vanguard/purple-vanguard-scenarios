#!/usr/bin/env python3
import argparse
import datetime
import glob
import json
import os
import re
import sys
from typing import Any, Dict, List, Tuple

try:
    import yaml
except ModuleNotFoundError:
    print(
        "[FAIL] Missing dependency: PyYAML. Install with: pip install -r requirements.txt"
    )
    sys.exit(2)


def load_yaml(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def is_relative_path(path: str) -> bool:
    if os.path.isabs(path):
        return False
    normalized = os.path.normpath(path)
    return not normalized.startswith("..")


def directory_has_files(path: str) -> bool:
    for _, _, files in os.walk(path):
        if files:
            return True
    return False


def get_by_dotted_path(data: Any, dotted_path: str) -> Any:
    current = data
    for part in dotted_path.split("."):
        if isinstance(current, list):
            if not part.isdigit():
                raise KeyError(f"Expected list index for '{part}'")
            index = int(part)
            if index >= len(current):
                raise KeyError(f"Index {index} out of range")
            current = current[index]
        elif isinstance(current, dict):
            if part not in current:
                raise KeyError(f"Key '{part}' not found")
            current = current[part]
        else:
            raise KeyError(f"Cannot traverse into '{part}'")
    return current


def extract_yaml_path(source_path: str, path: str) -> Any:
    data = load_yaml(source_path)
    return get_by_dotted_path(data, path)


def select_list_field(value: Any, field: str, rule_id: str) -> List[Any]:
    if not isinstance(value, list):
        raise ValueError(
            f"{rule_id}: select expects yaml_path to return a list of mappings"
        )
    selected = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise ValueError(f"{rule_id}: select expects mapping at index {index}")
        if field not in item:
            raise ValueError(
                f"{rule_id}: select missing '{field}' at index {index}"
            )
        selected.append(item[field])
    return selected


def extract_yaml_keys(source_path: str, path: str) -> List[str]:
    data = load_yaml(source_path)
    node = get_by_dotted_path(data, path)
    if not isinstance(node, dict):
        raise KeyError("Target is not a mapping")
    return sorted(node.keys())


def extract_glob_list(base_dir: str, pattern: str) -> List[str]:
    matches = glob.glob(os.path.join(base_dir, pattern), recursive=True)
    relative = [os.path.relpath(match, base_dir) for match in matches]
    return sorted(relative)


def extract_text_regex(source_path: str, pattern: str, group: int) -> str:
    with open(source_path, "r", encoding="utf-8") as handle:
        content = handle.read()
    match = re.search(pattern, content, re.MULTILINE)
    if not match:
        raise ValueError("Pattern not found")
    return match.group(group)


def validate_manifest(manifest: Dict[str, Any], scenario_id: str) -> List[str]:
    errors = []
    required_fields = [
        "schema_version",
        "scenario_id",
        "title",
        "attack_type",
        "description",
        "capabilities",
        "required_artifacts",
    ]
    for field in required_fields:
        if field not in manifest:
            errors.append(f"Missing required field: {field}")

    if manifest.get("schema_version") != "v1":
        errors.append("schema_version must be 'v1'")

    if manifest.get("scenario_id") != scenario_id:
        errors.append("scenario_id does not match scenario directory")

    capabilities = manifest.get("capabilities")
    if not isinstance(capabilities, list) or not all(
        isinstance(item, str) for item in capabilities
    ):
        errors.append("capabilities must be a list of strings")

    required_artifacts = manifest.get("required_artifacts")
    if not isinstance(required_artifacts, dict):
        errors.append("required_artifacts must be a mapping of capability to paths")
    else:
        capability_set = set(capabilities or [])
        for capability in required_artifacts.keys():
            if capability not in capability_set:
                errors.append(
                    f"required_artifacts key '{capability}' not in capabilities"
                )

    return errors


def validate_required_artifacts(
    artifacts_dir: str, required_artifacts: Dict[str, List[str]]
) -> Tuple[Dict[str, str], bool, List[str]]:
    results = {}
    notes = []
    all_passed = True

    for capability, paths in required_artifacts.items():
        if not isinstance(paths, list):
            results[str(paths)] = "FAIL"
            notes.append(f"required_artifacts for {capability} must be a list")
            all_passed = False
            continue

        for rel_path in paths:
            if not isinstance(rel_path, str):
                results[str(rel_path)] = "FAIL"
                notes.append("required_artifacts paths must be strings")
                all_passed = False
                continue

            if not is_relative_path(rel_path):
                results[rel_path] = "FAIL"
                notes.append(f"Path must be relative to artifacts/: {rel_path}")
                all_passed = False
                continue

            full_path = os.path.join(artifacts_dir, rel_path)
            if os.path.isfile(full_path):
                results[rel_path] = "PASS"
            elif os.path.isdir(full_path):
                if directory_has_files(full_path):
                    results[rel_path] = "PASS"
                else:
                    results[rel_path] = "FAIL"
                    notes.append(f"Directory is empty: {rel_path}")
                    all_passed = False
            else:
                results[rel_path] = "FAIL"
                notes.append(f"Required artifact missing: {rel_path}")
                all_passed = False

    return results, all_passed, notes


def run_deep_checks(
    artifacts_dir: str, capabilities: List[str]
) -> Tuple[Dict[str, str], bool, List[str]]:
    results = {}
    notes = []
    all_passed = True

    for capability in capabilities:
        if capability == "prompts":
            prompts_dir = os.path.join(artifacts_dir, "prompts")
            md_files = glob.glob(os.path.join(prompts_dir, "**", "*.md"), recursive=True)
            if os.path.isdir(prompts_dir) and md_files:
                results[capability] = "PASS"
            else:
                results[capability] = "FAIL"
                all_passed = False
        elif capability == "helm_repo":
            repo_path = os.path.join(artifacts_dir, "helm_repo", "index.yaml")
            try:
                data = load_yaml(repo_path)
                entries = data.get("entries") if isinstance(data, dict) else None
                if isinstance(entries, dict) and entries:
                    results[capability] = "PASS"
                else:
                    results[capability] = "FAIL"
                    all_passed = False
            except FileNotFoundError:
                results[capability] = "FAIL"
                all_passed = False
            except yaml.YAMLError as exc:
                results[capability] = "FAIL"
                all_passed = False
                notes.append(
                    f"helm_repo YAML parse error: {type(exc).__name__}: {exc}"
                )
            except Exception as exc:  # noqa: BLE001
                results[capability] = "FAIL"
                all_passed = False
                notes.append(
                    f"helm_repo validation error ({type(exc).__name__}): {exc}"
                )
        elif capability == "helm_chart":
            chart_path = os.path.join(artifacts_dir, "chart", "Chart.yaml")
            templates_dir = os.path.join(artifacts_dir, "chart", "templates")
            yaml_files = glob.glob(
                os.path.join(templates_dir, "**", "*.y*ml"), recursive=True
            )
            try:
                data = load_yaml(chart_path)
                if (
                    isinstance(data, dict)
                    and data.get("name")
                    and data.get("version")
                    and os.path.isdir(templates_dir)
                    and yaml_files
                ):
                    results[capability] = "PASS"
                else:
                    results[capability] = "FAIL"
                    all_passed = False
            except FileNotFoundError:
                results[capability] = "FAIL"
                all_passed = False
            except yaml.YAMLError as exc:
                results[capability] = "FAIL"
                all_passed = False
                notes.append(
                    f"helm_chart YAML parse error: {type(exc).__name__}: {exc}"
                )
            except Exception as exc:  # noqa: BLE001
                results[capability] = "FAIL"
                all_passed = False
                notes.append(
                    f"helm_chart validation error ({type(exc).__name__}): {exc}"
                )
        else:
            results[capability] = "WARN"
            notes.append(f"Unknown capability: {capability}")

    return results, all_passed, notes


def run_extractions(
    artifacts_dir: str, extract_rules: List[Dict[str, Any]]
) -> Tuple[Dict[str, Any], bool, List[str]]:
    results = {}
    all_passed = True
    notes = []

    for rule in extract_rules:
        rule_id = rule.get("id")
        kind = rule.get("kind")
        source = rule.get("source")
        required = rule.get("required", True)
        if not rule_id or not kind or not source:
            all_passed = False
            notes.append("Extract rule missing required fields (id/kind/source)")
            continue

        source_path = os.path.join(artifacts_dir, source)
        select = rule.get("select")
        if select and kind != "yaml_path":
            message = f"{rule_id}: select is only supported for yaml_path"
            if required:
                all_passed = False
                notes.append(f"Extraction failed for {rule_id}: {message}")
            else:
                notes.append(f"Optional extraction skipped for {rule_id}: {message}")
            results[rule_id] = None
            continue
        try:
            if kind == "yaml_path":
                path = rule.get("path")
                if not path:
                    raise ValueError("yaml_path requires 'path'")
                value = extract_yaml_path(source_path, path)
                if select:
                    value = select_list_field(value, select, rule_id)
            elif kind == "yaml_keys":
                path = rule.get("path")
                if not path:
                    raise ValueError("yaml_keys requires 'path'")
                value = extract_yaml_keys(source_path, path)
            elif kind == "glob_list":
                value = extract_glob_list(artifacts_dir, source)
                if not value:
                    raise ValueError("No files matched glob pattern")
            elif kind == "text_regex":
                pattern = rule.get("pattern")
                if not pattern:
                    raise ValueError("text_regex requires 'pattern'")
                group = int(rule.get("group", 1))
                value = extract_text_regex(source_path, pattern, group)
            else:
                raise ValueError(f"Unknown extract kind: {kind}")

            results[rule_id] = value
        except Exception as exc:  # noqa: BLE001
            if required:
                all_passed = False
                notes.append(f"Extraction failed for {rule_id}: {exc}")
            else:
                notes.append(f"Optional extraction skipped for {rule_id}: {exc}")
            results[rule_id] = None

    return results, all_passed, notes


def emit_artifacts_map(
    output_path: str,
    manifest: Dict[str, Any],
    required_artifacts_passed: bool,
    deep_checks: Dict[str, str],
    extracted: Dict[str, Any],
    notes: List[str],
    crashed: bool,
) -> None:
    verification = {
        "required_artifacts_passed": required_artifacts_passed,
        "deep_checks": deep_checks,
        "notes": notes,
    }
    if crashed:
        verification["crashed"] = True
    payload = {
        "schema_version": "v1",
        "scenario_id": manifest.get("scenario_id"),
        "title": manifest.get("title"),
        "attack_type": manifest.get("attack_type"),
        "description": manifest.get("description"),
        "capabilities": manifest.get("capabilities"),
        "required_artifacts": manifest.get("required_artifacts"),
        "verification": verification,
        "extracted_identifiers": extracted,
        "generated_at": datetime.datetime.now(
            datetime.timezone.utc
        ).isoformat(),
    }
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def print_summary(
    scenario_id: str,
    capabilities: List[str],
    required_results: Dict[str, str],
    deep_checks: Dict[str, str],
    extracted: Dict[str, Any],
    artifacts_map_path: str,
    notes: List[str],
) -> None:
    print(f"=== {scenario_id} Phase 3 – Step 1 Verification ===")
    print(f"Capabilities: {capabilities}")
    print("Required Artifacts:")
    for path, status in required_results.items():
        print(f"  - {path}: {status}")
    print("Deep Checks:")
    for capability, status in deep_checks.items():
        print(f"  - {capability}: {status}")
    print("Extracted Identifiers:")
    for rule_id, value in extracted.items():
        print(f"  - {rule_id}: {value}")
    print("Emitted:")
    print(f"  - artifacts_map: {artifacts_map_path}")
    print("Notes/WARN:")
    if notes:
        for note in notes:
            print(f"  - {note}")
    else:
        print("  - None")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify scenario artifacts and emit artifacts_map.json"
    )
    parser.add_argument("scenario_id", help="Scenario identifier")
    parser.add_argument("--emit-map", action="store_true", help="(reserved)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    scenario_id = args.scenario_id
    artifacts_dir = os.path.join("scenarios", scenario_id, "artifacts")
    manifest_path = os.path.join(artifacts_dir, "manifest.yaml")

    notes: List[str] = []
    manifest: Dict[str, Any] = {"scenario_id": scenario_id}
    capabilities: List[str] = []
    required_results: Dict[str, str] = {}
    deep_checks: Dict[str, str] = {}
    extracted: Dict[str, Any] = {}
    required_passed = False
    deep_passed = False
    extract_passed = False
    errors: List[str] = []
    crashed = False
    artifacts_map_path = os.path.join(artifacts_dir, "artifacts_map.json")

    try:
        if not os.path.exists(manifest_path):
            notes.append(f"Manifest missing: {manifest_path}")
            errors.append("manifest.yaml is required")
        else:
            try:
                manifest = load_yaml(manifest_path) or {}
            except yaml.YAMLError as exc:
                notes.append(
                    f"manifest.yaml YAML parse failed ({type(exc).__name__}): {exc}"
                )
                errors.append("manifest.yaml could not be parsed")
                manifest = {"scenario_id": scenario_id}

        if not isinstance(manifest, dict):
            notes.append("manifest.yaml must parse to a mapping")
            errors.append("manifest.yaml invalid format")
            manifest = {"scenario_id": scenario_id}

        errors.extend(validate_manifest(manifest, scenario_id))
        notes.extend(errors)

        capabilities = manifest.get("capabilities", [])
        if not isinstance(capabilities, list):
            capabilities = []

        required_artifacts = manifest.get("required_artifacts", {})
        if not isinstance(required_artifacts, dict):
            required_artifacts = {}

        required_results, required_passed, required_notes = validate_required_artifacts(
            artifacts_dir, required_artifacts
        )
        notes.extend(required_notes)

        deep_checks, deep_passed, deep_notes = run_deep_checks(
            artifacts_dir, capabilities
        )
        notes.extend(deep_notes)

        extract_rules = manifest.get("extract", [])
        if extract_rules is None:
            extract_rules = []
        extracted, extract_passed, extract_notes = run_extractions(
            artifacts_dir, extract_rules
        )
        notes.extend(extract_notes)
    except Exception as exc:  # noqa: BLE001
        crashed = True
        notes.append(f"Verifier crashed ({type(exc).__name__}): {exc}")
    finally:
        os.makedirs(artifacts_dir, exist_ok=True)
        emit_artifacts_map(
            artifacts_map_path,
            manifest,
            required_passed,
            deep_checks,
            extracted,
            notes,
            crashed,
        )

    print_summary(
        scenario_id,
        capabilities,
        required_results,
        deep_checks,
        extracted,
        artifacts_map_path,
        notes,
    )

    success = (
        required_passed and deep_passed and extract_passed and not errors and not crashed
    )
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
