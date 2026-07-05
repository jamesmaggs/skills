---
name: skill-evaluator
description: Measures a skill's real value programmatically and tracks it over time — runs the skill with its guidance versus a no-skill baseline and scores the difference. Also authors an eval spec for a skill that has none. Use when the user wants to evaluate, score, or benchmark a skill, prove it beats baseline, or create evals for a skill. For mechanical spec compliance (frontmatter, paths, length) use skill-linter instead.
allowed-tools: Bash, Read, Write, Edit
license: MIT
compatibility: Requires Docker, python3, and the claude CLI.
---

# Skill Evaluator

Judge a skill by what it **adds**, not how it reads. Every metric comes from running the
skill headlessly and grading the trace — a skill can read beautifully and still change
nothing. The eval spec format, check types, and scoring live in
[`references/eval-spec.md`](references/eval-spec.md); read it before authoring or judging.

Two flows: **author** an eval spec for a skill that lacks one, then **run** it.

## Prerequisites (for running; authoring needs none)

- Docker daemon running, and the sandbox image built once: `bash scripts/build_image.sh`.
- `ANTHROPIC_API_KEY` available for the **sandboxed** runs — export it or put
  `ANTHROPIC_API_KEY=sk-...` in a gitignored `.env` at the repo root (loaded
  automatically; override with `--env-file`). These runs bill against **API credits**,
  which a Claude subscription does not include.
- The **rubric grader** runs on the host and uses your **subscription** by default (off
  the API bill); pass `--grader-auth apikey` in CI where no subscription exists.
- **Model policy:** default to **haiku** (cheapest, and where a skill adds the most
  value); **sonnet** is the ceiling; **opus is rejected**.

## Trust boundary

The sandbox is hardened — dropped capabilities, no privilege escalation, read-only root
filesystem, and CPU/memory/pid limits — and the host side refuses path traversal in
fixtures and check paths, caps file reads, and runs the grader with no tools, no MCP, and
empty settings so untrusted output can't drive it. **But the container needs network to
reach the API and the API key lives inside it**, so a hostile skill with network access
could exfiltrate the key. As shipped, evaluate **skills you trust**; running genuinely
untrusted skills safely would need an egress-restricting proxy that keeps the key out of
the container.

## Author evals

Produce `<skill>/evals/triggering.csv` and `<skill>/evals/outcome.json` per
`references/eval-spec.md`. Read the target `SKILL.md` first, then:

1. **triggering.csv** — positive prompts the skill should fire on, plus **negative
   controls** it must stay quiet on.
2. **outcome.json** — 2–4 **discriminating** tasks (ones a no-skill baseline would fail),
   each with checks: deterministic where possible, a `rubric` check only where
   correctness needs judgement. Add a `fixture` dir when the task needs a starting state.
3. Validate: `python3 scripts/validate_spec.py --skill <skill-dir>`. Fix every error.

**Done when** `validate_spec.py` reports 0 errors and every outcome case is one you
believe baseline would fail.

## Run evals

1. Ensure the image is built (see Prerequisites).
2. `python3 scripts/run_evals.py --skill <skill-dir> [--model haiku|sonnet] [--json]`.
   Each triggering row runs with the skill available (does it fire?); each outcome case
   runs twice — once with the skill's guidance injected, once at baseline — to isolate
   the guidance's value. Use `--dry-run` first to confirm the plan.
3. Read the summary: `trigger_accuracy`, `outcome_pass_rate` (vs `baseline_pass_rate`),
   `value_delta`, and the `composite`. The run appends one line to
   `<skill>/evals/results/history.jsonl`.

## Report the verdict

Lead with **`value_delta`** — it isolates what the skill adds; `trigger_accuracy` and
`outcome_pass_rate` explain *why* it's high or low. Quote failing checks with their
evidence. End with **ship / revise / rethink**:

- **ship** — clear positive `value_delta` and sound triggering.
- **revise** — value is real but triggering misfires, or a few checks fail.
- **rethink** — `value_delta` at or below zero: baseline already does the job, so the
  skill earns its context cost only if it starts adding something.

Never call a skill effective from reading alone — cite the measured delta.
