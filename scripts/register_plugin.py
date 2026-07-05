#!/usr/bin/env python3
"""Wire a skill into the plugin marketplace.

Writes the skill's skills/<name>/.claude-plugin/plugin.json manifest and upserts
the matching entry in .claude-plugin/marketplace.json. Deterministic and
idempotent — re-running with the same inputs leaves both files byte-identical,
and the marketplace entries are always sorted by name.

Usage:
  python3 scripts/register_plugin.py <skill-name> ["<description>"]

The description is the short, human-facing summary shown in the marketplace
(distinct from the model-facing SKILL.md description). If omitted, the current
plugin.json's description is reused, so the command doubles as a re-sync.

Exit codes: 0 = success, 1 = errors, 2 = usage error / missing skill.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Repo-wide manifest constants.
AUTHOR_NAME = "James Maggs"
LICENSE = "MIT"
REPOSITORY = "https://github.com/jamesmaggs/software-factory"
DEFAULT_VERSION = "0.1.0"

ROOT = Path(__file__).resolve().parent.parent
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"


def die(msg, code):
    print(msg, file=sys.stderr)
    sys.exit(code)


def write_json(path, obj):
    # indent=2 + ensure_ascii=False + trailing newline matches jq's output.
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


def main():
    ap = argparse.ArgumentParser(description="Wire a skill into the plugin marketplace.")
    ap.add_argument("name", help="skill name (directory under skills/)")
    ap.add_argument("description", nargs="?", help="short marketplace summary (reused from the manifest if omitted)")
    args = ap.parse_args()

    name = args.name
    skill_dir = ROOT / "skills" / name
    manifest = skill_dir / ".claude-plugin" / "plugin.json"

    if not (skill_dir / "SKILL.md").exists():
        die(f"Error: no skill at skills/{name} (expected skills/{name}/SKILL.md).", 2)
    if not MARKETPLACE.exists():
        die(f"Error: marketplace file not found: {MARKETPLACE}", 1)

    # Resolve the description: explicit argument wins; otherwise reuse the manifest's.
    if args.description is not None:
        desc = args.description
    elif manifest.exists():
        desc = json.loads(manifest.read_text()).get("description", "")
    else:
        die(f"Error: no description given and no existing manifest to reuse.\n"
            f"       Pass one: python3 scripts/register_plugin.py {name} \"<description>\"", 2)
    if not desc:
        die("Error: description must not be empty.", 2)

    # Preserve an existing manifest version; new manifests start at the default.
    version = DEFAULT_VERSION
    if manifest.exists():
        version = json.loads(manifest.read_text()).get("version", DEFAULT_VERSION)

    manifest.parent.mkdir(parents=True, exist_ok=True)
    write_json(manifest, {
        "name": name,
        "description": desc,
        "version": version,
        "author": {"name": AUTHOR_NAME},
        "license": LICENSE,
        "repository": REPOSITORY,
    })

    # Upsert the marketplace entry, then sort all entries by name.
    data = json.loads(MARKETPLACE.read_text())
    plugins = [p for p in data.get("plugins", []) if p.get("name") != name]
    plugins.append({"name": name, "source": f"./skills/{name}", "description": desc})
    data["plugins"] = sorted(plugins, key=lambda p: p["name"])
    write_json(MARKETPLACE, data)

    print(f"Registered '{name}' -> {manifest} and {MARKETPLACE}")


if __name__ == "__main__":
    main()
