#!/usr/bin/env bash
# Fixture: a project with NO agent-instruction file.
# Correct behaviour: the skill reports none found and asks which to create.
set -euo pipefail
printf '# Acme App\n\nA small service.\n' > README.md
echo "Fixture ready: no CLAUDE.md / AGENTS.md / GEMINI.md present."
