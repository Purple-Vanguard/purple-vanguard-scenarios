#!/usr/bin/env python3
"""Launch the AgentBeats orchestrator with the badblueprint plugin registered."""

from __future__ import annotations

import asyncio
import importlib
import importlib.util
import sys
from pathlib import Path


def _register_plugin() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    vendor_root = repo_root / "vendor" / "agentbeats-lambda"
    submission_dir = repo_root / "submissions" / "purple_vanguard" / "badblueprint"

    sys.path.insert(0, str(vendor_root))
    sys.path.insert(0, str(submission_dir))

    from agentbeats import tool_provider
    from scenarios.security_arena.plugins import registry

    plugin_module_name = (
        "plugin"
        if importlib.util.find_spec("plugin") is not None
        else "plugin_badblueprint"
    )
    plugin_module = importlib.import_module(plugin_module_name)
    plugin_class = getattr(plugin_module, "PLUGIN_CLASS")
    scenario_type = getattr(plugin_module, "SCENARIO_TYPE")

    registry.register_scenario(scenario_type, plugin_class)

    original_talk = tool_provider.ToolProvider.talk_to_agent

    async def safe_talk_to_agent(self, message: str, url: str, new_conversation: bool = False):
        try:
            return await original_talk(self, message, url, new_conversation=new_conversation)
        except Exception as exc:
            if "terminal state" in str(exc).lower():
                self._context_ids.pop(url, None)
                return await original_talk(self, message, url, new_conversation=True)
            raise

    tool_provider.ToolProvider.talk_to_agent = safe_talk_to_agent


def main() -> None:
    _register_plugin()

    from scenarios.security_arena import orchestrator

    asyncio.run(orchestrator.main())


if __name__ == "__main__":
    main()
