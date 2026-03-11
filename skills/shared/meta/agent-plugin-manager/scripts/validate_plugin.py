#!/usr/bin/env python3
"""
Validate the structure and dependencies of a plugin directory.
"""

import json
import sys
from pathlib import Path

AGENT_TOOLS_ROOT = Path(__file__).resolve().parents[5]

VALID_DEPENDS_KEYS = {"skills", "agents", "rules", "hooks"}

DEP_PATH_MAP = {
    "skills": lambda name: AGENT_TOOLS_ROOT / "skills" / "shared" / name,
    "agents": lambda name: AGENT_TOOLS_ROOT / "agents" / "shared" / f"{name}.md",
    "rules": lambda name: AGENT_TOOLS_ROOT / "rules" / "shared" / f"{name}.md",
    "hooks": lambda name: AGENT_TOOLS_ROOT / "hooks" / "shared" / name,
}

DEP_DISPLAY_MAP = {
    "skills": lambda name: f"skills/shared/{name}/",
    "agents": lambda name: f"agents/shared/{name}.md",
    "rules": lambda name: f"rules/shared/{name}.md",
    "hooks": lambda name: f"hooks/shared/{name}",
}


def load_config():
    """
    Load configuration from config.local.json (if exists) or config.json.
    Local config takes precedence over default config.
    """
    script_dir = Path(__file__).parent.parent
    local_config_path = script_dir / "assets" / "config.local.json"
    config_path = script_dir / "assets" / "config.json"

    if local_config_path.exists():
        with open(local_config_path, "r") as f:
            return json.load(f)

    if config_path.exists():
        with open(config_path, "r") as f:
            return json.load(f)

    return {"plugins_path": "./plugins"}


def resolve_plugins_path(config):
    """Resolve plugins path from config."""
    plugins_rel = config.get("plugins_path", "./plugins")
    path = Path(plugins_rel)
    if not path.is_absolute():
        skill_root = Path(__file__).parent.parent
        path = (skill_root / path).resolve()
    return path


def validate_plugin(plugin_name, base_path=None):
    """
    Validate a plugin's structure and dependencies.

    Returns a dict with validation results.
    """
    if base_path is None:
        config = load_config()
        plugins_path = resolve_plugins_path(config)
    else:
        plugins_path = Path(base_path)

    plugin_path = plugins_path / plugin_name

    issues = []
    checks = {}
    deps = []

    # 1. Directory exists
    if not plugin_path.is_dir():
        issues.append(f"Plugin directory does not exist: {plugin_path}")
        return {
            "plugin_name": plugin_name,
            "valid": False,
            "issues": issues,
            "checks": {"directory": False},
            "deps": [],
        }
    checks["directory"] = True

    # 2-4. plugin.json
    plugin_json_path = plugin_path / "plugin.json"
    if not plugin_json_path.exists():
        checks["plugin_json"] = False
        issues.append("Required plugin.json is missing")
    else:
        try:
            with open(plugin_json_path, "r") as f:
                plugin_data = json.load(f)
        except (json.JSONDecodeError, ValueError) as e:
            checks["plugin_json"] = False
            issues.append(f"plugin.json is not valid JSON: {e}")
            plugin_data = None

        if plugin_data is not None:
            checks["plugin_json"] = True

            # 3. Required fields
            for field in ("name", "description", "depends"):
                if field not in plugin_data:
                    issues.append(f"plugin.json missing required field: {field}")
                    checks["plugin_json"] = False

            # 4. Validate depends structure
            depends = plugin_data.get("depends", {})
            if isinstance(depends, dict):
                unknown_keys = set(depends.keys()) - VALID_DEPENDS_KEYS
                for key in unknown_keys:
                    issues.append(f"plugin.json depends has unknown key: {key}")

                for key in VALID_DEPENDS_KEYS:
                    entries = depends.get(key, [])
                    if not isinstance(entries, list):
                        issues.append(f"depends.{key} must be an array")
                        continue
                    for entry in entries:
                        if not isinstance(entry, str):
                            issues.append(
                                f"depends.{key} contains non-string value: {entry}"
                            )
                            continue

                        # 6. Resolve dependency path
                        resolver = DEP_PATH_MAP[key]
                        resolved = resolver(entry)
                        exists = resolved.exists()
                        display = DEP_DISPLAY_MAP[key](entry)
                        deps.append(
                            {
                                "category": key,
                                "name": entry,
                                "display": display,
                                "exists": exists,
                            }
                        )
                        if not exists:
                            issues.append(f"Dependency not found: {display}")
            elif depends is not None:
                issues.append("plugin.json depends must be an object")

    # 5. README.md
    readme_path = plugin_path / "README.md"
    checks["readme"] = readme_path.exists()
    if not checks["readme"]:
        issues.append("Required README.md is missing")

    # 7. Optional settings.json
    settings_path = plugin_path / "settings.json"
    if settings_path.exists():
        try:
            with open(settings_path, "r") as f:
                json.load(f)
            checks["settings_json"] = True
        except (json.JSONDecodeError, ValueError) as e:
            checks["settings_json"] = False
            issues.append(f"settings.json is not valid JSON: {e}")
    else:
        checks["settings_json"] = None  # not present

    return {
        "plugin_name": plugin_name,
        "valid": len(issues) == 0,
        "issues": issues,
        "checks": checks,
        "deps": deps,
    }


def main():
    """Main function to validate a plugin."""
    if len(sys.argv) < 2:
        print("Usage: python validate_plugin.py <plugin-name>")
        sys.exit(1)

    plugin_name = sys.argv[1]
    results = validate_plugin(plugin_name)

    checks = results["checks"]
    deps = results["deps"]

    print(f"Validating plugin: {results['plugin_name']}\n")

    if results["valid"]:
        print("✅ Plugin structure is valid\n")
    else:
        print("❌ Plugin structure has issues\n")

    # File/directory checks
    def _mark(val):
        if val is True:
            return "✓"
        elif val is False:
            return "✗"
        return "— (not present)"

    print(f"Directory exists: {_mark(checks.get('directory'))}")
    if checks.get("directory"):
        print(f"plugin.json: {_mark(checks.get('plugin_json'))}")
        print(f"README.md: {_mark(checks.get('readme'))}")
        settings_val = checks.get("settings_json")
        print(f"settings.json: {_mark(settings_val)}")

    # Dependencies
    if deps:
        print(f"\nDependencies ({len(deps)} total):")
        for dep in deps:
            label = f"{dep['category']}/{dep['name']}"
            if dep["exists"]:
                print(f"  {label}: ✓ ({dep['display']})")
            else:
                print(f"  {label}: ✗ (not found: {dep['display']})")

    # Issues summary (for items not already covered above)
    non_dep_issues = [i for i in results["issues"] if not i.startswith("Dependency not found:")]
    if non_dep_issues and not results["valid"]:
        print("\nIssues:")
        for issue in non_dep_issues:
            print(f"  - {issue}")

    sys.exit(0 if results["valid"] else 1)


if __name__ == "__main__":
    main()
