#!/usr/bin/env python3
"""
Validate the structure of a strategy directory.
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
    return {"strategies_path": "./strategies"}


def validate_strategy(strategy_name, base_path=None):
    """
    Validate a strategy's structure.

    Args:
        strategy_name: Name of the strategy to validate
        base_path: Optional base path to search for strategies

    Returns:
        Dictionary with validation results
    """
    if base_path is None:
        config = load_config()
        strategies_rel_path = config.get("strategies_path", "./strategies")
        script_dir = Path(__file__).parent.parent
        strategies_path = (script_dir / strategies_rel_path).resolve()
    else:
        strategies_path = Path(base_path)

    strategy_path = strategies_path / strategy_name

    results = {
        "strategy_name": strategy_name,
        "exists": strategy_path.exists(),
        "is_directory": strategy_path.is_dir() if strategy_path.exists() else False,
        "has_readme": False,
        "optional_directories": {},
        "issues": [],
        "valid": True
    }

    if not results["exists"]:
        results["issues"].append(f"Strategy directory does not exist: {strategy_path}")
        results["valid"] = False
        return results

    if not results["is_directory"]:
        results["issues"].append(f"Path exists but is not a directory: {strategy_path}")
        results["valid"] = False
        return results

    # Check for required README.md
    readme_path = strategy_path / "README.md"
    results["has_readme"] = readme_path.exists()

    if not results["has_readme"]:
        results["issues"].append("Required README.md is missing")
        results["valid"] = False

    # Check for optional directories
    for dir_name in ["rules", "skills", "agents"]:
        dir_path = strategy_path / dir_name
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
    """Main function to validate a strategy"""
    if len(sys.argv) < 2:
        print("Usage: python validate_strategy.py <strategy-name>")
        sys.exit(1)

    strategy_name = sys.argv[1]
    results = validate_strategy(strategy_name)

    print(f"Validating strategy: {results['strategy_name']}\n")

    if results["valid"]:
        print("✅ Strategy structure is valid\n")
    else:
        print("❌ Strategy structure has issues\n")

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
