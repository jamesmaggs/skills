---
name: to-stories
description: Reads a project's documentation and codebase, finds capabilities that are specified but not yet built (and not already tracked), and creates INVEST-validated user stories — Connextra format with Gherkin acceptance criteria — in the project's issue tracker.
disable-model-invocation: true
---

# To Stories

Turn the gap between what the docs promise and what the code does into a backlog
of agent-actionable user stories. Each story is written so a coding agent can
pick it up and implement it end-to-end, then check its own work against the
acceptance criteria.

The unimplemented set is the intersection of three facts:

> **specified in the docs** ∧ **absent from the code** ∧ **not already in the tracker**

A capability that fails any one of these is not a story. Getting the intersection
right — not the writing — is where the effort goes.

## Step 1: Locate the tracker

Read the project's docs for where stories live — check `CLAUDE.md`, `AGENTS.md`,
`README`, and `docs/` for an issue-tracker line (a named tracker, a repo, or a
backlog path). Then resolve one of two destinations:

- **GitHub Issues** — the default when the repo has a GitHub remote. Confirm the
  tooling works before drafting: `gh auth status` (authenticated) and
  `gh repo view --json nameWithOwner` (repo resolves). If `gh` is missing or
  unauthenticated, tell the user how to fix it (`! gh auth login`) or fall back
  to markdown.
- **Local markdown backlog** — the fallback when no tracker is reachable, or the
  docs name an unsupported tracker (Jira, Linear, …). Write to `docs/backlog/`,
  one file per story.

State the resolved destination in one line before continuing.

## Step 2: Map what is specified

Build the set of intended capabilities from the documentation — `README`, `docs/`,
PRDs, specs, design notes, requirement lists. Capture each as a discrete
capability with a pointer back to its source section (you will cite it in the
story). Ignore aspiration that is too vague to test; keep anything concrete
enough to become a Given/When/Then.

## Step 3: Map what is built

Inspect the codebase to determine which of those capabilities already exist —
routes, handlers, modules, commands, UI, tests. Match by behaviour, not by name:
a capability is "built" when the code actually delivers it, not when a stub or a
TODO gestures at it. A half-built capability is a gap.

## Step 4: Fetch existing stories

List what the tracker already holds — you are reconciling against it, not just
appending to it:

- **GitHub** — `gh issue list --state all --limit 500 --json number,title,body,state`.
  Include closed issues: a closed story means done or rejected, not "do again".
- **Markdown** — read every file already under `docs/backlog/`.

## Step 5: Reconcile, then compute the gap

Compare each specified-but-unbuilt capability against the existing stories by
**capability, not exact title**, and sort it into one of three buckets:

- **Already covered** — an existing story (open or closed) fully captures the
  capability. Drop it; create nothing.
- **Partially covered** — an existing *open* story covers the requirement only in
  part. Do not create a duplicate. Instead **propose an update** to that story
  (added/sharpened acceptance criteria, corrected source) for the user to accept.
- **New** — no existing story covers it. This is the story set for Steps 6–8.

While reconciling, also look the other way: if an existing **open** story no
longer corresponds to anything in the current spec, **flag it for review** rather
than acting on it or spawning unrelated work beside it — the spec may have moved
on, or the story may be stale.

New stories are created directly in Step 8. Proposed updates and stale-story flags
are *surfaced for the user*, not applied — you did not author those stories, so
you do not silently mutate or close them. If the whole intersection is empty and
there is nothing to update or flag, say so and stop — a clean reconciliation is a
valid result, not a failure.

## Step 6: Draft each story

Write every story in this exact shape. The title is imperative; the body is
Connextra + Gherkin. Acceptance criteria must be concrete enough that an agent
can implement against them and verify them — reference real entities and
observable outcomes, never "works correctly".

```
Title: <short imperative summary>

As a <role>
I want <capability>
So that <value>

## Acceptance Criteria
Given <precondition>
When <action>
Then <outcome>

[additional Given/When/Then scenarios, and rule-based constraints where relevant]

## Source
Derived from: <spec section / doc reference>
```

Use a rule-based constraint (a plain "Rule: …" line) when a requirement is a
flat invariant rather than a scenario — e.g. `Rule: passwords are never logged`.

## Step 7: Validate against INVEST

Every story must pass INVEST before it is created. Read `references/invest.md` for
the rubric and the fix for each failing letter. The two that most often force a
rewrite: **Small** (split an epic into thin vertical slices) and **Independent**
(decouple or sequence stories that secretly depend on each other). Revise until
each story passes; a story that cannot be made to pass is a sign the underlying
spec is unclear — flag it rather than shipping a weak story.

## Step 8: Create

The user ran `/to-stories` to create stories, so create them directly — no further
approval gate — but keep each one traceable.

- **GitHub** — ensure the label exists once: `gh label create story --description
  "Generated by to-stories" --force`. Then per story:
  `gh issue create --title "<title>" --body "<body>" --label story`. Pass the body
  via `--body-file` (a temp file in the scratchpad) when it contains characters
  that fight the shell.
- **Markdown** — write each story to `docs/backlog/<nnn>-<slug>.md`, continuing
  the existing number sequence.

## Step 9: Report

Give the user the full picture of the reconciliation, grouped:

- **Created** — new stories, with issue numbers and URLs, or file paths.
- **Update proposed** — existing stories a candidate partially overlapped, with the
  specific change you suggest, for the user to accept or decline.
- **Flagged for review** — open stories that no longer match the spec.
- **Skipped** — capabilities held back because the spec was too vague, or stories
  that could not be made to pass INVEST and need the spec clarified first.

Omit any empty group.
