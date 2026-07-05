#!/usr/bin/env bash
#
# run_docker.sh — the sandbox seam. Runs exactly ONE `claude -p` invocation
# inside an ephemeral container and writes its stream-json trace to a file.
#
# The orchestrator (run_evals.py) calls this once per configuration per case.
# Swapping this file for run_seatbelt.sh / a CI backend is the only change
# needed to move the sandbox; the orchestrator treats it as a black box.
#
# Usage:
#   run_docker.sh --workdir DIR --prompt TEXT --out TRACE.jsonl \
#                 [--skill PLUGIN_DIR] [--model NAME] [--system-hint TEXT]
#
# Contract:
#   - DIR is mounted at /work (read-write, ephemeral) and is the only host path
#     the container can touch. Inspect DIR afterwards for outcome checks.
#   - With --skill, the plugin dir is mounted read-only at /skill and loaded via
#     --plugin-dir; without it, the run is a clean baseline (no skill available).
#   - The full stream-json trace goes to TRACE.jsonl; container stderr to
#     TRACE.jsonl.err for debugging.
#   - Requires ANTHROPIC_API_KEY in the environment (passed into the container).
#
# Exit codes: 0 = ran (grade the trace to judge pass/fail); 2 = usage/setup error.

set -euo pipefail

IMAGE="${SKILL_EVAL_IMAGE:-skill-eval-sandbox}"
WORKDIR="" PROMPT="" OUT="" SKILL="" MODEL="" SYS_HINT="" NAME=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --workdir)      WORKDIR="$2"; shift 2 ;;
    --prompt)       PROMPT="$2"; shift 2 ;;
    --out)          OUT="$2"; shift 2 ;;
    --skill)        SKILL="$2"; shift 2 ;;
    --model)        MODEL="$2"; shift 2 ;;
    --system-hint)  SYS_HINT="$2"; shift 2 ;;
    --name)         NAME="$2"; shift 2 ;;
    *) echo "run_docker.sh: unknown arg: $1" >&2; exit 2 ;;
  esac
done

if [ -z "$WORKDIR" ] || [ -z "$PROMPT" ] || [ -z "$OUT" ]; then
  echo "Usage: run_docker.sh --workdir DIR --prompt TEXT --out FILE [--skill DIR] [--model NAME] [--system-hint TEXT]" >&2
  exit 2
fi
if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
  echo "run_docker.sh: ANTHROPIC_API_KEY is not set — the sandboxed claude cannot authenticate." >&2
  exit 2
fi
if [ ! -d "$WORKDIR" ]; then
  echo "run_docker.sh: workdir not found: $WORKDIR" >&2
  exit 2
fi

# Build the docker argv. CLAUDECODE is cleared so the nested claude does not
# think it is inside the outer Claude Code session.
docker_args=(
  run --rm
  -v "$WORKDIR:/work" -w /work
  -e "ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY"
  -e "CLAUDECODE="
)
[ -n "$NAME" ] && docker_args+=(--name "$NAME")
[ -n "$SKILL" ] && docker_args+=(-v "$SKILL:/skill:ro")
docker_args+=("$IMAGE")

# Args passed to the `claude` entrypoint.
claude_args=(
  -p "$PROMPT"
  --bare
  --output-format stream-json
  --verbose
  --include-partial-messages
  --permission-mode bypassPermissions
)
[ -n "$MODEL" ]    && claude_args+=(--model "$MODEL")
[ -n "$SKILL" ]    && claude_args+=(--plugin-dir /skill)
[ -n "$SYS_HINT" ] && claude_args+=(--append-system-prompt "$SYS_HINT")

docker "${docker_args[@]}" "${claude_args[@]}" > "$OUT" 2> "$OUT.err"
