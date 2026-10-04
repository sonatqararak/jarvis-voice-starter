# Your first five minutes

## Mac first

You need Python 3.10+ and [Hammerspoon](https://www.hammerspoon.org/). Install them yourself from their official sources. Download this repository, open Terminal in the downloaded folder, and run:

```bash
bash install.sh mac
```

The installer stages this kit in your user account and creates its own Python environment. It does not overwrite Hammerspoon or SSH configuration or start server services.

Add this one line to your existing Hammerspoon `init.lua`:

```lua
shareKitJarvis = dofile(os.getenv('HOME') .. '/.local/share/headless-kit/mac/jarvis.lua')
```

Reload Hammerspoon and grant Accessibility permission yourself. Press Ctrl+Alt+J. Type `open app Safari`. Your browser should open and the galaxy shell should show the result. `open guide` opens the visual explanation. This first action does not require a server or an AI account.

## Add your server

You need an Ubuntu machine you control, SSH access, Python 3.10+, and [Herdr](https://herdr.dev/docs/install/). You also need your own agent CLI and account if you want an agent to do a task. The server can be another computer or a VM; this kit does not provision one.

1. Make your own SSH alias from `config/ssh.example`. Verify its host-key fingerprint through a trusted channel. Test SSH yourself.
2. Copy this repository to your Ubuntu server. Run `bash install.sh vm` there.
3. Review `~/.config/headless-kit/kit.json`. Start the dedicated services explicitly:

```bash
systemctl --user daemon-reload
systemctl --user enable --now headless-kit-herdr headless-kit-brain
python3 ~/.local/share/headless-kit/bin/doctor.py vm
```

4. On your Mac, edit `~/.config/headless-kit/kit.json`: replace `YOUR_VM_SSH_ALIAS` with your own alias. Reload Hammerspoon.
5. Attach from your desktop:

```bash
herdr --remote YOUR_VM_SSH_ALIAS --session share-kit --remote-keybindings server
```

Create a pane labelled exactly `Research`, and start your own agent in it. Wait until it is idle. In Jarvis, type `tell Research to write a three-line welcome note`. Check the destination and prompt in the confirmation dialog. The result appears in your agent pane; the orb only confirms delivery. Type `status` to inspect pane states.

To keep services alive after logout, the VM owner can enable user lingering; see ADVANCED-SETUP.md. Check reconnect and persistence on your machine rather than assuming them.

## Add your voice

On your Mac, from the repository folder:

```bash
bash install.sh mac --speech
```

This downloads speech dependencies. The first microphone use downloads the Whisper model and can take longer than later uses. Grant microphone permission yourself. Press Ctrl+Alt+Space and say `status`. Push-to-talk ends after a pause. Always-on wake-word detection is not enabled.

For dictation, focus your destination app, press Ctrl+Alt+D, speak, then review the text before clicking Paste. The starter changes the clipboard to that text and never presses Enter. Avoid password fields and private examples while testing.

## If it does not work

Start with typed `open app Safari`. If it works but voice does not, check the speech environment, model download and microphone permissions. If desktop actions work but server commands fail, check your SSH alias, dedicated services and pane labels. `doctor.py desktop` checks basic desktop configuration; `doctor.py vm` checks server prerequisites. Neither establishes end-to-end acceptance.

Ubuntu: follow the Ubuntu instructions in ADVANCED-SETUP.md. Its GTK shell is experimental; desktop behavior varies with the display system.
