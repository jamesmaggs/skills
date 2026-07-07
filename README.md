# Software Factory

A personal collection of harness-engineering skills for [Claude Code](https://claude.com/claude-code), authored to the portable [Agent Skills](https://agentskills.io/specification) spec.

## Skills

| Skill | Description |
|-------|-------------|
| [adr](./skills/adr/SKILL.md) | Capture architecture decisions as [MADR](https://adr.github.io/madr/) records |
| [blindspots](./skills/blindspots/SKILL.md) | Predict how a task is most likely to go wrong before starting it, and the fix for each |
| [brand-voice](./skills/brand-voice/SKILL.md) | Interview to establish a brand's voice, scored on the [four tone-of-voice dimensions](https://www.nngroup.com/articles/tone-of-voice-dimensions/) |
| [commit](./skills/commit/SKILL.md) | Stage and commit changes using [Conventional Commits](https://www.conventionalcommits.org) |
| [six-thinking-hats](./skills/six-thinking-hats/SKILL.md) | Review or stress-test an idea from six parallel perspectives (de Bono's Six Thinking Hats) |
| [skill-evaluator](./skills/skill-evaluator/SKILL.md) | Measure a skill's value programmatically in a sandbox and track the score over time |
| [skill-linter](./skills/skill-linter/SKILL.md) | Deterministically lint a SKILL.md against the [Agent Skills](https://agentskills.io/specification) spec |

## Install

This repo is a [Claude Code plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces).
Add it, then install any skill from the table above by name:

```sh
/plugin marketplace add jamesmaggs/software-factory
/plugin install <skill>@software-factory   # e.g. commit@software-factory
```

## License

MIT — see [LICENSE](./LICENSE).
