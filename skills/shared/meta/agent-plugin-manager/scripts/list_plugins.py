#!/usr/bin/env python3
"""
List all plugins in the plugins directory.
"""

import json
import os
from pathlib import Path


def load_config():
    """
    Load configuration from config.local.json (if exists) or config.json.
    Local config takes precedence over default config.
    """
    script_dir = Path(__file__).parent.parent
    local_config_path = script_dir / "assets" / "config.local.json"
    config_path = script_dir / "assets" / "config.json"

    # Try local config first
    if local_config_path.exists():
        with open(local_config_path, 'r') as f:
            return json.load(f)

    # Fall back to default config
    if config_path.exists():
        with open(config_path, 'r') as f:
            return json.load(f)

    # Default configuration
    return {"plugins_path": "./plugins"}


def read_plugin_json(plugin_dir: Path) -> dict | None:
    """Read plugin.json from a plugin directory, returning None if missing."""
    plugin_json_path = plugin_dir / "plugin.json"
    if not plugin_json_path.exists():
        return None
    with open(plugin_json_path, 'r') as f:
        return json.load(f)


def count_dependencies(plugin_json: dict) -> dict[str, int]:
    """Count dependency items per type from plugin.json's depends block."""
    counts = {}
    depends = plugin_json.get("depends", {})
    if not isinstance(depends, dict):
        return counts

    for key, value in depends.items():
        if isinstance(value, list) and len(value) > 0:
            counts[key] = len(value)

    return counts


def list_plugins(base_path=None):
    """
    List all plugins in the plugins directory.

    Args:
        base_path: Optional base path to search for plugins.
                   If None, uses config.json or default ./plugins

    Returns:
        List of plugin information dictionaries
    """
    if base_path is None:
        config = load_config()
        plugins_rel_path = config.get("plugins_path", "./plugins")
        script_dir = Path(__file__).parent.parent
        plugins_path = (script_dir / plugins_rel_path).resolve()
    else:
        plugins_path = Path(base_path)

    if not plugins_path.exists():
        return []

    plugins = []

    for item in plugins_path.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            plugin_json = read_plugin_json(item)

            plugin_info = {
                "name": item.name,
                "path": str(item),
                "has_readme": (item / "README.md").exists(),
                "has_plugin_json": plugin_json is not None,
                "has_settings": (item / "settings.json").exists(),
                "dependencies": count_dependencies(plugin_json) if plugin_json else {},
            }

            plugins.append(plugin_info)

    return sorted(plugins, key=lambda x: x["name"])


def format_status(flag: bool) -> str:
    return "\u2713" if flag else "\u2717"


def format_dependencies(deps: dict[str, int]) -> str:
    if not deps:
        return ""
    parts = [f"{count} {key}" for key, count in deps.items()]
    return ", ".join(parts)


def main():
    """Main function to list plugins."""
    plugins = list_plugins()

    if not plugins:
        print("No plugins found.")
        return

    print(f"Found {len(plugins)} plugin(s):\n")

    for plugin in plugins:
        print(f"\U0001f4c1 {plugin['name']}")
        print(f"   Path: {plugin['path']}")
        print(
            f"   README: {format_status(plugin['has_readme'])}  "
            f"plugin.json: {format_status(plugin['has_plugin_json'])}  "
            f"settings: {format_status(plugin['has_settings'])}"
        )
        deps_str = format_dependencies(plugin["dependencies"])
        if deps_str:
            print(f"   Depends: {deps_str}")
        print()


if __name__ == "__main__":
    main()
