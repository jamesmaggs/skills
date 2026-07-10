#!/usr/bin/env bash
# Fixture: a story with well-formed, testable acceptance criteria. Correct
# behaviour: pass the gate and decompose into single-session tasks — each with a
# concrete Verification — written to the markdown task store, covering every
# acceptance criterion, with no needs-clarification flag on the story.
set -euo pipefail

# Guard: only ever run in a throwaway directory. If we are inside a git work
# tree, this fixture would write files into the real repo — refuse.
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Refusing to run inside a git repository — run this fixture in an empty temp directory." >&2
  exit 1
fi

mkdir -p docs/backlog

cat > CLAUDE.md <<'MD'
# Acme Accounts

## Issue tracker
Stories live in a **local markdown backlog** under `docs/backlog/`, one file per story.

## Task tracker
Tasks live in a **local markdown task store** under `docs/tasks/`, one file per story.
This is configured separately from the story backlog.
MD

cat > docs/backlog/001-password-reset.md <<'MD'
Title: Reset a forgotten password

As a registered user
I want to reset my password via an emailed link
So that I can regain access if I forget my password

## Acceptance Criteria
Given a registered user with email "a@b.com"
When they request a password reset for "a@b.com"
Then an email is sent containing a reset link with a single-use token

Given a valid, unexpired reset token
When the user submits a new password with that token
Then the stored password hash is updated and the token is marked used

Rule: reset tokens expire 1 hour after they are issued

## Source
Derived from: docs/spec.md — R2 Password reset
MD

echo "Fixture ready: story 001 with two testable scenarios + one rule; task store docs/tasks/ empty."
