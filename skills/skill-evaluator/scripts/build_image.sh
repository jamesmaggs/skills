#!/usr/bin/env bash
#
# build_image.sh — build the sandbox image once (or after editing the Dockerfile).
# Run this before the first eval run.
#
# Usage: bash build_image.sh
# Override the tag with SKILL_EVAL_IMAGE=my-tag bash build_image.sh

set -euo pipefail

IMAGE="${SKILL_EVAL_IMAGE:-skill-eval-sandbox}"
HERE="$(cd "$(dirname "$0")" && pwd)"

if ! docker info >/dev/null 2>&1; then
  echo "Error: the Docker daemon is not running. Start Docker and retry." >&2
  exit 1
fi

echo "Building sandbox image '$IMAGE'…"
docker build -t "$IMAGE" "$HERE/sandbox"
echo "Done. Sanity check: docker run --rm -e ANTHROPIC_API_KEY=dummy $IMAGE --version"
