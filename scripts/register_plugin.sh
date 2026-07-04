#!/usr/bin/env bash
#
# register_plugin.sh
#
# Wires a skill into the plugin marketplace: writes its
# skills/<name>/.claude-plugin/plugin.json manifest and upserts the matching
# entry in .claude-plugin/marketplace.json. Deterministic and idempotent —
# re-running with the same inputs leaves both files byte-identical, and the
# marketplace entries are always sorted by name.
#
# Usage:
#   bash scripts/register_plugin.sh <skill-name> ["<description>"]
#
# The description is the short, human-facing summary shown in the marketplace
# (distinct from the model-facing SKILL.md description). If omitted, the current
# plugin.json's description is reused, so the command doubles as a re-sync.
#
# Exit codes:
#   0 = success
#   1 = one or more errors
#   2 = usage error / missing skill

set -euo pipefail

# Repo-wide manifest constants.
AUTHOR_NAME="James Maggs"
LICENSE="MIT"
REPOSITORY="https://github.com/jamesmaggs/software-factory"
DEFAULT_VERSION="0.1.0"

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(dirname "$SCRIPT_DIR")
MARKETPLACE="$ROOT/.claude-plugin/marketplace.json"

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
  echo "Usage: bash scripts/register_plugin.sh <skill-name> [\"<description>\"]" >&2
  exit 2
fi

NAME="$1"
SKILL_DIR="$ROOT/skills/$NAME"
MANIFEST="$SKILL_DIR/.claude-plugin/plugin.json"

if ! command -v jq >/dev/null 2>&1; then
  echo "Error: jq is required but not installed." >&2
  exit 1
fi
if [ ! -f "$SKILL_DIR/SKILL.md" ]; then
  echo "Error: no skill at skills/$NAME (expected skills/$NAME/SKILL.md)." >&2
  exit 2
fi
if [ ! -f "$MARKETPLACE" ]; then
  echo "Error: marketplace file not found: $MARKETPLACE" >&2
  exit 1
fi

# Resolve the description: explicit argument wins; otherwise reuse the manifest's.
if [ "$#" -eq 2 ]; then
  DESC="$2"
elif [ -f "$MANIFEST" ]; then
  DESC=$(jq -r '.description // ""' "$MANIFEST")
else
  echo "Error: no description given and no existing manifest to reuse." >&2
  echo "       Pass one: bash scripts/register_plugin.sh $NAME \"<description>\"" >&2
  exit 2
fi
if [ -z "$DESC" ]; then
  echo "Error: description must not be empty." >&2
  exit 2
fi

# Preserve an existing manifest version; new manifests start at the default.
if [ -f "$MANIFEST" ]; then
  VERSION=$(jq -r ".version // \"$DEFAULT_VERSION\"" "$MANIFEST")
else
  VERSION="$DEFAULT_VERSION"
fi

# Write the plugin.json manifest.
mkdir -p "$SKILL_DIR/.claude-plugin"
jq -n \
  --arg name "$NAME" \
  --arg description "$DESC" \
  --arg version "$VERSION" \
  --arg author "$AUTHOR_NAME" \
  --arg license "$LICENSE" \
  --arg repository "$REPOSITORY" \
  '{name: $name, description: $description, version: $version,
    author: {name: $author}, license: $license, repository: $repository}' \
  > "$MANIFEST"

# Upsert the marketplace entry, then sort all entries by name.
TMP=$(mktemp)
jq \
  --arg name "$NAME" \
  --arg source "./skills/$NAME" \
  --arg description "$DESC" \
  '.plugins |= (map(select(.name != $name))
                + [{name: $name, source: $source, description: $description}]
                | sort_by(.name))' \
  "$MARKETPLACE" > "$TMP"
mv "$TMP" "$MARKETPLACE"

echo "Registered '$NAME' -> $MANIFEST and $MARKETPLACE"
