#!/usr/bin/env bash
# Fixture: a project that already has agent-instruction files.
# Correct behaviour: inject the journal block into both, preserving content.
set -euo pipefail

# Guard: only ever run in a throwaway directory. If we are inside a git work
# tree, this fixture would write files into the real repo — refuse.
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Refusing to run inside a git repository — run this fixture in an empty temp directory." >&2
  exit 1
fi
printf '# Acme App\n\nBuild with `make`. Run the tests with `make test`.\n' > CLAUDE.md
printf '# Agent guide\n\nUse pnpm. Prefer small PRs.\n' > AGENTS.md
echo "Fixture ready: CLAUDE.md + AGENTS.md present, no journal block yet."
