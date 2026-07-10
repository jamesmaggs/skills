#!/usr/bin/env bash
# Fixture: a project with one accepted ADR (0001) that a new decision replaces.
# Correct behaviour: write 0002 (naming what it supersedes), flip 0001 to
# Superseded-by-0002, and update both index rows.
set -euo pipefail

# Guard: only ever run in a throwaway directory.
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Refusing to run inside a git repository — run this fixture in an empty temp directory." >&2
  exit 1
fi
printf '# API Gateway\n\nEdge service for the public API.\n' > README.md
mkdir -p docs/adr
cat > docs/adr/0001-use-a-rest-api.md <<'MD'
# 0001. Use a REST API

- Status: Accepted
- Date: 2026-01-15

## Context and drivers

Third-party integrators need a public API and are familiar with REST.

## Considered options

- REST
- GraphQL

## Decision

Expose a REST API.

## Consequences

Clients over-fetch on endpoints that return large aggregates.
MD
cat > docs/adr/README.md <<'MD'
# Architecture Decision Records

| # | Decision | Status |
|---|----------|--------|
| [0001](0001-use-a-rest-api.md) | Use a REST API | Accepted |
MD
echo "Fixture ready: docs/adr with accepted 0001-use-a-rest-api.md + index."
