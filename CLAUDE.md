# CLAUDE.md

## What this repo is

A personal collection of skills for [Claude Code](https://claude.com/claude-code).
Each skill is authored to the portable [Agent Skills](https://agentskills.io/specification)
spec so it stays agent-agnostic. Skills live under `skills/<skill>/`:

```
skills/<skill>/
├── SKILL.md          # the skill: frontmatter (name, description) + instructions
└── evals/            # scenario evals (task.md, criteria.json, scenario.json, inputs/)
```

## Conventions

- Keep each `SKILL.md` compliant with the Agent Skills spec — skills must stay
  portable, not Claude-specific.
- When adding, renaming, or removing a skill, keep the [README](./README.md)
  Skills table in sync. Keep the skills in this table in alphabetical order.
- When adding a skill, wire it into the plugin marketplace by running
  `python3 scripts/register_plugin.py <skill> "<one-line summary>"`. It writes the
  skill's `.claude-plugin/plugin.json` and upserts its entry in
  [`.claude-plugin/marketplace.json`](./.claude-plugin/marketplace.json).
- When you change a skill, bump its version with
  `python3 scripts/bump_version.py <skill> <major|minor|patch>` — `patch` for fixes
  and wording, `minor` for a new backward-compatible capability, `major` for a
  breaking change to its behaviour or output contract.
- Never hand-edit the generated `plugin.json` or `marketplace.json` — go through
  the scripts, which may also be run by hand. `register_plugin.py` is idempotent,
  so re-running is always safe; `bump_version.py` is not — it bumps every time, so
  before bumping confirm the version wasn't already bumped for this change (e.g.
  `git diff HEAD -- skills/<skill>/.claude-plugin/plugin.json` shows the `version`
  line already changed).
- A `SKILL.md` is runtime instruction, not a changelog. Keep it imperative —
  no rationale, justification, or "why we did it" commentary. Be ruthless.
  Would removing content change what the executing agent does? If no, it's
  commentary — cut it. If yes, keep it, but phrase it as the directive, not
  the reason. Record the reasoning in the commit message.
- Commit with Conventional Commits; prefer small, atomic commits.

## Skill linting

The `skill-linter` skill's `skills/skill-linter/scripts/lint_skill.py` checks a
`SKILL.md` against the Agent Skills spec (frontmatter, naming, length limits,
references, and best-practice heuristics). A pre-commit hook runs it on every
top-level skill — enable it once per clone:

```sh
git config core.hooksPath .githooks
```

Run it manually on a single skill: `python3 skills/skill-linter/scripts/lint_skill.py
<skill-dir> [--json]`.
