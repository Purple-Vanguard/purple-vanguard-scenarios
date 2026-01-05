from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = REPO_ROOT / "scenarios" / "badblueprint"


def test_scenario_config_exists() -> None:
    assert (SCENARIO_DIR / "scenario_config.yaml").exists()


def test_prompts_directory_contains_required_files() -> None:
    prompts_dir = SCENARIO_DIR / "prompts"
    assert prompts_dir.is_dir()

    required_files = {
        "attacker_lure.md",
        "attacker_lure.txt",
        "devops_task_request.md",
        "devops_task_request.txt",
    }
    present_files = {path.name for path in prompts_dir.iterdir() if path.is_file()}
    missing = required_files - present_files
    assert not missing, f"Missing required prompt files: {sorted(missing)}"


def test_helm_repo_index_exists() -> None:
    assert (SCENARIO_DIR / "artifacts" / "helm_repo" / "index.yaml").exists()


def test_chart_files_exist() -> None:
    chart_dir = SCENARIO_DIR / "artifacts" / "chart"
    assert (chart_dir / "Chart.yaml").exists()
    assert (chart_dir / "values.yaml").exists()


def test_chart_templates_dir_non_empty() -> None:
    templates_dir = SCENARIO_DIR / "artifacts" / "chart" / "templates"
    assert templates_dir.is_dir()
    assert any(path.is_file() for path in templates_dir.iterdir())
