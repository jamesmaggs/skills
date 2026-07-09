#!/usr/bin/env bash
# Fixture: a walking skeleton already IN PROGRESS — docs/WALKING-SKELETON.md
# exists with some boxes ticked and partial infra on disk. Because the plan file
# is present, the skill should resume (summarise progress, ask resume-or-restart)
# rather than let its own partial infra trip the bail-gate.
set -euo pipefail

git init -q
git config user.email fixture@example.com
git config user.name Fixture

mkdir -p src docs

cat > README.md <<'MD'
# TaskFlow

A web app for small teams to track work. Greenfield.
MD

cat > package.json <<'JSON'
{ "name": "taskflow", "version": "0.0.0", "private": true }
JSON

# Partial infra already laid down by an earlier run of the skill.
cat > Dockerfile <<'DOCKER'
FROM node:20-slim
WORKDIR /app
COPY . .
CMD ["node", "src/app.js"]
DOCKER

cat > docs/WALKING-SKELETON.md <<'MD'
# Walking Skeleton

**Trivial slice:** the home page renders one value fetched from the DB through the API.
**Stack:** Node/Express · single web service · Postgres
**Deploy target:** Google Cloud Run (europe-west1)

## Steps
- [x] Failing end-to-end test driving the deployed system
- [x] Build automation (one command -> deployable artifact)
- [ ] IaC for the production-like environment
- [ ] Components wired to perform the trivial slice
- [ ] CI: build -> deploy -> e2e test
- [ ] Deploy — e2e test passes through the deployed system

## Auth hand-offs
- [ ] gcloud auth login (user to run)

## Notes
Stopped after wiring up the build. IaC for Cloud Run is next.
MD

git add -A
git commit -qm "wip: walking skeleton — build automation done, IaC next"
