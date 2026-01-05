#!/usr/bin/env python3
"""Validate a submission bundle for AgentBeats security arena."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path


def _load_toml(path: Path) -> dict:
    try:
        import tomllib  # Python 3.11+
    except ModuleNotFoundError:  # pragma: no cover - fallback
        try:
            import toml as tomllib  # type: ignore
        except ModuleNotFoundError as exc:  # pragma: no cover - fallback
            raise RuntimeError("tomllib or toml is required to parse TOML") from exc
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _error(message: str) -> None:
    print(f"ERROR: {message}")
    sys.exit(1)


def _check_vendor_submissions(repo_root: Path) -> None:
    submissions_path = (
        repo_root
        / "vendor"
        / "agentbeats-lambda"
        / "scenarios"
        / "security_arena"
        / "submissions"
    )

    if not submissions_path.exists():
        _error(f"Vendored submissions path missing: {submissions_path}")

    if not any(submissions_path.rglob("*")):
        _error("Vendored submissions directory is empty")

    git_dir = repo_root / ".git"
    if git_dir.exists():
        result = subprocess.run(
            [
                "git",
                "status",
                "--porcelain",
                "--",
                str(submissions_path),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.stdout.strip():
            _error(
                "Vendored submissions directory has uncommitted changes:\n"
                f"{result.stdout.strip()}"
            )


def _load_plugin(plugin_path: Path, repo_root: Path) -> tuple[type, str]:
    vendor_root = repo_root / "vendor" / "agentbeats-lambda"
    sys.path.insert(0, str(vendor_root))

    spec = importlib.util.spec_from_file_location("submission_plugin", plugin_path)
    if spec is None or spec.loader is None:
        _error(f"Unable to import plugin module: {plugin_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if not hasattr(module, "PLUGIN_CLASS"):
        _error("Plugin module is missing PLUGIN_CLASS")
    if not hasattr(module, "SCENARIO_TYPE"):
        _error("Plugin module is missing SCENARIO_TYPE")

    plugin_class = getattr(module, "PLUGIN_CLASS")
    scenario_type = getattr(module, "SCENARIO_TYPE")

    from scenarios.security_arena.plugins.base import ScenarioPlugin

    if not isinstance(scenario_type, str) or not scenario_type:
        _error("SCENARIO_TYPE must be a non-empty string")

    if not isinstance(plugin_class, type) or not issubclass(plugin_class, ScenarioPlugin):
        _error("PLUGIN_CLASS must be a ScenarioPlugin subclass")

    return plugin_class, scenario_type


def validate_bundle(bundle_dir: Path) -> None:
    if not bundle_dir.exists():
        _error(f"Bundle directory not found: {bundle_dir}")

    toml_paths = sorted(bundle_dir.glob("scenario_*.toml"))
    if not toml_paths:
        _error("No scenario_*.toml files found in bundle")

    for toml_path in toml_paths:
        try:
            _load_toml(toml_path)
        except Exception as exc:
            _error(f"Failed to parse TOML {toml_path}: {exc}")

    plugin_paths = sorted(bundle_dir.glob("plugin_*.py"))
    if not plugin_paths:
        _error("No plugin_*.py files found in bundle")

    artifacts_dir = bundle_dir / "artifacts"
    prompts_dir = bundle_dir / "prompts"

    if not artifacts_dir.is_dir():
        _error("artifacts/ directory missing from bundle")
    if not any(artifacts_dir.rglob("*")):
        _error("artifacts/ directory is empty")

    if not prompts_dir.is_dir():
        _error("prompts/ directory missing from bundle")
    if not any(prompts_dir.rglob("*")):
        _error("prompts/ directory is empty")

    repo_root = Path(__file__).resolve().parents[1]
    _check_vendor_submissions(repo_root)

    plugin_class, scenario_type = _load_plugin(plugin_paths[0], repo_root)
    print(f"Validated plugin {plugin_class.__name__} for scenario {scenario_type}")


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python scripts/validate_submission_bundle.py <bundle_dir>")
        sys.exit(1)

    bundle_dir = Path(sys.argv[1]).resolve()
    validate_bundle(bundle_dir)
    print("Bundle validation OK")


if __name__ == "__main__":
    main()
