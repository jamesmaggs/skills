#!/usr/bin/env bash
# Fixture for commit eval 2: a rename that MUST stay together — a function
# renamed and all its call sites updated in lockstep.
# Correct behaviour: ONE commit (the call sites can't build without the rename).
set -euo pipefail
git init -q
git config user.email eval@example.com
git config user.name "Eval Fixture"
git config commit.gpgsign false
mkdir -p src
printf 'def fetch_user(id):\n    return {"id": id}\n' > src/users.py
printf 'from src.users import fetch_user\n\nprint(fetch_user(1))\n' > src/main.py
printf 'from src.users import fetch_user\n\nu = fetch_user(2)\n' > src/report.py
git add -A
git commit -qm "chore: initial commit"
# Rename fetch_user -> get_user across the definition and both call sites.
printf 'def get_user(id):\n    return {"id": id}\n' > src/users.py
printf 'from src.users import get_user\n\nprint(get_user(1))\n' > src/main.py
printf 'from src.users import get_user\n\nu = get_user(2)\n' > src/report.py
echo "Fixture ready: coupled rename across 3 files (must be ONE commit). Baseline commit count: 1."
