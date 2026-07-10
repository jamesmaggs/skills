#!/usr/bin/env bash
# Fixture for commit eval 1: TWO UNRELATED uncommitted changes.
# Correct behaviour: two separate atomic commits (a fix: and a docs:).
set -euo pipefail

# Guard: only ever run in a throwaway directory. If we are inside a git work
# tree, this fixture would mutate the real repo (config, files) — refuse.
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Refusing to run inside a git repository — run this fixture in an empty temp directory." >&2
  exit 1
fi
git init -q
git config user.email eval@example.com
git config user.name "Eval Fixture"
git config commit.gpgsign false
mkdir -p src
printf 'def parse(x):\n    return x.strip()\n' > src/parser.py
printf '# Widget\n\nA small tool.\n' > README.md
git add -A
git commit -qm "chore: initial commit"
# Change 1 — a bug fix: guard against None in the parser.
printf 'def parse(x):\n    if x is None:\n        return ""\n    return x.strip()\n' > src/parser.py
# Change 2 — an unrelated wording tweak in the README.
printf '# Widget\n\nA small, fast tool.\n' > README.md
echo "Fixture ready: 2 unrelated changes (src/parser.py fix + README.md docs). Baseline commit count: 1."
