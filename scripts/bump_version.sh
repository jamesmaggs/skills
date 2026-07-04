#!/usr/bin/env bash
#
# bump_version.sh
#
# Bumps a skill's semantic version in skills/<name>/.claude-plugin/plugin.json.
# Deterministic: reads the current MAJOR.MINOR.PATCH, increments the requested
# part (resetting the lower parts), and writes it back in place, preserving the
# manifest's key order and formatting.
#
# Usage:
#   bash scripts/bump_version.sh <skill-name> <major|minor|patch>
#
#   major  breaking change to the skill's behaviour or output contract
#   minor  new backward-compatible capability
#   patch  fixes, wording, and other backward-compatible tweaks
#
# Exit codes:
#   0 = success
#   1 = one or more errors
#   2 = usage error / missing skill or manifest

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(dirname "$SCRIPT_DIR")

if [ "$#" -ne 2 ]; then
  echo "Usage: bash scripts/bump_version.sh <skill-name> <major|minor|patch>" >&2
  exit 2
fi

NAME="$1"
PART="$2"
SKILL_DIR="$ROOT/skills/$NAME"
MANIFEST="$SKILL_DIR/.claude-plugin/plugin.json"

if ! command -v jq >/dev/null 2>&1; then
  echo "Error: jq is required but not installed." >&2
  exit 1
fi
case "$PART" in
  major|minor|patch) ;;
  *) echo "Error: part must be one of major, minor, patch (got \"$PART\")." >&2; exit 2 ;;
esac
if [ ! -f "$SKILL_DIR/SKILL.md" ]; then
  echo "Error: no skill at skills/$NAME (expected skills/$NAME/SKILL.md)." >&2
  exit 2
fi
if [ ! -f "$MANIFEST" ]; then
  echo "Error: no manifest at $MANIFEST." >&2
  echo "       Create it first: bash scripts/register_plugin.sh $NAME \"<description>\"" >&2
  exit 2
fi

CURRENT=$(jq -r '.version // ""' "$MANIFEST")
if ! printf '%s' "$CURRENT" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+$'; then
  echo "Error: current version \"$CURRENT\" is not a MAJOR.MINOR.PATCH semver." >&2
  exit 1
fi

IFS=. read -r MAJ MIN PAT <<EOF
$CURRENT
EOF

case "$PART" in
  major) MAJ=$((MAJ + 1)); MIN=0; PAT=0 ;;
  minor) MIN=$((MIN + 1)); PAT=0 ;;
  patch) PAT=$((PAT + 1)) ;;
esac
NEW="$MAJ.$MIN.$PAT"

TMP=$(mktemp)
jq --arg v "$NEW" '.version = $v' "$MANIFEST" > "$TMP"
mv "$TMP" "$MANIFEST"

echo "Bumped '$NAME' ($PART): $CURRENT -> $NEW"
