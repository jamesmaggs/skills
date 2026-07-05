#!/usr/bin/env python3
"""Validate a skill's eval spec (evals/triggering.csv + evals/outcome.json).

Deterministic — used by the authoring flow to check a freshly written spec.

Usage: python3 validate_spec.py --skill <skill-dir>
Exit: 0 = clean (warnings allowed), 1 = errors, 2 = usage/missing skill.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from spec import validate  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description="Validate a skill's eval spec.")
    ap.add_argument("--skill", required=True, help="Path to the skill directory")
    args = ap.parse_args()

    skill = Path(args.skill)
    if not (skill / "SKILL.md").exists():
        print(f"Error: no SKILL.md at {skill}", file=sys.stderr)
        sys.exit(2)

    errors, warnings = validate(skill)
    for w in warnings:
        print(f"  [warn]  {w}")
    for e in errors:
        print(f"  [ERROR] {e}")
    if errors:
        print(f"\nFAIL: {len(errors)} error(s), {len(warnings)} warning(s).")
        sys.exit(1)
    print(f"\nOK: 0 errors, {len(warnings)} warning(s).")
    sys.exit(0)


if __name__ == "__main__":
    main()
