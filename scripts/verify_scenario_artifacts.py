#!/usr/bin/env python3
import argparse
import datetime
import json
import os
import re
import sys
from glob import glob

import yaml


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def is_relative_artifact_path(path):
    if os.path.isabs(path):
        return False
    normalized = os.path.normpath(path)
    return not normalized.startswith("..") and not normalized.startswith("../")


def dotted_get(value, dotted_path):
    if dotted_path is None or dotted_path == "":
        return value
    current = value
    for part in dotted_path.split("."):
        if isinstance(current, dict):
            if part not in current:
                return None
            current = current[part]
        elif isinstance(current, list):
            if not part.isdigit():
                return None
            index = int(part)
            if index >= len(current):
                return None
            current = current[index]
        else:
            return None
    return current


def ensure_non_empty_dir(path):
    if not os.path.isdir(path):
        return False
    for _, _, files in os.walk(path):
        if files:
            return True
    return False


def relative_paths(paths, base_dir):
    rel_paths = []
    for path in paths:
        rel_paths.append(os.path.relpath(path, base_dir))
    return rel_paths


def verify_required_artifacts(artifacts_dir, required_artifacts):
    results = []
    all_passed = True
    for _, paths in required_artifacts.items():
        for rel_path in paths:
            status = "PASS"
            if not is_relative_artifact_path(rel_path):
                status = "FAIL"
            else:
                abs_path = os.path.join(artifacts_dir, rel_path)
                if os.path.isfile(abs_path):
                    try:
                        with open(abs_path, "r", encoding="utf-8"):
                            pass
                    except OSError:
                        status = "FAIL"
                elif os.path.isdir(abs_path):
                    if not ensure_non_empty_dir(abs_path):
                        status = "FAIL"
                else:
                    status = "FAIL"
            results.append((rel_path, status))
            if status != "PASS":
                all_passed = False
    return results, all_passed


def deep_check_prompts(artifacts_dir):
    prompts_dir = os.path.join(artifacts_dir, "prompts")
    if not os.path.isdir(prompts_dir):
        return False
    matches = glob(os.path.join(prompts_dir, "**", "*.md"), recursive=True)
    return len(matches) > 0


def deep_check_helm_repo(artifacts_dir):
    index_path = os.path.join(artifacts_dir, "helm_repo", "index.yaml")
    if not os.path.isfile(index_path):
        return False
    data = load_yaml(index_path)
    if not isinstance(data, dict):
        return False
    entries = data.get("entries")
    return isinstance(entries, dict) and len(entries) > 0


def deep_check_helm_chart(artifacts_dir):
    chart_path = os.path.join(artifacts_dir, "chart", "Chart.yaml")
    templates_dir = os.path.join(artifacts_dir, "chart", "templates")
    if not os.path.isfile(chart_path):
        return False
    chart_data = load_yaml(chart_path)
    if not isinstance(chart_data, dict):
        return False
    if not chart_data.get("name") or not chart_data.get("version"):
        return False
    if not os.path.isdir(templates_dir):
        return False
    template_matches = []
    template_matches.extend(glob(os.path.join(templates_dir, "**", "*.yaml"), recursive=True))
    template_matches.extend(glob(os.path.join(templates_dir, "**", "*.yml"), recursive=True))
    return len(template_matches) > 0


def run_deep_checks(artifacts_dir, capabilities, warnings):
    statuses = {}
    for capability in capabilities:
        if capability == "prompts":
            statuses[capability] = "PASS" if deep_check_prompts(artifacts_dir) else "FAIL"
        elif capability == "helm_repo":
            statuses[capability] = "PASS" if deep_check_helm_repo(artifacts_dir) else "FAIL"
        elif capability == "helm_chart":
            statuses[capability] = "PASS" if deep_check_helm_chart(artifacts_dir) else "FAIL"
        else:
            statuses[capability] = "WARN"
            warnings.append(f"Unknown capability '{capability}'")
    return statuses


