#!/usr/bin/env bash
# Fixture for commit eval 3: a CLEAN working tree — nothing to commit.
# Correct behaviour: report there is nothing to commit and STOP (no empty commit).
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
printf 'hello\n' > file.txt
git add -A
git commit -qm "chore: initial commit"
echo "Fixture ready: clean tree, nothing to commit. Baseline commit count: 1."
