#!/usr/bin/env bash
# Fixture: a spec describing three capabilities, one already built, no tracker.
# Correct behaviour: create stories only for the two unimplemented capabilities
# (password reset, CSV export), NOT for the already-built one (registration).
set -euo pipefail

# Guard: only ever run in a throwaway directory. If we are inside a git work
# tree, this fixture would write files into the real repo — refuse.
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Refusing to run inside a git repository — run this fixture in an empty temp directory." >&2
  exit 1
fi

mkdir -p docs src/auth

cat > CLAUDE.md <<'MD'
# Acme Accounts

A small user-accounts service.

## Issue tracker

This project has no hosted tracker. Stories live in a **local markdown backlog**
under `docs/backlog/`, one file per story.
MD

cat > docs/spec.md <<'MD'
# Acme Accounts — product spec

## Capabilities

### R1 — Registration
Users can register with an email address and a password. The password is hashed
before storage and a duplicate email is rejected.

### R2 — Password reset
Users who forget their password can request a reset link by email and set a new
password via that link. Reset links expire after one hour.

### R3 — User export
An administrator can export the full list of users as a CSV file, including email
and signup date but never the password hash.
MD

cat > src/auth/register.js <<'JS'
const bcrypt = require('bcrypt')
const { db } = require('../db')

// R1 — Registration: hash the password, reject duplicate emails.
async function register(email, password) {
  const existing = await db.users.findByEmail(email)
  if (existing) throw new Error('email already registered')
  const passwordHash = await bcrypt.hash(password, 12)
  return db.users.insert({ email, passwordHash, createdAt: new Date() })
}

module.exports = { register }
JS

echo "Fixture ready: spec.md (R1-R3), R1 implemented in src/auth/register.js, markdown backlog tracker, docs/backlog/ empty."
