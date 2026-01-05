#!/usr/bin/env python3
"""Launch the AgentBeats orchestrator with the badblueprint plugin registered."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path


def _register_plugin() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    vendor_root = repo_root / "vendor" / "agentbeats-lambda"
    submission_dir = repo_root / "submissions" / "purple_vanguard" / "badblueprint"

    sys.path.insert(0, str(vendor_root))
    sys.path.insert(0, str(submission_dir))

    from scenarios.security_arena.plugins import registry
    from plugin_badblueprint import PLUGIN_CLASS, SCENARIO_TYPE

    registry.register_scenario(SCENARIO_TYPE, PLUGIN_CLASS)


def main() -> None:
    _register_plugin()

    from scenarios.security_arena import orchestrator

    asyncio.run(orchestrator.main())


if __name__ == "__main__":
    main()
