#!/usr/bin/env python3
"""Inject work-journal instructions into a project's agent-instruction files.

Scans the project root for the agent-instruction files CLAUDE.md, AGENTS.md,
and GEMINI.md, and injects (or updates) a marker-wrapped "## Journal" section
in each one it finds. The block tells the agent to keep a running journal under
docs/journal/, recording commands, outputs, hypotheses, dead-ends, and
decisions — and never secrets.

Idempotent: the section is wrapped in HTML-comment markers, so re-running
updates the block in place rather than appending a duplicate.

Usage:  inject_journal.py [--root DIR] [--create FILE]
Exit:   0 = injected/updated at least one file; 1 = bad arguments;
        2 = no agent-instruction file found and --create not given.

Stdlib only -- no network, no third-party packages.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

TARGETS = ["CLAUDE.md", "AGENTS.md", "GEMINI.md"]

BEGIN = "<!-- BEGIN JOURNAL INSTRUCTIONS (managed by with-journal skill) -->"
END = "<!-- END JOURNAL INSTRUCTIONS -->"

BODY = """## Journal

Keep a running journal of your work in `docs/journal/`. It survives context
compaction and session boundaries. It is committed to the repository, so it
must never contain secrets.

At the start of a session, create `docs/journal/journal-N.md`, where N is one
higher than the highest existing `docs/journal/journal-*.md` (start at 1 if
none exist). Create `docs/journal/` if it is missing.

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

BLOCK = f"{BEGIN}\n{BODY}\n{END}"


def inject(path: Path) -> str:
    """Create/update the journal block in `path`. Returns the action taken."""
    if not path.exists():
        path.write_text(BLOCK + "\n")
        return "created"

    text = path.read_text()
    if BEGIN in text and END in text:
        pre = text[: text.index(BEGIN)]
        post = text[text.index(END) + len(END) :]
        updated = pre + BLOCK + post
        if updated == text:
            return "unchanged"
        path.write_text(updated)
        return "updated"

    # Append, leaving exactly one blank line before the block.
    path.write_text(text.rstrip("\n") + "\n\n" + BLOCK + "\n")
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
        raise SystemExit(2)

    for path in found:
        print(f"{inject(path)}: {path}")


if __name__ == "__main__":
    main()
