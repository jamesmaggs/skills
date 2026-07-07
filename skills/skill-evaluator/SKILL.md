---
name: skill-evaluator
description: Evaluates whether a skill actually works: grades how it is written, then measures what it adds by running it against a no-skill baseline. Also authors an eval spec for a skill that has none.
disable-model-invocation: true
allowed-tools: Bash, Read, Write, Edit
license: MIT
---

# Skill Evaluator

Judge a skill by what it **adds**, not how it reads. A skill's worth is the gap between the
model's performance *with* it and *without* it — a skill can read beautifully and still
change nothing. That gap is measurable in whatever harness you are already in; no special
tooling is required. The eval spec format, check types, and scoring live in
[`references/eval-spec.md`](references/eval-spec.md); read it before authoring or judging.

Two flows: **author** an eval spec for a skill that lacks one, then **evaluate**.

## Author an eval spec

Produce `<skill>/evals/triggering.csv` and `<skill>/evals/outcome.json` per
`references/eval-spec.md`. Read the target `SKILL.md` first, then:

1. **triggering.csv** — positive prompts the skill should fire on, plus **negative
   controls** it must stay quiet on. Omit this file for a **user-invoked** skill
   (`disable-model-invocation: true`): it never fires on its own, so triggering is moot.
2. **outcome.json** — 2–4 **discriminating** tasks (ones a no-skill baseline would fail),
   each with checks: deterministic where possible, a `rubric` check only where correctness
   needs judgement. Add a `fixture` dir when the task needs a starting state.
3. Check the spec against the format in `references/eval-spec.md`.

**Done when** the spec matches the format and every outcome case is one you believe
baseline would fail.

## Evaluate

Three parts. Value is decisive; the other two explain it.

### Calibration — how it reads

Walk the body and classify every passage **keep / cut / push**: keep what changes
behaviour, cut what the model already does by default or says twice, push reference that
belongs behind a pointer. Name all three categories even when one is empty. This measures
form, not effectiveness — a skill can pass every check and still add nothing.

### Triggering — would it fire

Judge the **description** qualitatively: does it carry *what + when* in the third person,
name the key terms, cover the phrasings a user would actually use, and avoid firing on
near-misses or losing to a competing skill? For a **user-invoked** skill
(`disable-model-invocation: true`), triggering is **N/A** — the user is the index; say so
and skip it.

### Value — what it adds (decisive)

Run each `outcome.json` case **twice**: once with the skill's guidance in context, once at
baseline (nothing). In Claude Code, spawn one subagent per configuration so they run in the
same turn; elsewhere, run them yourself one at a time with fresh context each. Grade every
run against the case's `checks`, recording `pass` + `evidence`, then compute
`value_delta = with_skill_pass_rate − baseline_pass_rate`.

Watch for non-discriminating checks (baseline passes them too) and presence-not-correctness
traps — both make the delta lie. Flag them rather than trusting the number.

This repo ships an optional local runner at `scripts/eval/` that automates these value runs
in a Docker sandbox for CI and dashboards (see its README for prerequisites). Use it when
present; the evaluation does not require it.

**Done when** you have a measured with-vs-baseline delta — reason it through inline only
when no run was possible, and label it as such.

## Report the verdict

Lead with **`value_delta`** — it isolates what the skill adds; calibration and triggering
explain *why* it is high or low. Quote failing checks with their evidence. End with
**ship / revise / rethink**:

- **ship** — clear positive `value_delta` and sound triggering.
- **revise** — value is real but triggering misfires, or a few checks fail.
- **rethink** — `value_delta` at or below zero: baseline already does the job, so the skill
  earns its context cost only if it starts adding something.

Never call a skill effective from reading alone — cite the measured delta.
