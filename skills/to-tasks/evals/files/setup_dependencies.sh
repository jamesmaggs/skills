#!/usr/bin/env bash
# Fixture: a story whose behaviours share a foundation — archived state must be
# persisted before it can be hidden from the active list or restored. Correct
# behaviour: decompose into tasks and record the genuine dependency explicitly
# (a populated "Depends on:" on the dependent tasks), never leave it implicit.
# A fully-independent vertical-slice decomposition is also acceptable if each
# slice truly stands alone.
set -euo pipefail

# Guard: only ever run in a throwaway directory. If we are inside a git work
# tree, this fixture would write files into the real repo — refuse.
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Refusing to run inside a git repository — run this fixture in an empty temp directory." >&2
  exit 1
fi

mkdir -p docs/backlog

cat > CLAUDE.md <<'MD'
# Acme Admin

## Issue tracker
Stories live in a **local markdown backlog** under `docs/backlog/`, one file per story.

## Task tracker
Tasks live in a **local markdown task store** under `docs/tasks/`, one file per story.
This is configured separately from the story backlog.
MD

cat > docs/backlog/001-archive-customer.md <<'MD'
Title: Archive a customer account

As an administrator
I want to archive a customer account
So that inactive customers are hidden without deleting their data

## Acceptance Criteria
Given an active customer
When an administrator archives that customer
Then the customer record is marked archived and the change is persisted

Given an archived customer
When an administrator views the active customer list
Then the archived customer does not appear in the list

Given an archived customer
When an administrator restores that customer
Then the customer is active again and reappears in the active list

## Source
Derived from: docs/spec.md — Customer archiving
MD

echo "Fixture ready: story 001 with three scenarios sharing a persisted-archived-state foundation; task store empty."
