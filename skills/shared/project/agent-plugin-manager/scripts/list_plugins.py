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
            readme_path = item / "README.md"

            plugin_info = {
                "name": item.name,
                "path": str(item),
                "has_readme": readme_path.exists(),
                "directories": []
            }

            # Check for optional directories
            for dir_name in ["rules", "skills", "agents"]:
                dir_path = item / dir_name
                if dir_path.exists() and dir_path.is_dir():
                    plugin_info["directories"].append(dir_name)

            plugins.append(plugin_info)

    return sorted(plugins, key=lambda x: x["name"])


def main():
    """Main function to list plugins"""
    plugins = list_plugins()

    if not plugins:
        print("No plugins found.")
        return

    print(f"Found {len(plugins)} plugin(s):\n")

    for plugin in plugins:
        print(f"📁 {plugin['name']}")
        print(f"   Path: {plugin['path']}")
        print(f"   README: {'✓' if plugin['has_readme'] else '✗'}")
        if plugin['directories']:
            print(f"   Contains: {', '.join(plugin['directories'])}")
        print()


if __name__ == "__main__":
    main()
