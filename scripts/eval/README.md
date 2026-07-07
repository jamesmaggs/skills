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
- **Model policy:** default **haiku** (cheapest, where a skill adds the most value); **sonnet**
  is the ceiling; **opus is rejected**.

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
