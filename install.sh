#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
target_dir="${CODEX_SKILLS_DIR:-${CODEX_HOME:-$HOME/.codex}/skills}"
source_dir_name="skills"
force=0
claude=0

usage() {
  printf '%s\n' "Usage: CODEX_SKILLS_DIR=/path/to/skills ./install.sh [--force]"
  printf '%s\n' "       CLAUDE_SKILLS_DIR=/path/to/skills ./install.sh --claude [--force]"
  printf '%s\n' "Default target: ${target_dir} (--claude: ${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills})"
}

while (($#)); do
  case "$1" in
    --force)
      force=1
      shift
      ;;
    --claude)
      claude=1
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
  aside-workflow
  general-review-loop
  pair-agent-sync
  project-outline-update
  route-developer-review
  refresh-repo-status
  third-party-codex-updater
  video-to-md
)

if [[ "$claude" -eq 1 ]]; then
  source_dir_name="claude-skills"
  target_dir="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
  skills=(
    goose-bridge
    third-party-claude-updater
  )
fi

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
  source_dir="${repo_root}/${source_dir_name}/${skill}"
  destination="${target_dir}/${skill}"
  if [[ -e "$destination" ]]; then
    rm -rf "$destination"
  fi
  cp -R "$source_dir" "$destination"
  printf 'Installed %s -> %s\n' "$skill" "$destination"
done
