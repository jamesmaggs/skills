#!/usr/bin/env python3
"""Bump a skill's semantic version in skills/<name>/.claude-plugin/plugin.json.

Deterministic: reads the current MAJOR.MINOR.PATCH, increments the requested
part (resetting the lower parts), and writes it back, preserving the manifest's
key order and formatting.

Usage:
  python3 scripts/bump_version.py <skill-name> <major|minor|patch>

  major  breaking change to the skill's behaviour or output contract
  minor  new backward-compatible capability
  patch  fixes, wording, and other backward-compatible tweaks

Exit codes: 0 = success, 1 = errors, 2 = usage error / missing skill or manifest.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import NoReturn

ROOT = Path(__file__).resolve().parent.parent


def die(msg, code) -> NoReturn:
    print(msg, file=sys.stderr)
    sys.exit(code)


def main():
    ap = argparse.ArgumentParser(description="Bump a skill's semantic version.")
    ap.add_argument("name", help="skill name (directory under skills/)")
    ap.add_argument("part", choices=["major", "minor", "patch"])
    args = ap.parse_args()

    skill_dir = ROOT / "skills" / args.name
    manifest = skill_dir / ".claude-plugin" / "plugin.json"

    if not (skill_dir / "SKILL.md").exists():
        die(f"Error: no skill at skills/{args.name} (expected skills/{args.name}/SKILL.md).", 2)
    if not manifest.exists():
        die(f"Error: no manifest at {manifest}.\n"
            f"       Create it first: python3 scripts/register_plugin.py {args.name} \"<description>\"", 2)

    data = json.loads(manifest.read_text())
    current = str(data.get("version", ""))
    if not re.match(r"^\d+\.\d+\.\d+$", current):
        die(f'Error: current version "{current}" is not a MAJOR.MINOR.PATCH semver.', 1)

    maj, minor, patch = (int(x) for x in current.split("."))
    if args.part == "major":
        maj, minor, patch = maj + 1, 0, 0
    elif args.part == "minor":
        minor, patch = minor + 1, 0
    else:
        patch += 1
    new = f"{maj}.{minor}.{patch}"

    data["version"] = new
    # indent=2 + ensure_ascii=False + trailing newline matches the manifest's format.
    manifest.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"Bumped '{args.name}' ({args.part}): {current} -> {new}")


if __name__ == "__main__":
    main()
