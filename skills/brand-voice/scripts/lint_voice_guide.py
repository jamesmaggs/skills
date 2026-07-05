#!/usr/bin/env python3
"""Deterministic checker for a finished brand voice guide.

Enforces the fixed output contract that downstream design tools and AI agents
rely on, so the schema is guaranteed rather than merely promised by the prose
instructions.

Usage:
  python3 lint_voice_guide.py path/to/brand-voice-guide.md

Exit codes:
  0 = clean (warnings allowed)
  1 = one or more errors
  2 = file unreadable / no argument
"""
from __future__ import annotations

import re
import sys

# The four dimensions and their pole words (left / right).
DIMS = [
    ("Funny ↔ Serious", "funny", "serious"),
    ("Formal ↔ Casual", "formal", "casual"),
    ("Respectful ↔ Irreverent", "respectful", "irreverent"),
    ("Enthusiastic ↔ Matter-of-fact", "enthusiastic", "matter-of-fact"),
]
DIM_NAMES = {d[0] for d in DIMS}
SAMPLE_LABELS = ["Error message", "Marketing line", "Support reply", "Onboarding email opener"]
CHART_COLS = ["Trait", "Description", "Do's", "Don'ts"]
REQUIRED_SECTIONS = ["Tone of Voice Dimensions", "Brand Voice Chart", "Sample Copy"]


