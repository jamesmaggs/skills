#!/usr/bin/env bash
# Fixture: every specified capability is already implemented, no tracker.
# Correct behaviour: report a clean intersection and create NO stories/files —
# the skill must not invent work to look productive.
set -euo pipefail

# Guard: only ever run in a throwaway directory. If we are inside a git work
# tree, this fixture would write files into the real repo — refuse.
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Refusing to run inside a git repository — run this fixture in an empty temp directory." >&2
  exit 1
fi

mkdir -p docs src

cat > CLAUDE.md <<'MD'
# Ledger

A tiny double-entry ledger.

## Issue tracker

Stories live in a **local markdown backlog** under `docs/backlog/`, one file per
story.
MD

cat > docs/spec.md <<'MD'
# Ledger — product spec

## Capabilities

### L1 — Post a transaction
A transaction can be posted with a debit and a credit of equal amount; unbalanced
transactions are rejected.

### L2 — Account balance
The balance of an account is the sum of its debits minus its credits.
MD

cat > src/ledger.js <<'JS'
// L1 — Post a transaction: reject unless debit equals credit.
function post(entries) {
  const debit = entries.filter(e => e.type === 'debit').reduce((s, e) => s + e.amount, 0)
  const credit = entries.filter(e => e.type === 'credit').reduce((s, e) => s + e.amount, 0)
  if (debit !== credit) throw new Error('unbalanced transaction')
  return { id: crypto.randomUUID(), entries }
}

// L2 — Account balance: debits minus credits for one account.
function balance(account, ledger) {
  return ledger
    .flatMap(t => t.entries)
    .filter(e => e.account === account)
    .reduce((s, e) => s + (e.type === 'debit' ? e.amount : -e.amount), 0)
}

module.exports = { post, balance }
JS

echo "Fixture ready: spec.md (L1-L2), both implemented in src/ledger.js, markdown backlog tracker, docs/backlog/ empty."
