# Validation — 4 October 2026

18 automated tests passed on the separate build machine (Python 3.14.7). Tests cover Unix-socket request transport, exact pane matching, refusal of busy or ambiguous targets, reviewed prompt delivery, literal text handling, guarded park/restore and installer staging in a temporary directory. Bash syntax and both Lua files were checked; Lua parsing used luaparse 0.3.1 in Lua 5.3 mode. The visual demo was inspected in a browser.

A scan of the packaged text files found no IP literals, email addresses, provider tokens, private key blocks, assigned secrets, personal absolute paths or session UUIDs. This scan supplements a source allowlist; it is not proof that arbitrary future contributions are safe.

Phone-review revision: the public post preview is bundled with the welcome page. The same 18 tests passed again; both page scripts and both Lua files parsed. Microphone command errors now release the busy flag so the user can retry. The public handle and links use `soyakaai-studio`.

## Still unverified

Fresh speech dependency resolution, real microphone use, OS permissions, real Hammerspoon rendering, Ubuntu GTK behavior and real-provider task submission have not been exercised in this packaging run. These are recipient-machine acceptance steps, not completed tests. No services or permissions were changed on the owner's live system.

The source starter is intentionally smaller than the owner's personal setup. Push-to-talk is supported; always-on wake-word detection and cloud interpretation are not included. Dependencies and model files are installed by the recipient under their own licenses.

Run `python3 -m unittest discover -s tests -v` before modifying the starter. Test with fictional tasks and your own accounts.
