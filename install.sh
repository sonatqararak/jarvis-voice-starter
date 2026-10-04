#!/usr/bin/env bash
# Stages this kit only. Does not install Herdr, change SSH config, or start services.
set -euo pipefail
umask 077
role="${1:-}"
case "$role" in vm|ubuntu|mac) ;; *) echo 'Usage: bash install.sh vm|ubuntu|mac [--speech]'; exit 2;; esac
src="$(cd "$(dirname "$0")" && pwd)"
dest="$HOME/.local/share/headless-kit"
conf="$HOME/.config/headless-kit"
command -v python3 >/dev/null || { echo 'Install Python 3.10+ first'; exit 1; }
python3 -c 'import sys; assert sys.version_info >= (3,10), "Python 3.10+ required"'
if [ "$role" = vm ]; then command -v herdr >/dev/null || { echo 'Install Herdr and put it on PATH first'; exit 1; }; fi
mkdir -p "$dest/bin" "$dest/mac" "$conf" "$HOME/.local/state/headless-kit"
for file in "$src"/bin/*; do [ -f "$file" ] && cp "$file" "$dest/bin/"; done
cp "$src"/mac/* "$dest/mac/"
mkdir -p "$dest/docs"
cp "$src/docs/index.html" "$dest/docs/"
cp "$src/requirements-speech.txt" "$dest/"
[ -f "$conf/kit.json" ] || cp "$src/config/kit.example.json" "$conf/kit.json"
if [ "$role" = vm ]; then
  hbin="$(command -v herdr)"
  python3 - "$conf/kit.json" "$hbin" <<'EOF'
import json,sys
from pathlib import Path
p=Path(sys.argv[1]);d=json.loads(p.read_text());d['herdr']=sys.argv[2];p.write_text(json.dumps(d,indent=2)+'\n')
EOF
  mkdir -p "$HOME/.config/systemd/user"
  cat > "$HOME/.config/systemd/user/headless-kit-herdr.service" <<'EOF'
[Unit]
Description=Headless Kit dedicated Herdr session
[Service]
ExecStart=/usr/bin/env python3 %h/.local/share/headless-kit/bin/server.py
Restart=on-failure
RestartSec=3
[Install]
WantedBy=default.target
EOF
  cat > "$HOME/.config/systemd/user/headless-kit-brain.service" <<'EOF'
[Unit]
Description=Headless Kit private Jarvis brain
After=headless-kit-herdr.service
Requires=headless-kit-herdr.service
[Service]
ExecStart=/usr/bin/env python3 %h/.local/share/headless-kit/bin/brain.py
Restart=on-failure
RestartSec=3
[Install]
WantedBy=default.target
EOF
  echo 'Staged. Review kit.json, then: systemctl --user daemon-reload'
  echo 'Start explicitly: systemctl --user enable --now headless-kit-herdr headless-kit-brain'
else
  if [ ! -x "$dest/.venv/bin/python" ]; then
    if [ "$role" = ubuntu ]; then python3 -m venv --system-site-packages "$dest/.venv"; else python3 -m venv "$dest/.venv"; fi
  fi
  if [ "${2:-}" = --speech ]; then "$dest/.venv/bin/python" -m pip install -r "$dest/requirements-speech.txt"; fi
  if [ "$role" = ubuntu ]; then
    mkdir -p "$HOME/.config/systemd/user"
    cat > "$HOME/.config/systemd/user/headless-kit-shell.service" <<'EOF'
[Unit]
Description=Headless Kit Ubuntu desktop shell
PartOf=graphical-session.target
After=graphical-session.target
[Service]
ExecStart=%h/.local/share/headless-kit/.venv/bin/python %h/.local/share/headless-kit/bin/linux_shell.py
Restart=on-failure
[Install]
WantedBy=graphical-session.target
EOF
    echo 'After reviewing kit.json and installing GTK: systemctl --user daemon-reload'
    echo 'From the desktop: systemctl --user import-environment DISPLAY WAYLAND_DISPLAY XAUTHORITY DBUS_SESSION_BUS_ADDRESS'
    echo 'Then: systemctl --user enable --now headless-kit-shell'
  else
    echo 'In your Hammerspoon init.lua, add the dofile line from README; reload it yourself.'
  fi
fi
printf 'Installed kit files in %s. Existing personal configuration preserved.\n' "$dest"