def extract_yaml_path(source_path, path):
    data = load_yaml(source_path)
    return dotted_get(data, path)


def extract_yaml_keys(source_path, path):
    data = load_yaml(source_path)
    target = dotted_get(data, path)
    if not isinstance(target, dict):
        return None
    return list(target.keys())


def extract_glob_list(artifacts_dir, pattern):
    matches = glob(os.path.join(artifacts_dir, pattern), recursive=True)
    matches = sorted(relative_paths(matches, artifacts_dir))
    return matches


def extract_text_regex(source_path, pattern, group):
    with open(source_path, "r", encoding="utf-8") as handle:
        text = handle.read()
    match = re.search(pattern, text)
    if not match:
        return None
    try:
        return match.group(group)
    except IndexError:
        return None


def run_extractions(artifacts_dir, extract_rules, warnings):
    extracted = {}
    failures = []
    for rule in extract_rules:
        rule_id = rule.get("id")
        kind = rule.get("kind")
        source = rule.get("source")
        required = rule.get("required", True)
        if not rule_id or not kind or not source:
            failures.append("Extraction rule missing id, kind, or source")
            continue

        value = None
        try:
            if kind == "yaml_path":
                source_path = os.path.join(artifacts_dir, source)
                value = extract_yaml_path(source_path, rule.get("path"))
            elif kind == "yaml_keys":
                source_path = os.path.join(artifacts_dir, source)
                value = extract_yaml_keys(source_path, rule.get("path"))
            elif kind == "glob_list":
                value = extract_glob_list(artifacts_dir, source)
            elif kind == "text_regex":
                source_path = os.path.join(artifacts_dir, source)
                group = rule.get("group", 1)
                value = extract_text_regex(source_path, rule.get("pattern", ""), group)
            else:
                warnings.append(f"Unknown extract kind '{kind}' for id '{rule_id}'")
        except (OSError, yaml.YAMLError, re.error) as exc:
            warnings.append(f"Extraction '{rule_id}' failed: {exc}")
            value = None

        if value is None or (isinstance(value, list) and len(value) == 0):
            if required:
                failures.append(f"Extraction '{rule_id}' failed")
            else:
                warnings.append(f"Extraction '{rule_id}' returned no results")

        extracted[rule_id] = value

    return extracted, failures


