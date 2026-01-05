#!/usr/bin/env python3
"""Validate a submission bundle produced by export_badblueprint_submission.py."""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VENDOR_SUBMISSIONS = (
    REPO_ROOT
    / "vendor"
    / "agentbeats-lambda"
    / "scenarios"
    / "security_arena"
    / "submissions"
)


def _fail(message: str) -> None:
    raise SystemExit(f"Validation error: {message}")


def _load_toml(path: Path) -> dict:
    try:
        import tomllib
    except ModuleNotFoundError:  # pragma: no cover - fallback for <3.11
        try:
            import toml as tomllib  # type: ignore[assignment]
        except ModuleNotFoundError as exc:  # pragma: no cover
            raise SystemExit(
                "Validation error: tomllib unavailable; install toml for Python < 3.11"
            ) from exc

    return tomllib.loads(path.read_text(encoding="utf-8"))


def _assert_vendor_submissions_untouched() -> None:
    if not VENDOR_SUBMISSIONS.exists():
        _fail(f"Vendor submissions path missing: {VENDOR_SUBMISSIONS}")

    if not any(VENDOR_SUBMISSIONS.rglob("*")):
        _fail(f"Vendor submissions path is empty: {VENDOR_SUBMISSIONS}")

    git_dir = REPO_ROOT / ".git"
    if git_dir.exists():
        result = subprocess.run(
            ["git", "status", "--porcelain", str(VENDOR_SUBMISSIONS)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.stdout.strip():
            _fail(
                "Vendor submissions content was modified:\n"
                f"{result.stdout.strip()}"
            )


def _validate_plugin_entrypoint(plugin_path: Path) -> None:
    tree = ast.parse(plugin_path.read_text(encoding="utf-8"))
    class_found = False
    register_found = False
    main_found = False

    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "BadBlueprintPlugin":
            class_found = any(
                isinstance(base, ast.Name) and base.id == "ScenarioPlugin"
                for base in node.bases
            )
        if isinstance(node, ast.FunctionDef) and node.name == "register":
            register_found = True
        if isinstance(node, ast.FunctionDef) and node.name == "main":
            main_found = True

    if not class_found:
        _fail("Plugin must define BadBlueprintPlugin inheriting ScenarioPlugin")
    if not register_found:
        _fail("Plugin must define register() entrypoint")
    if not main_found:
        _fail("Plugin must define main() entrypoint")


def main() -> None:
    if len(sys.argv) != 2:
        _fail("Usage: python scripts/validate_submission_bundle.py <bundle_dir>")

    bundle_dir = Path(sys.argv[1]).resolve()
    if not bundle_dir.exists():
        _fail(f"Bundle directory does not exist: {bundle_dir}")

    toml_files = list(bundle_dir.glob("scenario_*.toml"))
    if not toml_files:
        _fail("Missing scenario_*.toml in bundle directory")

    for toml_path in toml_files:
        _load_toml(toml_path)

    plugin_files = list(bundle_dir.glob("plugin_*.py"))
    if not plugin_files:
        _fail("Missing plugin_*.py in bundle directory")

    _validate_plugin_entrypoint(plugin_files[0])

    artifacts_dir = bundle_dir / "artifacts"
    if not artifacts_dir.exists() or not any(artifacts_dir.rglob("*")):
        _fail("artifacts/ missing or empty")

    prompts_dir = bundle_dir / "prompts"
    if not prompts_dir.exists() or not any(prompts_dir.rglob("*")):
        _fail("prompts/ missing or empty")

    _assert_vendor_submissions_untouched()

    print(f"Bundle validation passed: {bundle_dir}")


if __name__ == "__main__":
    main()
