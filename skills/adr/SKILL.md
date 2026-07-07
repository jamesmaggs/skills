---
name: adr
description: Captures Architecture Decision Records (ADRs) in the streamlined MADR format. Use when the user wants to record an architectural or technical decision, write an ADR, supersede or deprecate an existing one, or change an ADR's status.
allowed-tools: Bash
license: MIT
compatibility: Requires a POSIX shell.
---

# ADR

### Step 1: Locate the ADR directory

Search for an existing directory, in this order: `docs/adrs`, `docs/adr`, `doc/adr`, `adr`, `decisions`. Use the first that exists, and match the convention of the files already in it (number width, filename style, section headers). If none exists, default to `docs/adrs/` and create it. Note whether a `README.md` index is present in that directory.

### Step 2: Choose the operation and gather inputs

Determine which operation is being requested:

- **new** — record a fresh decision
- **supersede** — a new decision replaces an earlier ADR
- **status change** — move an existing ADR along its lifecycle (e.g. Proposed → Accepted, or → Deprecated)

A **new** or **supersede** record needs: a title, the context and drivers, **at least two considered options**, the chosen decision, and its consequences. If any are absent from the request or the conversation, ask for them — do not invent options, rationale, or consequences.

### Step 3: Write a new ADR

- **Number:** the highest `NNNN` among existing `NNNN-*.md` files, plus one; zero-padded to four digits (first ADR is `0001`).
- **Filename:** `NNNN-kebab-cased-title.md`.
- **Date:** use the output of `date +%F`; do not guess it.
- **Status:** `Accepted`, unless the decision is not yet final — then `Proposed`.
- **Body** — exactly these sections, in this order (one decision per record; keep each section tight):

  ```markdown
  # NNNN. Title

  - Status: <status>
  - Date: <YYYY-MM-DD>

  ## Context and drivers

  ## Considered options

  ## Decision

  ## Consequences
  ```

- **Index:** if a `README.md` exists in the ADR directory, append a row for the new ADR; otherwise create one with a `| # | Decision | Status |` table and the new row, linking the number to its file.

### Step 4: Supersede an ADR

Write the new ADR (Step 3); its Decision should name the ADR it replaces. Then set the superseded ADR's status to `Superseded-by-NNNN` (the new number) and update its row in the index.

### Step 5: Change an ADR's status

Update the `- Status:` line of the named ADR and its row in the index.
