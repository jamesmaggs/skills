#!/bin/sh
# Sets up a repo with TWO unrelated working-tree changes: a logic fix in auth.py
# and an unrelated wording change in README.md. A good commit splits them.
set -e
git init -q
git config user.email eval@example.com
git config user.name Eval
printf 'def login(u, p):\n    return u == p\n' > auth.py
printf '# My Project\n\nA tool.\n' > README.md
git add auth.py README.md
git commit -qm "initial commit"
# Change 1: fix the auth logic (unrelated to docs).
printf 'def login(u, p):\n    return check_password(u, p)\n' > auth.py
# Change 2: reword the README (unrelated to auth).
printf '# My Project\n\nA fast, reliable tool for syncing files.\n' > README.md
