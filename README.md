# Skills

A personal collection of skills for [Claude Code](https://claude.com/claude-code), authored to the portable [Agent Skills](https://agentskills.io/specification) spec.

## Skills

| Skill | Description |
|-------|-------------|
| [brand-voice](./skills/brand-voice/SKILL.md) | Interview to establish a brand's voice, scored on the [four tone-of-voice dimensions](https://www.nngroup.com/articles/tone-of-voice-dimensions/) |
| [commit](./skills/commit/SKILL.md) | Stage and commit changes using [Conventional Commits](https://www.conventionalcommits.org) |
| [premortem](./skills/premortem/SKILL.md) | Run a premortem before starting a task — assume it failed, surface why, and fix the gaps first |
| [six-thinking-hats](./skills/six-thinking-hats/SKILL.md) | Review or stress-test an idea from six parallel perspectives (de Bono's Six Thinking Hats) |
| [walking-skeleton](./skills/walking-skeleton/SKILL.md) | Stand up a walking skeleton at project start — the thinnest end-to-end slice, built, deployed, and tested through a real deployment |

## Install

This repo is a [Claude Code plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces).
Add it, then install any skill from the table above by name:

```sh
/plugin marketplace add jamesmaggs/skills
/plugin install <skill>@jamesmaggs   # e.g. commit@jamesmaggs
```

## License

MIT — see [LICENSE](./LICENSE).
