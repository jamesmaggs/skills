---
name: skill-linter
description: Deterministically checks a SKILL.md against the official Agent Skills spec — frontmatter limits, body length, one-level-deep references, path style, time-sensitive content — reporting errors plus heuristic warnings.
disable-model-invocation: true
---

# Skill Linter

Mechanically check a skill against the parts of the Agent Skills spec that can be
decided without judgement. This is a linter, not a critic: it tells you whether a
skill is *well-formed*, not whether it is *good* or *effective* — those take human
judgement, not this tool.

## How to run

The script is the source of truth — run it and relay what it reports; never
substitute your own read-through. Several checks turn on exact quantities a reader
can't judge by eye (description length in characters, body length in lines,
reserved-word matching), and eyeballing is exactly where those get missed.

```bash
python3 scripts/lint_skill.py <path-to-skill-dir> [--json]
```

It exits `0` when there are no errors (warnings are allowed), `1` when any error
is found, and `2` if the path can't be read. Use `--json` to parse the result
programmatically; otherwise read the human-readable report. After running it,
report the verdict line and quote the specific errors and warnings rather than
paraphrasing.

## How to interpret the output

Each check is `error`, `warning`, or passing.

- **Errors** are violations of the spec's hard rules (name charset and length,
  reserved words, the 1024-char description limit, missing frontmatter). A skill
  with errors should not be published until they are fixed.
- **Warnings** are best-practice heuristics (third-person description, a "when"
  cue, body under 500 lines, one-level-deep references, no time-sensitive text).
  They need a human's judgement, not blind obedience.

Report the verdict and walk the user through each error and warning. For warnings,
say *why* the rule exists so they can decide whether it applies, rather than
treating every flag as a defect.

## Warnings are heuristics, so expect the occasional false positive

The text-based checks pattern-match; they cannot read intent. A `time-sensitive`
flag might be a deliberate "old patterns" note; a `desc-third-person` flag might
be a quoted user phrase. When a warning looks wrong, say so and explain why,
rather than forcing a change that makes the skill worse.

## What this skill does NOT do

It does not assess calibration (is the body lean, or padded with things the model
already knows?), description triggering quality, or whether the skill beats a
no-skill baseline on real tasks. Those are matters of judgement and real-task
performance — out of scope for a mechanical linter. A clean bill here means the
skill is well-formed, not that it is good.

Checks are grounded in Anthropic's Agent Skills best-practices and spec
(`platform.claude.com/docs/en/agents-and-tools/agent-skills`).
