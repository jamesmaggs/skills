---
name: premortem
description: Runs a premortem on a pending task — assumes it is already done and has failed, names the five most likely reasons why, pairs each with a preventing instruction, and stops for the user to close the gaps first.
disable-model-invocation: true
---

# Premortem

Assume the task is already finished — and botched. Look back from that failure and
explain what went wrong, then hand the fixes to the user *before* taking a single step.

## Step 1: Imagine the failure

Name the **top five** reasons it failed — concrete to *this* task, never generic advice,
each written as something that already happened ("it failed because…"), not a hypothetical
("it might…"). Draw from these angles (mark one N/A only if it genuinely does not apply):

- **Misread intent** — the request was ambiguous and you took the wrong reading.
- **Unstated assumption** — you filled in something the user never actually said.
- **Generic drift** — you hedged, padded, or gave a templated answer instead of a
  specific one.
- **Genuinely hard** — the part that is hard for a model like you, not just hard in general.

## Step 2: Prevent each one

For every failure, give the **single instruction** the user could paste into the prompt to
head it off — one directive sentence, usable as-is.

## Step 3: Stop and wait

Present the five failures, each paired with its fix, then **stop**. Do not begin the task
until the user responds.

**Done when** control is back with the user — never when the task itself has been started.
