#!/usr/bin/env python3
"""
Validate the structure of a plugin directory.
"""

import json
import sys
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


def validate_plugin(plugin_name, base_path=None):
    """
    Validate a plugin's structure.

    Args:
        plugin_name: Name of the plugin to validate
        base_path: Optional base path to search for plugins

    Returns:
        Dictionary with validation results
    """
    if base_path is None:
        config = load_config()
        plugins_rel_path = config.get("plugins_path", "./plugins")
        script_dir = Path(__file__).parent.parent
        plugins_path = (script_dir / plugins_rel_path).resolve()
    else:
        plugins_path = Path(base_path)

    plugin_path = plugins_path / plugin_name

    results = {
        "plugin_name": plugin_name,
        "exists": plugin_path.exists(),
        "is_directory": plugin_path.is_dir() if plugin_path.exists() else False,
        "has_readme": False,
        "optional_directories": {},
        "issues": [],
        "valid": True
    }

    if not results["exists"]:
        results["issues"].append(f"Plugin directory does not exist: {plugin_path}")
        results["valid"] = False
        return results

    if not results["is_directory"]:
        results["issues"].append(f"Path exists but is not a directory: {plugin_path}")
        results["valid"] = False
        return results

    # Check for required README.md
    readme_path = plugin_path / "README.md"
    results["has_readme"] = readme_path.exists()

    if not results["has_readme"]:
        results["issues"].append("Required README.md is missing")
        results["valid"] = False

    # Check for optional directories
    for dir_name in ["rules", "skills", "agents"]:
        dir_path = plugin_path / dir_name
        if dir_path.exists():
            if dir_path.is_dir():
                # Check if directory has any files
                files = list(dir_path.glob("*"))
                results["optional_directories"][dir_name] = {
                    "exists": True,
                    "file_count": len(files)
                }
            else:
                results["issues"].append(f"{dir_name} exists but is not a directory")
                results["valid"] = False

    return results


def main():
    """Main function to validate a plugin"""
    if len(sys.argv) < 2:
        print("Usage: python validate_plugin.py <plugin-name>")
        sys.exit(1)

    plugin_name = sys.argv[1]
    results = validate_plugin(plugin_name)

    print(f"Validating plugin: {results['plugin_name']}\n")

    if results["valid"]:
        print("✅ Plugin structure is valid\n")
    else:
        print("❌ Plugin structure has issues\n")

    print(f"Directory exists: {'✓' if results['exists'] else '✗'}")
    print(f"Is directory: {'✓' if results['is_directory'] else '✗'}")
    print(f"README.md: {'✓' if results['has_readme'] else '✗'}")

    if results["optional_directories"]:
        print("\nOptional directories:")
        for dir_name, info in results["optional_directories"].items():
            print(f"  {dir_name}/: {info['file_count']} file(s)")

    if results["issues"]:
        print("\nIssues found:")
        for issue in results["issues"]:
            print(f"  • {issue}")

    sys.exit(0 if results["valid"] else 1)


if __name__ == "__main__":
    main()
