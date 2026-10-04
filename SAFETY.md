# What you are installing

The phone walkthrough is a demonstration. It does not use your microphone, connect to a server or run an agent task.

The downloadable starter contains source code and example configuration. It contains no owner deployment, account credentials, client records, chat histories, audio recordings or private memory. The portrait and public profile links in the post preview are intentionally public.

## Your first action

Start with typed `open app Safari` on Mac. This opens a local app. It needs no cloud model or server. Add speech and a server only when this works.

## What the real starter can access

- Hammerspoon can control your Mac after you grant its Accessibility permission. The local app-opening command permits Safari, Notes and Terminal.
- Push-to-talk transcribes your microphone locally. The speech dependencies and model must be downloaded first.
- Dictation changes your clipboard and pastes reviewed text into the application you focused. It does not press Enter.
- Agent delivery uses your SSH alias and a private Unix socket. It requires a unique, idle agent pane and shows the target and prompt before sending. Your own agent may use cloud models and may act with the permissions you gave it.
- Park/restore helpers can interrupt a registered idle agent or resume its saved session. Start with a dedicated test pane and fictional data.

The installer stages dedicated kit files and preserves existing kit configuration. It does not rewrite your SSH or Hammerspoon configuration, grant permissions or automatically start server services. SSH host-key checking stays enabled in the example.

This starter does not include the owner's Jev integration, client connectors, private memory, always-on wake-word model or automatic discovery of agent-created pages. It is an early source starter, not a verified one-click replica of the personal system.

The public files passed a secret-pattern scan and source tests. Real microphone, desktop and provider acceptance remain to be tested on the recipient's own machine. Read START-HERE and VALIDATION for those checks.
