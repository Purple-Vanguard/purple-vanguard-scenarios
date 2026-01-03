from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = REPO_ROOT / "scenarios" / "badblueprint"


REQUIRED_PATHS = {
    "helm_repo_index": SCENARIO_DIR / "artifacts" / "helm_repo" / "index.yaml",
    "chart_yaml": SCENARIO_DIR / "artifacts" / "chart" / "Chart.yaml",
    "values_yaml": SCENARIO_DIR / "artifacts" / "chart" / "values.yaml",
    "chart_templates_dir": SCENARIO_DIR / "artifacts" / "chart" / "templates",
    "prompts_dir": SCENARIO_DIR / "prompts",
    "scenario_config": SCENARIO_DIR / "scenario_config.yaml",
}


YAML_FILES = [
    REQUIRED_PATHS["helm_repo_index"],
    REQUIRED_PATHS["chart_yaml"],
    REQUIRED_PATHS["values_yaml"],
    REQUIRED_PATHS["scenario_config"],
]


def _assert_exists(path: Path, description: str) -> None:
    assert path.exists(), f"Expected {description} at {path}, but it does not exist."


def _assert_dir_has_files(path: Path, description: str) -> None:
    assert path.is_dir(), f"Expected {description} at {path}, but it is not a directory."
    files = [entry for entry in path.iterdir() if entry.is_file()]
    assert files, f"Expected {description} at {path} to contain at least one file."


def _parse_yaml(path: Path) -> Any:
    try:
        content = path.read_text(encoding="utf-8")
        return yaml.safe_load(content)
    except yaml.YAMLError as exc:
        pytest.fail(f"Failed to parse YAML file at {path}: {exc}")


def _looks_like_url(value: str) -> bool:
    return value.startswith("http://") or value.startswith("https://") or "://" in value


def _iter_referenced_paths(data: Any, key_path: Iterable[str] = ()) -> Iterable[tuple[str, str]]:
    if isinstance(data, dict):
        for key, value in data.items():
            new_key_path = (*key_path, str(key))
            lowered_key = str(key).lower()
            if any(token in lowered_key for token in ("path", "file", "dir")):
                if isinstance(value, str):
                    yield (".".join(new_key_path), value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, str):
                            yield (".".join(new_key_path), item)
            yield from _iter_referenced_paths(value, new_key_path)
    elif isinstance(data, list):
        for index, item in enumerate(data):
            yield from _iter_referenced_paths(item, (*key_path, str(index)))


@pytest.mark.parametrize(
    ("path", "description"),
    [
        (REQUIRED_PATHS["helm_repo_index"], "helm repo index.yaml"),
        (REQUIRED_PATHS["chart_yaml"], "chart Chart.yaml"),
        (REQUIRED_PATHS["values_yaml"], "chart values.yaml"),
        (REQUIRED_PATHS["scenario_config"], "scenario_config.yaml"),
    ],
)
def test_required_files_exist(path: Path, description: str) -> None:
    _assert_exists(path, description)


def test_required_directories_exist_and_have_files() -> None:
    _assert_dir_has_files(REQUIRED_PATHS["chart_templates_dir"], "chart templates directory")
    _assert_dir_has_files(REQUIRED_PATHS["prompts_dir"], "prompts directory")


def test_yaml_files_parse() -> None:
    for path in YAML_FILES:
        _assert_exists(path, f"YAML file {path.name}")
        _parse_yaml(path)


def test_config_referenced_paths_exist() -> None:
    config_path = REQUIRED_PATHS["scenario_config"]
    _assert_exists(config_path, "scenario_config.yaml")
    config_data = _parse_yaml(config_path)
    if not config_data:
        return

    for key_path, value in _iter_referenced_paths(config_data):
        if _looks_like_url(value):
            continue
        candidate = Path(value)
        resolved = candidate if candidate.is_absolute() else SCENARIO_DIR / candidate
        assert resolved.exists(), (
            f"scenario_config.yaml references missing path '{value}' at '{key_path}'. "
            f"Resolved path: {resolved}"
        )
