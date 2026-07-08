#!/bin/sh
# Sets up a repo with a BREAKING change: a public function is renamed, so its
# call sites would break. A good commit marks this per Conventional Commits.
set -e
git init -q
git config user.email eval@example.com
git config user.name Eval
printf 'def get_user(id):\n    return db.find(id)\n' > api.py
git add api.py
git commit -qm "initial commit"
# Breaking change: rename the public function (callers must change).
printf 'def fetch_user(user_id):\n    return db.find(user_id)\n' > api.py
