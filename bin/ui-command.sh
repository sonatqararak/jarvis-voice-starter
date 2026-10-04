#!/usr/bin/env bash
set -euo pipefail
mkdir -p "$HOME/.config/headless-kit"
case "${1:-show}" in show|listen|dictate) ;; *) exit 2;; esac
printf '%s\n' "${1:-show}" >> "$HOME/.config/headless-kit/ui-command"
chmod 600 "$HOME/.config/headless-kit/ui-command"
