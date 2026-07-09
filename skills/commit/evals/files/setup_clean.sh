#!/usr/bin/env bash
# Fixture for commit eval 3: a CLEAN working tree — nothing to commit.
# Correct behaviour: report there is nothing to commit and STOP (no empty commit).
set -euo pipefail
git init -q
git config user.email eval@example.com
git config user.name "Eval Fixture"
git config commit.gpgsign false
printf 'hello\n' > file.txt
git add -A
git commit -qm "chore: initial commit"
echo "Fixture ready: clean tree, nothing to commit. Baseline commit count: 1."
