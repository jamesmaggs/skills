#!/usr/bin/env bash
# Fixture: a project that already has agent-instruction files.
# Correct behaviour: inject the journal block into both, preserving content.
set -euo pipefail
printf '# Acme App\n\nBuild with `make`. Run the tests with `make test`.\n' > CLAUDE.md
printf '# Agent guide\n\nUse pnpm. Prefer small PRs.\n' > AGENTS.md
echo "Fixture ready: CLAUDE.md + AGENTS.md present, no journal block yet."
