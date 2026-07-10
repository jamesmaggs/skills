#!/usr/bin/env bash
# Fixture: two stories in the backlog, one already decomposed (it has a tasks file
# in the task store) and one not. No story is named in the request. Correct
# behaviour: pick the un-decomposed story (002 logout) and decompose it, leaving
# the already-decomposed story (001 login) and its existing tasks untouched.
set -euo pipefail

# Guard: only ever run in a throwaway directory. If we are inside a git work
# tree, this fixture would write files into the real repo — refuse.
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Refusing to run inside a git repository — run this fixture in an empty temp directory." >&2
  exit 1
fi

mkdir -p docs/backlog docs/tasks

cat > CLAUDE.md <<'MD'
# Acme Accounts

## Issue tracker
Stories live in a **local markdown backlog** under `docs/backlog/`, one file per story.

## Task tracker
Tasks live in a **local markdown task store** under `docs/tasks/`, one file per story.
This is configured separately from the story backlog.
MD

cat > docs/backlog/001-login.md <<'MD'
Title: Log in with email and password

As a registered user
I want to log in with my email and password
So that I can access my account

## Acceptance Criteria
Given a registered user with a correct password
When they submit their email and password
Then a session is created and a 200 response with a session cookie is returned

Given a registered user with a wrong password
When they submit their email and password
Then no session is created and a 401 response is returned

## Source
Derived from: docs/spec.md — Login
MD

# 001 is ALREADY decomposed — it has a tasks file in the task store.
cat > docs/tasks/001-login.md <<'MD'
# Tasks for 001 — Log in with email and password

- [ ] Task: Create a session on correct credentials
  Story: docs/backlog/001-login.md
  Satisfies: correct-password scenario
  ## Verification
  POST /login with valid creds returns 200 and a session cookie
  ## Depends on
  none
MD

cat > docs/backlog/002-logout.md <<'MD'
Title: Log out of a session

As a logged-in user
I want to log out
So that my session cannot be reused on a shared device

## Acceptance Criteria
Given a user with an active session
When they log out
Then the session is invalidated and a 200 response clearing the session cookie is returned

Given an invalidated session cookie
When it is used on any authenticated endpoint
Then a 401 response is returned

## Source
Derived from: docs/spec.md — Logout
MD

echo "Fixture ready: 001-login already decomposed (docs/tasks/001-login.md present), 002-logout not yet decomposed."