def emit_artifacts_map(
    artifacts_dir,
    manifest,
    required_paths,
    required_artifacts_passed,
    deep_checks,
    extracted,
):
    output = {
        "schema_version": "v1",
        "scenario_id": manifest.get("scenario_id"),
        "title": manifest.get("title"),
        "attack_type": manifest.get("attack_type"),
        "description": manifest.get("description"),
        "capabilities": manifest.get("capabilities"),
        "required_artifacts": required_paths,
        "verification": {
            "required_artifacts_passed": required_artifacts_passed,
            "deep_checks": deep_checks,
        },
        "extracted_identifiers": extracted,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    output_path = os.path.join(artifacts_dir, "artifacts_map.json")
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return output_path


def print_summary(
    scenario_id,
    capabilities,
    required_results,
    deep_checks,
    extracted,
    artifacts_map_path,
    warnings,
):
    print(f"=== {scenario_id} Phase 3 – Step 1 Verification ===")
    print(f"Capabilities: {capabilities}")
    print("Required Artifacts:")
    if required_results:
        for rel_path, status in required_results:
            print(f"  - {rel_path}: {status}")
    else:
        print("  - None")
    print("Deep Checks:")
    if deep_checks:
        for capability, status in deep_checks.items():
            print(f"  - {capability}: {status}")
    else:
        print("  - None")
    print("Extracted Identifiers:")
    if extracted:
        for extract_id, value in extracted.items():
            print(f"  - {extract_id}: {value}")
    else:
        print("  - None")
    print("Emitted:")
    print(f"  - artifacts_map: {artifacts_map_path}")
    print("Notes/WARN:")
    if warnings:
        for note in warnings:
            print(f"  - {note}")
    else:
        print("  - None")


def validate_manifest(manifest, scenario_id):
    errors = []
    if not isinstance(manifest, dict):
        errors.append("manifest must be a mapping")
        return errors
    if manifest.get("schema_version") != "v1":
        errors.append("schema_version must be 'v1'")
    if manifest.get("scenario_id") != scenario_id:
        errors.append("scenario_id must match scenario folder")
    capabilities = manifest.get("capabilities")
    if not isinstance(capabilities, list) or not all(
        isinstance(cap, str) for cap in capabilities
    ):
        errors.append("capabilities must be a list of strings")
    required_artifacts = manifest.get("required_artifacts")
    if not isinstance(required_artifacts, dict):
        errors.append("required_artifacts must be a map of capability to list of paths")
        required_artifacts = {}
    else:
        for cap, paths in required_artifacts.items():
            if not isinstance(paths, list) or not all(
                isinstance(path, str) for path in paths
            ):
                errors.append(
                    f"required_artifacts for capability '{cap}' must be a list of strings"
                )
    if isinstance(capabilities, list) and isinstance(required_artifacts, dict):
        if not set(required_artifacts.keys()).issubset(set(capabilities)):
            errors.append("required_artifacts keys must be a subset of capabilities")
    return errors


def main():
    parser = argparse.ArgumentParser(description="Verify scenario artifacts (Phase 3 Step 1)")
    parser.add_argument("scenario_id", help="Scenario ID")
    parser.add_argument("--emit-map", action="store_true", help="Emit artifacts_map.json")
    args = parser.parse_args()

    scenario_id = args.scenario_id
    artifacts_dir = os.path.join("scenarios", scenario_id, "artifacts")
    manifest_path = os.path.join(artifacts_dir, "manifest.yaml")

    warnings = []
    required_results = []
    required_artifacts_passed = False
    deep_checks = {}
    extracted = {}
    required_paths = []

    if not os.path.isfile(manifest_path):
        warnings.append("manifest.yaml missing")
        print_summary(
            scenario_id,
            [],
            [],
            {},
            {},
            os.path.join(artifacts_dir, "artifacts_map.json"),
            warnings,
        )
        return 1

    try:
        manifest = load_yaml(manifest_path)
    except (OSError, yaml.YAMLError) as exc:
        warnings.append(f"Failed to load manifest: {exc}")
        print_summary(
            scenario_id,
            [],
            [],
            {},
            {},
            os.path.join(artifacts_dir, "artifacts_map.json"),
            warnings,
        )
        return 1

    errors = validate_manifest(manifest, scenario_id)
    if errors:
        warnings.extend(errors)

    capabilities = manifest.get("capabilities", [])
    required_artifacts = manifest.get("required_artifacts", {})
    required_paths = [path for paths in required_artifacts.values() for path in paths]

    required_results, required_artifacts_passed = verify_required_artifacts(
        artifacts_dir, required_artifacts
    )

    deep_checks = run_deep_checks(artifacts_dir, capabilities, warnings)

    extract_rules = manifest.get("extract", []) or []
    extracted, extraction_failures = run_extractions(artifacts_dir, extract_rules, warnings)
    if extraction_failures:
        warnings.extend(extraction_failures)

    artifacts_map_path = emit_artifacts_map(
        artifacts_dir,
        manifest,
        required_paths,
        required_artifacts_passed,
        deep_checks,
        extracted,
    )

    print_summary(
        scenario_id,
        capabilities,
        required_results,
        deep_checks,
        extracted,
        os.path.relpath(artifacts_map_path),
        warnings,
    )

    deep_checks_passed = all(status != "FAIL" for status in deep_checks.values())
    success = (
        not errors
        and required_artifacts_passed
        and deep_checks_passed
        and not extraction_failures
    )
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
