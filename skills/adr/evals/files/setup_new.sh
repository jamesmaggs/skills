#!/usr/bin/env bash
# Fixture: a plain project with NO ADR directory yet.
# Used by the "new ADR" eval (must create docs/adr/0001-*.md + index) and the
# "decline a trivial decision" eval (must write nothing).
set -euo pipefail

# Guard: only ever run in a throwaway directory. If we are inside a git work
# tree, this fixture would write files into the real repo — refuse.
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Refusing to run inside a git repository — run this fixture in an empty temp directory." >&2
  exit 1
fi
printf '# Billing Service\n\nA small service that issues invoices.\n' > README.md
echo "Fixture ready: plain project, no ADR directory present."
