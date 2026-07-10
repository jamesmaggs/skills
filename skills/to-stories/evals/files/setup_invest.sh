#!/usr/bin/env bash
# Fixture: the spec lumps a whole account system into one requirement. Nothing is
# built, no existing backlog. Correct behaviour: split the epic into several thin
# vertical-slice stories that each pass INVEST — NOT one giant "build the account
# system" story, and NOT horizontal layers (a UI story, an API story, a DB story).
set -euo pipefail

# Guard: only ever run in a throwaway directory. If we are inside a git work
# tree, this fixture would write files into the real repo — refuse.
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Refusing to run inside a git repository — run this fixture in an empty temp directory." >&2
  exit 1
fi

mkdir -p docs

cat > CLAUDE.md <<'MD'
# Portal

Customer portal.

## Issue tracker

Stories live in a **local markdown backlog** under `docs/backlog/`, one file per
story.
MD

cat > docs/spec.md <<'MD'
# Portal — product spec

## Capabilities

### A1 — Account system
The portal needs a complete customer account system: customers can register, log
in, log out, reset a forgotten password, edit their profile details, and an
administrator can view and deactivate customer accounts.
MD

echo "Fixture ready: spec.md (A1, one lumped account-system requirement), nothing built, docs/backlog/ empty."
