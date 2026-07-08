# Eval runner (local infra — not portable)

This is the automated backend for the portable `skill-evaluator` skill. The **skill**
describes how to evaluate any skill in any harness; **this runner** is one concrete
implementation, bound to Claude Code + Anthropic, that executes the value runs in a Docker
sandbox so scores can be tracked over time (CI, dashboards). It consumes the portable eval
spec defined in [`skills/skill-evaluator/references/eval-spec.md`](../../skills/skill-evaluator/references/eval-spec.md).

Being non-portable is fine here — it is repo infrastructure, not a shipped skill.

## Prerequisites

- Docker daemon running, and the sandbox image built once: `bash scripts/eval/build_image.sh`.
- `ANTHROPIC_API_KEY` for the **sandboxed** runs — export it or put `ANTHROPIC_API_KEY=sk-...`
  in a gitignored `.env` at the repo root (loaded automatically; override with `--env-file`).
  These runs bill against **API credits**, which a Claude subscription does not include.
- The **rubric grader** runs on the host and uses your **subscription** by default; pass
  `--grader-auth apikey` in CI where no subscription exists.
- **Model policy:** default **sonnet** (a reliable middle ground for triggering and value);
  **haiku** is allowed (cheaper, but under-triggers); **opus is rejected**.

## Trust boundary

The sandbox is hardened (dropped capabilities, no privilege escalation, read-only root
filesystem, CPU/memory/pid limits) and the host side refuses path traversal in fixtures and
check paths, caps file reads, and runs the grader with no tools, no MCP, and empty settings.
**But the container needs network to reach the API and the key lives inside it**, so a
hostile skill with network access could exfiltrate it. As shipped, evaluate **skills you
trust**; running genuinely untrusted skills safely would need an egress-restricting proxy
that keeps the key out of the container.

## Usage

```sh
python3 scripts/eval/validate_spec.py --skill <skill-dir>      # check a spec against the format
bash    scripts/eval/build_image.sh                            # build the sandbox image once
python3 scripts/eval/run_evals.py --skill <skill-dir> [--model haiku|sonnet] [--json]
```

`run_evals.py` runs each triggering row with the skill available (does it fire?) and each
outcome case twice — with the skill's guidance injected, and at baseline — appending one
line per run to `<skill-dir>/evals/results/history.jsonl`. Use `--dry-run` first.

## Limitations — what this harness can't measure

This harness measures skills whose value is **inline, single-call behaviour on a
discriminating task** — it runs one `claude -p` per config in the sandbox and grades the
result. Skills whose value lies elsewhere don't get an honest `value_delta` here, and
should not carry an eval spec that fakes one. The classes we've hit, with the skills that
fall in each:

- **Deterministic tools** (`skill-linter`) — the skill's worth is a bundled script whose
  checks a capable baseline reproduces by direct measurement. The only "lift" is a
  ran-our-tool artifact (a presence-not-correctness trap), not a real outcome gap. Its
  correctness belongs in script-level tests. *(This one is harness-agnostic — a
  deterministic tool resists value-delta in any harness.)*
- **Multi-agent orchestrators** (`six-thinking-hats`) — the skill delegates to parallel
  sub-agents, whose output is not captured in the single main-agent trace the grader reads,
  so the with-skill run looks truncated/incomplete.
- **Bundled-asset / interactive skills** (`brand-voice`, partly) — the sandbox ships only
  `SKILL.md` text, not the skill's `references/`, `scripts/`, or `assets/`, and there is no
  back-and-forth. `brand-voice` is evaluable only by front-loading the whole brief and
  testing the "produce a structured, persisted guide" slice, not its real value (the
  interview).
- **The evaluator itself** (`skill-evaluator`) — self-referential, and it combines the two
  failure modes above: its run flow needs sub-agents (uncaptured), and its author flow needs
  the bundled `references/eval-spec.md` (absent in the sandbox).

Skills currently with a measured spec: `adr`, `blindspots`, `brand-voice`, `commit`.
