---
name: with-journal
description: Injects work-journal instructions into a project's agent-instruction files so the agent keeps a persistent journal in docs/journal.
disable-model-invocation: true
---

# With Journal

Injects a marker-wrapped `## Journal` section into the project's
agent-instruction files so the agent keeps a running, on-disk work journal
under `docs/journal/`. Journals are committed and must never contain secrets.

**Run the script to inject the block. It is idempotent — re-running updates
the block in place rather than duplicating it.**

## Requirements

Python 3 standard library only — no third-party packages, no Node.

## Usage

```bash
python3 scripts/inject_journal.py [--root DIR] [--create FILE]
```

| Flag | Default | Meaning |
|---|---|---|
| `--root` | *(current dir)* | Project root to scan for agent-instruction files. |
| `--create` | *(none)* | Inject into this specific file, creating it if absent. Use only after the user picks a file to create. |

## Workflow

1. Run `python3 scripts/inject_journal.py` from the project root. It injects
   the journal block into every `CLAUDE.md`, `AGENTS.md`, and `GEMINI.md` it
   finds, and prints the action taken per file (`created`/`updated`/`added`/
   `unchanged`).
2. If it exits reporting no agent-instruction file found, ask the user which
   file to create — `AGENTS.md` is the portable, cross-agent default — then run
   `python3 scripts/inject_journal.py --create <FILE>`.
3. Tell the user the journal is set up, and that `docs/journal/` will be
   created by the agent on its next session. Do not create journal files
   yourself here — the injected instructions drive that during real work.
