# Things that save a lot of frustration

Get ordinary SSH and terminal attachment working before adding voice. A working orb does not prove the VM brain or agent login is ready.

Give each pane a unique name. The starter uses exact labels rather than guessing between similar projects. Treat “unknown” agent status as unknown, not as permission to paste or park.

Use matching Herdr versions. Read the help for your installed version if a flag differs. Closing a terminal should leave VM agents alive; a VM reboot needs the dedicated services and separate agent resumption.

On Ubuntu Wayland, hotkeys, overlays and screenshots have restrictions. Use GNOME custom shortcuts. The starter uses a normal GTK window. In a nested Mac VM, some key combinations may be intercepted; choose a shortcut that actually reaches the guest.

Clipboard support varies by terminal. Test a harmless selection in your own terminal. In our source setup, a lightweight Wayland terminal worked better than a graphics-heavy terminal inside a VM; that is a starting point for testing, not a guarantee for your hardware.

Keep wake listening off when two desktops share one microphone. Model downloads and microphone permissions can take longer than the terminal setup. Speech can mishear a pane name; test with synthetic projects first.

Register the actual agent session before parking. Restoring the wrong account, folder or session ID can fail or open the wrong work. Never copy somebody else's history just to make restore work.

Paste does not press Enter. Review the target and text in the agent terminal before submitting. Status banners are on demand; automatic completion notifications and the original animated artwork are future extensions.
