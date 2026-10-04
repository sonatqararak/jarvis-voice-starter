# Jarvis: start with typing, then add your microphone

Jarvis here is a small desktop front door to the VM. The kit's README has the full commands. First confirm ordinary SSH and Herdr attachment work.

On the VM, run `bash install.sh vm`, review the configuration and explicitly start the two dedicated user services. On the desktop, run `bash install.sh mac` or `bash install.sh ubuntu`, then put your own SSH alias in the local configuration.

Mac uses Hammerspoon. Add the kit's dofile line to your existing init.lua and reload it. Ctrl+Alt+J opens a command box, Ctrl+Alt+P opens a paste box, and Ctrl+Alt+Space listens locally. Ubuntu uses GTK; add GNOME shortcuts to the supplied ui-command helper.

Try `status`, `go to Research`, `focus Research`, and `unfocus`, using your own exact pane label. Status produces a banner on request. The paste box inserts reviewed text into an idle agent without submitting it.

For speech, re-run the desktop installer with `--speech`. The first use downloads a local Whisper model. Grant OS microphone permissions yourself. Wake word stays off in the starter; always-on listening needs a later integration. Ubuntu includes stop-controlled dictation into the review box; Mac's starter supports one spoken command at a time.

The packaging tests did not exercise real microphones or desktop permissions. Complete those checks on your own machines before relying on voice.
