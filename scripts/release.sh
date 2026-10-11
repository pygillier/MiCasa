#!/usr/bin/env bash
# Usage: scripts/release.sh <patch|minor|major|X.Y.Z> [--dry-run]
# Bumps the version in backend/pyproject.toml and frontend/package.json,
# commits, and creates the annotated git tag vX.Y.Z. Does not push.
set -euo pipefail
cd "$(dirname "$0")/.."

bump="${1:-}"
dry="${2:-}"
[[ -n "$bump" ]] || { echo "usage: $0 <patch|minor|major|X.Y.Z> [--dry-run]" >&2; exit 2; }

current=$(git describe --tags --abbrev=0 --match 'v[0-9]*.[0-9]*.[0-9]*' 2>/dev/null || echo v0.0.0)
IFS=. read -r major minor patch <<<"${current#v}"

case "$bump" in
  patch) next="$major.$minor.$((patch + 1))" ;;
  minor) next="$major.$((minor + 1)).0" ;;
  major) next="$((major + 1)).0.0" ;;
  *)
    [[ "$bump" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || { echo "invalid version: $bump" >&2; exit 2; }
    next="$bump"
    ;;
esac
tag="v$next"

echo "$current -> $tag"
[[ "$dry" == "--dry-run" ]] && exit 0

git rev-parse -q --verify "refs/tags/$tag" >/dev/null && { echo "tag $tag already exists" >&2; exit 1; }
[[ -z "$(git status --porcelain)" ]] || { echo "working tree is not clean" >&2; exit 1; }

sed -i -E "0,/^version = \".*\"/s//version = \"$next\"/" backend/pyproject.toml
(cd backend && uv lock --offline >/dev/null 2>&1 || uv lock >/dev/null)
(cd frontend && npm version "$next" --no-git-tag-version --allow-same-version >/dev/null)

git add backend/pyproject.toml backend/uv.lock frontend/package.json frontend/package-lock.json
git commit -m "Release $tag"
git tag -a "$tag" -m "Release $tag"

echo "Created $tag. Publish with: git push --follow-tags"