def parse_row(line):
    """Split '| a | b |' into ['a', 'b'] (drop the leading/trailing empties)."""
    return [c.strip() for c in line.split("|")[1:-1]]


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 lint_voice_guide.py path/to/brand-voice-guide.md")
        sys.exit(2)
    path = sys.argv[1]
    try:
        with open(path, "r", errors="replace") as f:
            text = f.read()
    except OSError:
        print(f"Could not read file: {path}")
        sys.exit(2)

    # Normalise the U+2192 arrow (→) to "->" so parsing stays simple.
    lines = text.replace("→", "->").splitlines()

    errors, warnings = [], []
    has_h1 = False
    voiceseen = False
    secseen = set()
    rows = {}          # section -> list of captured table rows (first table only)
    tabledone = set()  # sections whose first table has ended
    sample_lines = []
    sec = ""

    for nr, line in enumerate(lines, start=1):
        if re.match(r"^#[ \t]+Brand Voice Guide:", line):
            has_h1 = True

        # Unfilled template placeholders [..], skipping markdown links "](".
        for m in re.finditer(r"\[[^\]]+\]", line):
            after = line[m.end():m.end() + 1]
            if after != "(":
                errors.append(f"Line {nr}: unfilled template placeholder {m.group(0)}")

        # Section heading (## but not ###).
        if re.match(r"^##[ \t]", line) and not line.startswith("###"):
            sec = line[2:].strip()
            secseen.add(sec)
            if sec.startswith("The Voice"):
                voiceseen = True
            continue

        # Capture the first table per section.
        if sec and re.match(r"^[ \t]*\|", line) and sec not in tabledone:
            rows.setdefault(sec, []).append(line)
        elif sec and re.match(r"^[ \t]*$", line) and rows.get(sec) and sec not in tabledone:
            tabledone.add(sec)

        if sec == "Sample Copy":
            sample_lines.append(line)

    def load_table(section):
        rc = rows.get(section, [])
        if not rc:
            return []
        start = 1  # skip the header row
        if len(rc) >= 2 and re.sub(r"[ \t|:\-]", "", rc[1]) == "":
            start = 2  # also skip the |---| separator row
        return rc[start:]

    # --- required structure ---
    if not has_h1:
        errors.append('Missing H1 heading "# Brand Voice Guide: <name>".')
    if not voiceseen:
        errors.append('Missing required section "## The Voice: <label>".')
    for req in REQUIRED_SECTIONS:
        if req not in secseen:
            errors.append(f'Missing required section "## {req}".')

    # --- Dimensions ---
    found = {}
    for row in load_table("Tone of Voice Dimensions"):
        c = parse_row(row)
        if len(c) >= 1:
            found[c[0]] = {
                "score": c[1] if len(c) >= 2 else "",
                "pos": c[2] if len(c) >= 3 else "",
                "rat": c[3] if len(c) >= 4 else "",
            }
    defaults = {}
    for name, lp, rp in DIMS:
        if name not in found:
            errors.append(f'Dimensions table is missing the row "{name}".')
            continue
        s = found[name]["score"]
        if not re.match(r"^[1-5]$", s):
            errors.append(f'"{name}": Score must be an integer 1-5, got "{s}".')
            continue
        sv = int(s)
        defaults[name] = sv
        dp = found[name]["pos"]
        pos = dp.lower()
        if dp == "":
            errors.append(f'"{name}": Position cell is empty.')
        elif sv <= 2 and lp not in pos:
            errors.append(f'"{name}": Score {sv} (toward "{lp}") but Position "{dp}" doesn\'t name that pole.')
        elif sv == 3 and "balanced" not in pos:
            errors.append(f'"{name}": Score 3 should be described "balanced"; Position is "{dp}".')
        elif sv >= 4 and rp not in pos:
            errors.append(f'"{name}": Score {sv} (toward "{rp}") but Position "{dp}" doesn\'t name that pole.')
        if found[name]["rat"] == "":
            errors.append(f'"{name}": Rationale cell is empty.')

    # --- Brand Voice Chart ---
    chart = load_table("Brand Voice Chart")
    if len(chart) < 3 or len(chart) > 5:
        errors.append(f"Brand Voice Chart must have 3-5 trait rows, found {len(chart)}.")
    for row in chart:
        c = parse_row(row)
        if len(c) < 4:
            errors.append(f"Brand Voice Chart row has fewer than 4 columns: {row}")
            continue
        tr = c[0] if c[0] else "(unnamed)"
        for j in range(4):
            if c[j] == "":
                errors.append(f'Brand Voice Chart row "{tr}": empty {CHART_COLS[j]} cell.')

    # --- Tone Shifts (optional) ---
    if "Tone Shifts by Context" in secseen:
        ts = load_table("Tone Shifts by Context")
        if not ts:
            warnings.append("Tone Shifts by Context section present but has no rows; omit it or fill it.")
        for row in ts:
            c = parse_row(row)
            if len(c) < 2:
                errors.append(f"Tone shift row malformed: {row}")
                continue
            ctx, shift = c[0], c[1]
            if shift.lower().startswith("no score change"):
                continue
            if re.match(r"^.+:[ \t]*[0-9]+[ \t]*->[ \t]*[0-9]+", shift):
                colon = shift.index(":")
                dim = shift[:colon].strip()
                rest = shift[colon + 1:]
                ap = rest.index("->")
                fromnum = int(rest[:ap].strip())
                tonum = int(re.search(r"[0-9]+", rest[ap + 2:]).group())
                if dim not in DIM_NAMES:
                    errors.append(f'Tone shift for "{ctx}" names unknown dimension "{dim}".')
                elif dim in defaults and fromnum != defaults[dim]:
                    errors.append(f'Tone shift for "{ctx}": "{dim}" default is {defaults[dim]} but shift starts from {fromnum}.')
                if tonum < 1 or tonum > 5:
                    errors.append(f'Tone shift for "{ctx}": shifted score {tonum} out of range 1-5.')
            else:
                errors.append(f'Tone shift for "{ctx}" must be "Dimension: default -> shifted" or "No score change"; got "{shift}".')

    # --- Sample Copy ---
    present = [False] * 4
    satisfied = [False] * 4
    pending = -1
    for l in sample_lines:
        for k, label in enumerate(SAMPLE_LABELS):
            if re.search(r"\*\*" + re.escape(label) + r":?\*\*", l):
                present[k] = True
                pending = k
        if re.match(r"^[ \t]*>", l) and pending >= 0:
            satisfied[pending] = True
    for k, label in enumerate(SAMPLE_LABELS):
        if not present[k]:
            errors.append(f'Sample Copy is missing the "{label}" sample.')
        elif not satisfied[k]:
            errors.append(f'Sample "{label}" has no blockquote (>) with the actual copy.')

    for w in warnings:
        print(f"  [warn] {w}")
    for e in errors:
        print(f"  [ERROR] {e}")
    if errors:
        print(f"\nFAIL: {len(errors)} error(s), {len(warnings)} warning(s).")
        sys.exit(1)
    print(f"\nCLEAN: 0 errors, {len(warnings)} warning(s).")
    sys.exit(0)


if __name__ == "__main__":
    main()
