#!/usr/bin/env bash
# Fixture: a project with one ADR (0003) still in Proposed status.
# Correct behaviour: a pure status change — flip 0003 to Accepted and update its
# index row; write NO new ADR and change nothing else in the file.
set -euo pipefail

# Guard: only ever run in a throwaway directory.
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Refusing to run inside a git repository — run this fixture in an empty temp directory." >&2
  exit 1
fi
printf '# Orders\n\nOrder-processing service.\n' > README.md
mkdir -p docs/adr
cat > docs/adr/0003-adopt-event-sourcing.md <<'MD'
# 0003. Adopt event sourcing for the order log

- Status: Proposed
- Date: 2026-02-20

## Context and drivers

We need a complete, replayable audit trail of every order state change.

## Considered options

- Event sourcing
- Audit-log table alongside mutable state

## Decision

Adopt event sourcing for the order aggregate.

## Consequences

Read models must be projected from the event stream.
MD
cat > docs/adr/README.md <<'MD'
# Architecture Decision Records

| # | Decision | Status |
|---|----------|--------|
| [0003](0003-adopt-event-sourcing.md) | Adopt event sourcing for the order log | Proposed |
MD
echo "Fixture ready: docs/adr with proposed 0003-adopt-event-sourcing.md + index."
