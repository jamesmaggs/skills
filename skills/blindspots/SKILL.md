---
name: blindspots
description: Surfaces how a task is most likely to go wrong before it is attempted, and the one instruction that would prevent each blind spot, then waits for the user to close the gaps.
disable-model-invocation: true
---

# Blindspots

Predict how you will fail the task *before* doing it, then hand the gaps back to the
user to close.

## Step 1: Surface the blind spots

Read the pending task, then name the **top five** ways it is most likely to go wrong for
you — concrete to *this* task, never generic advice. Draw from these angles (mark one
N/A only if it genuinely does not apply):

- **Misread intent** — where the request is ambiguous and you could take the wrong reading.
- **Unstated assumption** — what you would fill in that the user never actually said.
- **Generic drift** — where you would hedge, pad, or give a templated answer instead of a
  specific one.
- **Genuinely hard** — the part that is hard for a model like you, not just hard in general.

## Step 2: Propose a fix for each

For every blind spot, give the **single instruction** the user could paste into the
prompt to prevent it — one directive sentence, usable as-is.

## Step 3: Stop and wait

Present the five blind spots, each paired with its fix, then **stop**. Do not begin the
task until the user responds.

**Done when** control is back with the user — never when the task itself has been started.
