#!/usr/bin/env bash
# Fixture: a project that already keeps ADRs in doc/adr (note: not the default
# docs/adr), numbered with THREE digits and using a non-default section layout.
# Correct behaviour: discover doc/adr, match the 3-digit width (next is 008),
# mirror the existing headings, and append to the existing index.
set -euo pipefail

# Guard: only ever run in a throwaway directory.
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Refusing to run inside a git repository — run this fixture in an empty temp directory." >&2
  exit 1
fi
printf '# Platform\n\nInternal platform services.\n' > README.md
mkdir -p doc/adr
cat > doc/adr/007-use-a-rest-api.md <<'MD'
# 7. Use a REST API

- Status: Accepted
- Date: 2026-01-15

## Context

We need a public API for third-party integrators.

## Decision Drivers

- Broad client familiarity
- Simple HTTP caching

## Considered Options

- REST
- GraphQL
- gRPC

## Decision Outcome

Chosen: REST, because it is the most widely understood by our integrators.
MD
cat > doc/adr/README.md <<'MD'
# Architecture Decision Records

| # | Decision | Status |
|---|----------|--------|
| [007](007-use-a-rest-api.md) | Use a REST API | Accepted |
MD
echo "Fixture ready: doc/adr with 007-use-a-rest-api.md (3-digit, custom sections) + index."
