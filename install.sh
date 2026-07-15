#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
target_dir="${CODEX_SKILLS_DIR:-${CODEX_HOME:-$HOME/.codex}/skills}"
force=0

usage() {
  printf '%s\n' "Usage: CODEX_SKILLS_DIR=/path/to/skills ./install.sh [--force]"
  printf '%s\n' "Default target: ${target_dir}"
}

while (($#)); do
  case "$1" in
    --force)
      force=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      printf 'Unknown option: %s\n' "$1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

skills=(
  team-based-review-loop
  route-developer-review
  third-party-codex-updater
)

for skill in "${skills[@]}"; do
  destination="${target_dir}/${skill}"
  if [[ -e "$destination" && "$force" -ne 1 ]]; then
    printf 'Refusing to overwrite existing skill: %s\n' "$destination" >&2
    printf 'Use --force only after reviewing the local copy.\n' >&2
    exit 3
  fi
done

mkdir -p "$target_dir"
for skill in "${skills[@]}"; do
  source_dir="${repo_root}/skills/${skill}"
  destination="${target_dir}/${skill}"
  if [[ -e "$destination" ]]; then
    rm -rf "$destination"
  fi
  cp -R "$source_dir" "$destination"
  printf 'Installed %s -> %s\n' "$skill" "$destination"
done
