#!/usr/bin/env bash
# Fixture: a story whose acceptance criterion is not testable ("works correctly
# and loads fast" — no observable outcome). Correct behaviour: HALT before
# decomposing, create NO tasks, and flag the story in its tracker (a
# needs-clarification note appended to the story file).
set -euo pipefail

# Guard: only ever run in a throwaway directory. If we are inside a git work
# tree, this fixture would write files into the real repo — refuse.
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Refusing to run inside a git repository — run this fixture in an empty temp directory." >&2
  exit 1
fi

mkdir -p docs/backlog

cat > CLAUDE.md <<'MD'
# Acme

## Issue tracker
Stories live in a **local markdown backlog** under `docs/backlog/`, one file per story.

## Task tracker
Tasks live in a **local markdown task store** under `docs/tasks/`, one file per story.
This is configured separately from the story backlog.
MD

cat > docs/backlog/001-account-dashboard.md <<'MD'
Title: Show an account dashboard

As a customer
I want a dashboard of my account
So that I can see everything at a glance

## Acceptance Criteria
Given I am logged in
When I open the dashboard
Then it works correctly and loads fast

## Source
Derived from: docs/spec.md — Dashboard
MD

echo "Fixture ready: story 001 with an untestable acceptance criterion; task store docs/tasks/ empty."
