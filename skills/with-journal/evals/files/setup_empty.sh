#!/usr/bin/env bash
# Fixture: a project with NO agent-instruction file.
# Correct behaviour: the skill reports none found and asks which to create.
set -euo pipefail

# Guard: only ever run in a throwaway directory. If we are inside a git work
# tree, this fixture would write files into the real repo — refuse.
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Refusing to run inside a git repository — run this fixture in an empty temp directory." >&2
  exit 1
fi
printf '# Acme App\n\nA small service.\n' > README.md
echo "Fixture ready: no CLAUDE.md / AGENTS.md / GEMINI.md present."
