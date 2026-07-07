---
name: adr
description: Captures Architecture Decision Records (ADRs) in the streamlined MADR format. Use when the user wants to record an architectural or technical decision, write an ADR, supersede or deprecate an existing one, or change an ADR's status.
allowed-tools: Bash
license: MIT
compatibility: Requires a POSIX shell.
---

# ADR

### Step 1: Locate the ADR directory

Search for an existing directory, in this order: `docs/adr`, `docs/adrs`, `doc/adr`, `adr`, `decisions`. Use the first that exists. If it already contains ADRs, note their conventions — filename style (number width, slug) and content structure (which sections, in what order) — and match them in Step 3. If none exists, default to `docs/adr/` and create it. Note whether a `README.md` index is present in that directory.

### Step 2: Choose the operation and qualify the decision

Determine which operation is being requested:

- **new** — record a fresh decision
- **supersede** — a new decision replaces an earlier ADR
- **status change** — move an existing ADR along its lifecycle (e.g. Proposed → Accepted, or → Deprecated)

A **status change** needs only the target ADR and its new status — skip to Step 5.

Before writing a **new** or **supersede** record, confirm the decision earns one. An ADR is worth it only when the decision is **both**:

- **Consequential** — it shapes the system or a quality attribute (scalability, security…), creates a long-lived constraint, or would cost days-to-weeks (not minutes) to reverse.
- **Non-obvious** — real alternatives were on the table and the rationale needs preserving to avoid repeat debates, or the choice needs alignment across more than one team.

A decision that is easy to reverse, obvious, or had no real alternative fails the bar — don't document every minor choice (picking a JSON library, naming a component, following a standard pattern). If it isn't **both**, say so and stop rather than recording noise; when unsure, ask the user whether it needs an ADR rather than defaulting to writing one.

A qualifying record then needs: a title, the context and drivers, **at least two considered options**, the chosen decision, and its consequences. If any are absent from the request or the conversation, ask for them — do not invent options, rationale, or consequences.

### Step 3: Write a new ADR

The formats below are the skill's defaults; when the directory already contains ADRs, match their filename and section conventions (noted in Step 1) instead.

- **Number:** the highest existing number plus one, padded to the width the existing files use; in an empty directory, zero-pad to four digits (first ADR is `0001`).
- **Filename:** `<number>-kebab-cased-title.md`.
- **Date:** use the output of `date +%F`; do not guess it.
- **Status:** `Accepted`, unless the decision is not yet final — then `Proposed`.
- **Body** — one decision per record; keep each section tight. Match the section structure of existing ADRs if there is one; otherwise use exactly these sections, in this order:

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
