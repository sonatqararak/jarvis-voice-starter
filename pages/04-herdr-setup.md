# Headless chats in Herdr

Install Herdr on your own VM and desktop. Keep the versions compatible. The kit's syntax was checked against Herdr 0.9.3. Install and authenticate the agent CLIs on the VM yourself.

Stage the kit on the VM with `bash install.sh vm`. Review its config, then start the dedicated Herdr and brain services using the commands in README. Enable user lingering if you want those services to survive SSH logout; that may need the VM administrator.

From your terminal, attach with:

```bash
herdr --remote YOUR_VM_SSH_ALIAS --session share-kit --remote-keybindings server
```

Create a couple of panes, name them uniquely, and launch your own agents. Close and reopen the terminal to verify persistence.

Parking is different from closing the terminal: it exits an idle agent process. Before parking, use the sessions helper to register that agent's real session ID and project folder. Restore resumes that same registered session and leaves login/trust prompts for you. It refuses busy agents and unverified foreground processes. There is no automatic bulk wake on boot.

Focus zooms one pane. The explicit layout helper can put two or three named panes into a row. Your project files and agent histories stay on the VM; the kit never imports another person's sessions.
