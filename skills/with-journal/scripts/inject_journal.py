#!/usr/bin/env python3
"""Inject work-journal instructions into a project's agent-instruction files.

Scans the project root for the agent-instruction files CLAUDE.md, AGENTS.md,
and GEMINI.md, and injects (or updates) a "## Journal" section in each one it
finds. The block tells the agent to keep a running journal under docs/journal/,
recording commands, outputs, hypotheses, dead-ends, and decisions — and never
secrets.

Idempotent, and safe for hand-edited files. The block is located by its
"## Journal" heading, which runs to the next level-1/2 heading (or end of
file). On re-run: an unchanged block (matching any version this skill has ever
generated, listed in KNOWN_BODIES) is refreshed to the current text; a block a
user has edited is left untouched and reported as `kept`.

Usage:  inject_journal.py [--root DIR] [--create FILE]
Exit:   0 = ran against at least one file; 1 = bad input (e.g. --root
        not a directory); 2 = argparse usage error; 3 = no agent-instruction
        file found and --create not given.

Stdlib only -- no network, no third-party packages.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

TARGETS = ["CLAUDE.md", "AGENTS.md", "GEMINI.md"]

HEADING = "## Journal"

BODY = """## Journal

Keep a running journal of your work in `docs/journal/`. It survives context
compaction and session boundaries. It is committed to the repository, so it
must never contain secrets.

At the start of a session, create `docs/journal/journal-NNNN.md`, where NNNN is
a zero-padded four-digit number one higher than the highest existing
`docs/journal/journal-*.md` (start at `0001` if none exist). Create
`docs/journal/` if it is missing.

Append an entry for every non-trivial action, as you do the work — not as a
summary at the end. Each entry includes:

- ISO timestamp (`YYYY-MM-DD HH:MM`)
- A one-line summary
- The exact command run, if any, and its actual output — never a paraphrase
- Files edited, and why
- Hypotheses, and whether they held up
- Dead-ends, and why they didn't work
- Links read during research
- Decisions made, and the reasoning behind them

Never write secrets to the journal: no credentials, API keys, tokens,
passwords, connection strings, or personal data. Redact them from command
output before recording (replace the value with `***`). If an entry would
require a secret, note that it was omitted and move on.

Be specific — record the real command and its real output, not "ran it, it
worked". Vague entries make the journal worthless.

Before starting new work, and after any context compaction, read the current
journal to orient yourself. If this is a fresh attempt at a task you have
tried before, skim the previous `docs/journal/journal-*.md` files too."""

# Every "## Journal" body this skill has ever generated, current one first.
# A block matching any of these is recognised as skill-generated and safe to
# refresh; anything else is treated as a user edit and left alone. Append the
# outgoing text here (never remove entries) whenever BODY changes.
KNOWN_BODIES = [
    BODY,
    BODY.replace(  # v0.2.0: plain integer journal numbering
        "create `docs/journal/journal-NNNN.md`, where NNNN is\n"
        "a zero-padded four-digit number one higher than the highest existing\n"
        "`docs/journal/journal-*.md` (start at `0001` if none exist).",
        "create `docs/journal/journal-N.md`, where N is one\n"
        "higher than the highest existing `docs/journal/journal-*.md` (start at 1 if\n"
        "none exist).",
    ),
]


def _section_span(lines: list[str]) -> tuple[int, int] | None:
    """Line span [start, end) of the '## Journal' section, or None if absent.

    The section runs from the heading line to the next level-1 or level-2
    heading, or to end of file."""
    start = next((i for i, ln in enumerate(lines) if ln.strip() == HEADING), None)
    if start is None:
        return None
    end = next(
        (j for j in range(start + 1, len(lines)) if re.match(r"#{1,2} ", lines[j])),
        len(lines),
    )
    return start, end


def _splice(pre: str, post: str) -> str:
    """Join `pre`, the current BODY, and `post` with tidy blank lines."""
    out = (pre + BODY).rstrip("\n")
    return out + ("\n\n" + post.lstrip("\n") if post.strip() else "\n")


def inject(path: Path) -> str:
    """Create/update the journal block in `path`. Returns the action taken."""
    if not path.exists():
        path.write_text(BODY + "\n", encoding="utf-8")
        return "created"

    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    span = _section_span(lines)

    if span is not None:
        start, end = span
        current = "".join(lines[start:end]).rstrip()
        if current == BODY.rstrip():
            return "unchanged"
        if current not in {b.rstrip() for b in KNOWN_BODIES}:
            return "kept"  # user-edited — do not clobber
        rebuilt = _splice("".join(lines[:start]), "".join(lines[end:]))
        path.write_text(rebuilt, encoding="utf-8")
        return "updated"

    # Append, leaving exactly one blank line before the block.
    path.write_text(text.rstrip("\n") + "\n\n" + BODY + "\n", encoding="utf-8")
    return "added"


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="inject_journal.py",
        description="Inject work-journal instructions into a project's agent-instruction files.",
    )
    p.add_argument("--root", default=".", metavar="DIR", help="Project root to scan (default: current directory)")
    p.add_argument(
        "--create",
        metavar="FILE",
        help="Inject into this file (create it if absent) — use when no agent-instruction file exists yet, e.g. AGENTS.md",
    )
    args = p.parse_args(argv)

    root = Path(args.root)
    if not root.is_dir():
        sys.exit(f"Error: --root '{args.root}' is not a directory.")

    if args.create:
        target = Path(args.create)
        if not target.is_absolute():
            target = root / target
        action = inject(target)
        print(f"{action}: {target}")
        return

    found = [root / name for name in TARGETS if (root / name).is_file()]
    if not found:
        print(
            "No agent-instruction file found (looked for "
            + ", ".join(TARGETS)
            + f") in {root}.\nAsk the user which to create, then re-run with --create <FILE>.",
            file=sys.stderr,
        )
        sys.exit(3)

    for path in found:
        action = inject(path)
        if action == "kept":
            print(f"kept (locally edited — left as is): {path}")
        else:
            print(f"{action}: {path}")


if __name__ == "__main__":
    main()
