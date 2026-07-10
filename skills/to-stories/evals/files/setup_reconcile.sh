#!/usr/bin/env bash
# Fixture: an existing markdown backlog to reconcile against. The spec has one
# capability partially covered by an existing story, one brand-new capability,
# and the backlog holds a stale story no longer in the spec. Nothing is built.
# Correct behaviour:
#   - new capability (price filter) -> create a new story
#   - partially-covered capability (search by city) -> PROPOSE updating story 001,
#     not a duplicate, and do NOT edit the file
#   - stale story 002 (loyalty points, absent from spec) -> FLAG for review,
#     do NOT edit or delete the file
set -euo pipefail

# Guard: only ever run in a throwaway directory. If we are inside a git work
# tree, this fixture would write files into the real repo — refuse.
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Refusing to run inside a git repository — run this fixture in an empty temp directory." >&2
  exit 1
fi

mkdir -p docs/backlog src

cat > CLAUDE.md <<'MD'
# Wanderlust

Hotel search.

## Issue tracker

Stories live in a **local markdown backlog** under `docs/backlog/`, one file per
story.
MD

cat > docs/spec.md <<'MD'
# Wanderlust — product spec

## Capabilities

### S1 — Search hotels
A traveller can search for hotels by city name and see matching results. (The
current backlog only covers exact-name lookup, not search by city.)

### S2 — Filter by price
A traveller can filter search results to a maximum nightly price.
MD

# Existing story that only PARTIALLY covers S1 (exact-name lookup, not by city).
cat > docs/backlog/001-lookup-hotel-by-name.md <<'MD'
Title: Look up a hotel by exact name

As a traveller
I want to look up a hotel by its exact name
So that I can jump straight to a hotel I already know

## Acceptance Criteria
Given a hotel named "The Grand" exists
When I search for "The Grand"
Then that hotel is returned

## Source
Derived from: docs/spec.md — S1 Search hotels
MD

# Stale story: loyalty points is nowhere in the current spec.
cat > docs/backlog/002-loyalty-points.md <<'MD'
Title: Earn loyalty points on booking

As a traveller
I want to earn loyalty points when I book
So that I am rewarded for repeat bookings

## Acceptance Criteria
Given I complete a booking of £200
When the booking is confirmed
Then 200 loyalty points are credited to my account

## Source
Derived from: docs/spec.md — (loyalty programme)
MD

echo "Fixture ready: spec.md (S1-S2, nothing built), backlog holds 001 (partial S1) and 002 (stale)."
