#!/usr/bin/env bash
# Fixture: a greenfield project — a README describing the product and latent
# stack signals (Node), but NO CI, NO Dockerfile, NO IaC, NO e2e harness.
# The walking-skeleton skill should NOT bail; it should infer the stack, present
# it, confirm the deploy target explicitly, and interview narrowly.
set -euo pipefail

# Guard: only ever run in a throwaway directory. If we are inside a git work
# tree, this fixture would mutate the real repo (config, files) — refuse.
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Refusing to run inside a git repository — run this fixture in an empty temp directory." >&2
  exit 1
fi

git init -q
git config user.email fixture@example.com
git config user.name Fixture

mkdir -p src

cat > README.md <<'MD'
# TaskFlow

TaskFlow is a web app that helps small teams track work. A user signs in, creates
tasks, assigns them to teammates, and marks them done. We want a dashboard, email
reminders, recurring tasks, and a mobile app later — but none of that is built yet.

This repo is brand new. Nothing has been set up.
MD

cat > package.json <<'JSON'
{
  "name": "taskflow",
  "version": "0.0.0",
  "private": true,
  "dependencies": {
    "express": "^4.19.0"
  }
}
JSON

cat > .nvmrc <<'NVM'
20
NVM

cat > src/app.js <<'JS'
const express = require("express");
const app = express();
app.get("/", (_, res) => res.send("TaskFlow"));
module.exports = app;
JS

git add -A
git commit -qm "chore: initial TaskFlow app skeleton"
