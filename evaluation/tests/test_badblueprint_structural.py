from __future__ import annotations

from pathlib import Path

import yaml

SCENARIO_ROOT = Path("scenarios/badblueprint")

REQUIRED_PATHS = {
    "helm_index": SCENARIO_ROOT / "artifacts/helm_repo/index.yaml",
    "chart_yaml": SCENARIO_ROOT / "artifacts/chart/Chart.yaml",
    "values_yaml": SCENARIO_ROOT / "artifacts/chart/values.yaml",
    "chart_templates_dir": SCENARIO_ROOT / "artifacts/chart/templates",
    "prompts_dir": SCENARIO_ROOT / "prompts",
    "scenario_config": SCENARIO_ROOT / "scenario_config.yaml",
}

YAML_FILES = [
    REQUIRED_PATHS["helm_index"],
    REQUIRED_PATHS["chart_yaml"],
    REQUIRED_PATHS["values_yaml"],
    REQUIRED_PATHS["scenario_config"],
]


def _parse_yaml(path: Path) -> object:
    try:
        return yaml.safe_load(path.read_text())
    except Exception as exc:  # pragma: no cover - ensure assertion detail
        raise AssertionError(f"Failed to parse YAML at {path}: {exc}") from exc


def _looks_like_path(value: str) -> bool:
    if "://" in value:
        return False
    if value.startswith("~"):
        return True
    return "/" in value or value.endswith((".yaml", ".yml", ".json", ".md", ".txt"))


def _iter_path_strings(data: object) -> list[str]:
    paths: list[str] = []
    if isinstance(data, dict):
        for value in data.values():
            paths.extend(_iter_path_strings(value))
    elif isinstance(data, list):
        for value in data:
            paths.extend(_iter_path_strings(value))
    elif isinstance(data, str) and _looks_like_path(data):
        paths.append(data)
    return paths


def test_required_paths_exist() -> None:
    missing = [name for name, path in REQUIRED_PATHS.items() if not path.exists()]
    assert not missing, f"Missing required paths: {', '.join(missing)}"

    templates = list(REQUIRED_PATHS["chart_templates_dir"].iterdir())
    assert templates, "Chart templates directory must contain at least one file"

    prompts = list(REQUIRED_PATHS["prompts_dir"].iterdir())
    assert prompts, "Prompts directory must contain at least one file"


def test_yaml_parseability() -> None:
    for path in YAML_FILES:
        assert path.exists(), f"Expected YAML file to exist at {path}"
        _parse_yaml(path)


def test_config_referenced_paths_exist() -> None:
    config_path = REQUIRED_PATHS["scenario_config"]
    config = _parse_yaml(config_path) or {}
    assert isinstance(config, dict), "scenario_config.yaml must parse to a mapping"

    candidate_paths = _iter_path_strings(config)
    missing: list[str] = []
    for candidate in candidate_paths:
        candidate_path = Path(candidate)
        if not candidate_path.is_absolute():
            candidate_path = config_path.parent / candidate_path
        if not candidate_path.exists():
            missing.append(f"{candidate} -> {candidate_path}")

    assert not missing, (
        "scenario_config.yaml references missing paths: " + "; ".join(missing)
    )
