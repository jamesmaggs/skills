"""Shared helpers for the marketplace scripts (register_plugin, bump_version)."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import NoReturn

# Repo root (this file lives in scripts/).
ROOT = Path(__file__).resolve().parent.parent


def die(msg, code) -> NoReturn:
    print(msg, file=sys.stderr)
    sys.exit(code)


def read_json(path):
    """Parse JSON at path, or die(1) with a clean message if it is malformed."""
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as e:
        die(f"Error: {path} is not valid JSON: {e}", 1)


def write_json(path, obj):
    # indent=2 + ensure_ascii=False + trailing newline matches jq's output.
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")
