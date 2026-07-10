---
name: with-journal
description: Injects work-journal instructions into a project's agent-instruction files so the agent keeps a persistent journal in docs/journal.
disable-model-invocation: true
---

# With Journal

Runs a script that injects an idempotent `## Journal` block into the project's
agent-instruction files, so the agent keeps an on-disk work journal under
`docs/journal/`.

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
   the block into every `CLAUDE.md`, `AGENTS.md`, and `GEMINI.md` it finds and
   prints the action per file (`created`/`added`/`updated`/`unchanged`/`kept`);
   re-running is safe. `kept` means the file's `## Journal` section was edited
   locally and was left untouched.
2. If it reports no agent-instruction file found, ask the user which file to
   create — `AGENTS.md` is the portable, cross-agent default — then run
   `python3 scripts/inject_journal.py --create <FILE>`.
3. Confirm setup and stop. `docs/journal/` and the journal files are created
   later by the agent during real work, driven by the injected block — not by
   this skill.
