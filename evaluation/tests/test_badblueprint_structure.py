from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = REPO_ROOT / "scenarios" / "badblueprint"


EXPECTED_PROMPTS = {
    "attacker_lure.md",
    "attacker_lure.txt",
    "devops_task_request.md",
    "devops_task_request.txt",
}


def test_scenario_config_exists() -> None:
    config_path = SCENARIO_DIR / "scenario_config.yaml"
    assert config_path.exists(), f"Missing scenario_config.yaml at {config_path}"


def test_prompts_directory_contains_required_files() -> None:
    prompt_dir = SCENARIO_DIR / "prompts"
    assert prompt_dir.is_dir(), f"Missing prompts directory at {prompt_dir}"
    prompt_files = {path.name for path in prompt_dir.iterdir() if path.is_file()}
    missing = EXPECTED_PROMPTS - prompt_files
    assert not missing, f"Missing prompt files: {sorted(missing)}"


def test_helm_repo_index_exists() -> None:
    helm_index = SCENARIO_DIR / "artifacts" / "helm_repo" / "index.yaml"
    assert helm_index.exists(), f"Missing helm repo index at {helm_index}"


def test_chart_files_exist() -> None:
    chart_dir = SCENARIO_DIR / "artifacts" / "chart"
    chart_yaml = chart_dir / "Chart.yaml"
    values_yaml = chart_dir / "values.yaml"
    assert chart_yaml.exists(), f"Missing chart yaml at {chart_yaml}"
    assert values_yaml.exists(), f"Missing values yaml at {values_yaml}"


def test_chart_templates_directory_is_populated() -> None:
    templates_dir = SCENARIO_DIR / "artifacts" / "chart" / "templates"
    assert templates_dir.is_dir(), f"Missing templates directory at {templates_dir}"
    template_files = [path for path in templates_dir.iterdir() if path.is_file()]
    assert template_files, f"No template files found in {templates_dir}"
