from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = REPO_ROOT / "scenarios" / "badblueprint"


def test_required_files_exist() -> None:
    required_files = [
        SCENARIO_DIR / "artifacts" / "helm_repo" / "index.yaml",
        SCENARIO_DIR / "artifacts" / "chart" / "Chart.yaml",
        SCENARIO_DIR / "artifacts" / "chart" / "values.yaml",
        SCENARIO_DIR / "scenario_config.yaml",
    ]
    for path in required_files:
        assert path.exists(), f"Expected file at {path}"


def test_required_directories_exist_and_have_files() -> None:
    templates_dir = SCENARIO_DIR / "artifacts" / "chart" / "templates"
    prompts_dir = SCENARIO_DIR / "prompts"

    assert templates_dir.is_dir(), f"Expected templates directory at {templates_dir}"
    assert any(templates_dir.iterdir()), f"Expected templates directory at {templates_dir} to have files"

    assert prompts_dir.is_dir(), f"Expected prompts directory at {prompts_dir}"
    assert any(prompts_dir.iterdir()), f"Expected prompts directory at {prompts_dir} to have files"
