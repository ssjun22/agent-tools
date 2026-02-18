#!/usr/bin/env python3
"""
List all strategies in the strategies directory.
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
    return {"strategies_path": "./strategies"}


def list_strategies(base_path=None):
    """
    List all strategies in the strategies directory.

    Args:
        base_path: Optional base path to search for strategies.
                   If None, uses config.json or default ./strategies

    Returns:
        List of strategy information dictionaries
    """
    if base_path is None:
        config = load_config()
        strategies_rel_path = config.get("strategies_path", "./strategies")
        script_dir = Path(__file__).parent.parent
        strategies_path = (script_dir / strategies_rel_path).resolve()
    else:
        strategies_path = Path(base_path)

    if not strategies_path.exists():
        return []

    strategies = []

    for item in strategies_path.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            readme_path = item / "README.md"

            strategy_info = {
                "name": item.name,
                "path": str(item),
                "has_readme": readme_path.exists(),
                "directories": []
            }

            # Check for optional directories
            for dir_name in ["rules", "skills", "agents"]:
                dir_path = item / dir_name
                if dir_path.exists() and dir_path.is_dir():
                    strategy_info["directories"].append(dir_name)

            strategies.append(strategy_info)

    return sorted(strategies, key=lambda x: x["name"])


def main():
    """Main function to list strategies"""
    strategies = list_strategies()

    if not strategies:
        print("No strategies found.")
        return

    print(f"Found {len(strategies)} strategy/strategies:\n")

    for strategy in strategies:
        print(f"📁 {strategy['name']}")
        print(f"   Path: {strategy['path']}")
        print(f"   README: {'✓' if strategy['has_readme'] else '✗'}")
        if strategy['directories']:
            print(f"   Contains: {', '.join(strategy['directories'])}")
        print()


if __name__ == "__main__":
    main()
