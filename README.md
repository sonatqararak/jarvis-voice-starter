# Jarvis: your voice, your agents, your tools

A small self-hosted starter. Your desktop listens, your server routes agent requests, and your own accounts do the work.

**See it first:** [play the visual welcome](https://soyakaai-studio.github.io/jarvis-voice-starter/). No account or installation is needed to explore it. Explore how my personal Jarvis connects stored knowledge, AI agents and desktop apps. The animated overview uses illustrative commands and screens. You can also open `docs/index.html` locally.

[Preview the unpublished X and LinkedIn drafts on your phone](https://soyakaai-studio.github.io/jarvis-voice-starter/social-preview.html) · [Download the source ZIP](https://github.com/soyakaai-studio/jarvis-voice-starter/archive/refs/heads/main.zip)

**Make it yours:** use this repository as a template or download its source. The starter uses push-to-talk, not an always-on wake word. No proprietary wake-word model, cloud classifier, customer connector or private deployment is included.

## Three useful first actions

| Say or type | What happens |
|---|---|
| `open app Safari` | Mac opens Safari locally. |
| `tell Research to write a three-line welcome note` | Review the prompt, then send it to your idle Research agent. |
| `status` | Your server reports the state of your Herdr panes. |

On Mac, focus a notes app and use Ctrl+Alt+D to dictate. Review the text, then paste it; Enter is not pressed. Ctrl+Alt+Space listens for one command. Ctrl+Alt+J opens typed commands. Ctrl+Alt+Escape hides the orb.

## Start here

1. [Mac first: get the orb and one desktop action](docs/START-HERE.md#mac-first).
2. [Connect your own Ubuntu server and agent](docs/START-HERE.md#add-your-server).
3. [Add local speech](docs/START-HERE.md#add-your-voice).

Follow [the detailed setup](docs/ADVANCED-SETUP.md) only when needed. Do not run installers on a machine you cannot administer.

## What is and is not included

Included: typed commands, optional local speech, an animated Mac galaxy shell, reviewed dictation, simple Mac app opening, server pane status/focus, prompt delivery with confirmation, and guarded session helpers. Ubuntu's shell is experimental and has a simple GTK interface, not the Mac galaxy UI. The visual welcome demo describes a broader personal system; it is not a guarantee that every feature is in this starter.

Not included: natural-language cloud routing, client knowledge-base access, System One, long-term memory, automatic page discovery from agent results, spoken replies, or model training. `open guide` opens the bundled local demo, not a dynamically discovered agent page.

The code can send prompts to your provider-backed agents after your confirmation. Local speech does not imply those agents are local. Set up your own provider accounts and understand their data settings.

## Validation

See [validation](VALIDATION.md) for the latest checks and remaining acceptance work. Passing source tests does not prove microphone, permissions, GTK, Hammerspoon or a real agent works on your computer. Try a fictional task first.

See [what the starter accesses](SAFETY.md) before connecting your own agents. The phone walkthrough is interactive; installing the assistant requires a Mac or Ubuntu computer and some setup.

## Reuse and credits

Starter code and bundled demo: MIT. Third-party dependencies keep their own licenses and are not bundled. [Herdr](https://herdr.dev/docs/install/), [Hammerspoon](https://www.hammerspoon.org/), faster-whisper, and the listed speech packages are installed separately.

## Remove it

Stop the dedicated `headless-kit-brain`, `headless-kit-herdr`, and optional `headless-kit-shell` user services. Call `shareKitJarvis.stop()` in Hammerspoon, remove the single dofile line you added, and reload. Review and remove only this kit's installed files, configuration and dedicated unit files. Preserve your project files, accounts and agent histories.
