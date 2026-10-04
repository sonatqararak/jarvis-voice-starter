#!/usr/bin/env python3
"""Local speech listener. READY/HEARD on stdout; LISTEN/DICTATE/STOP in the command file."""
import os, shutil, subprocess, sys, time, wave
import numpy as np

WAKE_MODE = "--nowake" not in sys.argv
RATE, FRAME = 16000, 1280                     # the models want 16 kHz, 80 ms frames
WAKE_THRESHOLD, COOLDOWN = 0.5, 4.0
PAUSE_S, NO_SPEECH_S, MAX_S = 0.9, 5.0, 15.0  # finish 0.9 s after he stops talking
CONF = os.path.expanduser("~/.config/headless-kit")
CMD = os.path.join(CONF, "cmd")
VOCAB = os.path.expanduser("~/.local/share/headless-kit/vocabulary.txt")   # optional local vocabulary supplied by you


def say(msg):
    print(msg, flush=True)


class FileMic:
    """Replays a wav (tests). After the file: silence, and exit once JARVIS_MIC_TAIL seconds of it have passed."""
    def __init__(self, path):
        w = wave.open(path)
        assert w.getframerate() == RATE and w.getnchannels() == 1 and w.getsampwidth() == 2, "need 16 kHz mono s16"
        self.data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
        self.pos, self.tail = 0, float(os.environ.get("JARVIS_MIC_TAIL", "8"))
        self.name = "file"
    def __enter__(self): return self
    def __exit__(self, *a): return False
    def read(self, n):
        chunk = self.data[self.pos:self.pos + n]; self.pos += n
        if len(chunk) < n:
            if os.environ.get("JARVIS_MIC_STOP_AT_END") and not getattr(self, "stopped", False):
                self.stopped = True                       # tests: "he presses again" when the recording ends
                with open(CMD, "a") as f:
                    f.write("STOP\n")
            if self.pos - len(self.data) > self.tail * RATE:
                say("MICEND"); sys.exit(0)
            chunk = np.pad(chunk, (0, n - len(chunk)))
        if os.environ.get("JARVIS_MIC_REALTIME"):
            time.sleep(n / RATE)
        return chunk.reshape(-1, 1), False


class PipeMic:
    """pw-record / parec writing raw s16le 16 kHz mono to a pipe: the sound server resamples, the device keeps
    its own rate (the Mac lesson of 29 Sep 2026: forcing 16 kHz on the device broke other recorders)."""
    def __init__(self, argv, name):
        self.argv, self.name, self.p = argv, name, None
    def __enter__(self):
        self.p = subprocess.Popen(self.argv, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=0)
        return self
    def __exit__(self, *a):
        if self.p:
            self.p.kill(); self.p.wait()
        return False
    def read(self, n):
        want, buf = n * 2, b""
        while len(buf) < want:
            got = self.p.stdout.read(want - len(buf))
            if not got:
                raise RuntimeError(f"{self.name} stopped")
            buf += got
        return np.frombuffer(buf, dtype=np.int16).reshape(-1, 1), False


class SoundDeviceMic:
    """PortAudio at the device's native rate, resampled here (same as the Mac's MicStream)."""
    def __init__(self):
        import sounddevice as sd
        from math import gcd
        self.sd, self.name = sd, "portaudio"
        self.native = int(sd.query_devices(kind="input")["default_samplerate"]) or RATE
        self.g = gcd(RATE, self.native)
        self.nf = FRAME * self.native // RATE
        self.s = sd.InputStream(samplerate=self.native, channels=1, dtype="float32", blocksize=self.nf)
    def __enter__(self):
        self.s.__enter__(); return self
    def __exit__(self, *a):
        return self.s.__exit__(*a)
    def read(self, _n):
        from scipy.signal import resample_poly
        data, overflow = self.s.read(self.nf)
        mono = data[:, 0] if self.native == RATE else resample_poly(data[:, 0], RATE // self.g, self.native // self.g)
        out = np.clip(mono[:FRAME] * 32767, -32768, 32767).astype(np.int16)
        if len(out) < FRAME:
            out = np.pad(out, (0, FRAME - len(out)))
        return out.reshape(-1, 1), overflow


def open_mic():
    if os.environ.get("JARVIS_MIC_FILE"):
        return FileMic(os.environ["JARVIS_MIC_FILE"])
    order = os.environ.get("JARVIS_MIC", "portaudio,pipewire,pulse").split(",")
    for b in order:
        try:
            if b == "portaudio":
                return SoundDeviceMic()
            if b == "pipewire" and shutil.which("pw-record"):
                return PipeMic(["pw-record", "--rate", str(RATE), "--channels", "1", "--format", "s16",
                                "--latency", "80ms", "-"], "pipewire")
            if b == "pulse" and shutil.which("parec"):
                return PipeMic(["parec", "--raw", "--format=s16le", f"--rate={RATE}", "--channels=1",
                                "--latency-msec=80"], "pulse")
        except Exception as e:                   # e.g. OSError: PortAudio library not found
            print(f"mic {b} unavailable: {e}", file=sys.stderr, flush=True)
    raise SystemExit("ERROR no microphone backend (need pw-record, parec or libportaudio2)")


def vocabulary():
    try:
        words = [w.strip() for w in open(VOCAB) if w.strip() and "," not in w]
        return "Chat names: " + ", ".join(words[:120]) + "."
    except OSError:
        return None


HOT = {"on": False}      # the orb is on screen: listen for "thank you" / "cancel" without the wake word


PARENT = os.getppid()


def commands():
    if os.getppid() != PARENT:                   # Jarvis went away: never keep the mic open as an orphan
        sys.exit(0)
    try:
        if os.path.getsize(CMD) == 0:
            return []
        with open(CMD, "r+") as f:
            lines = [l.strip().upper() for l in f if l.strip()]
            f.seek(0); f.truncate()
        for l in lines:                          # HOT/COLD are state, remembered wherever they are read
            if l == "HOT":
                HOT["on"] = True
            elif l == "COLD":
                HOT["on"] = False
        return lines
    except OSError:
        return []


def level(frame):
    return float(np.sqrt(np.mean(frame.astype(np.float32) ** 2)))


def record(stream, floor, preroll=None):
    """One request: until a pause after speech, a STOP, or a timeout. Returns int16 audio or None.
    preroll = the ~3 s heard before the wake word ("Hey Jarvis, take me to X" in one breath)."""
    say("LISTENING")
    floor = max(floor, 60.0)
    chunks = list(preroll or [])
    recent = chunks[-19:]
    spoke = any(level(c) > floor * 2.2 for c in recent)
    quiet, t0, voiced = 0.0, time.time(), 0.0
    heard_s = 0.0                                # audio time, so file replays behave like the real clock
    wait_more = preroll is not None
    while True:
        frame, _ = stream.read(FRAME)
        mono = frame[:, 0].copy()
        chunks.append(mono)
        heard_s += FRAME / RATE
        for cmd in commands():
            if cmd == "STOP":
                return np.concatenate(chunks) if spoke else None
            if cmd == "CANCEL":
                record.last = None
                return None
        lv = level(mono)
        say(f"LEVEL {min(1.0, lv / (floor * 10)):.2f}")
        if lv > floor * 2.2:
            spoke, quiet = True, 0.0
            voiced += FRAME / RATE
        elif spoke and lv < floor * 1.6:
            quiet += FRAME / RATE
        waited = max(time.time() - t0, heard_s)
        if spoke and quiet >= (2.0 if wait_more and voiced < 0.6 else PAUSE_S):
            return np.concatenate(chunks)
        if (not spoke and waited > NO_SPEECH_S) or waited > MAX_S:
            record.last = np.concatenate(chunks)
            return record.last if spoke else None


_stt = None


def stt():
    global _stt
    if _stt is None:
        from faster_whisper import WhisperModel
        _stt = WhisperModel(os.environ.get("JARVIS_WHISPER", "base.en"), device="cpu", compute_type="int8")
    return _stt


def transcribe(audio):
    segs, _ = stt().transcribe(audio.astype(np.float32) / 32768.0, language="en", beam_size=1,
                               initial_prompt=vocabulary(), vad_filter=True)
    return " ".join(s.text.strip() for s in segs).strip()


def handle(stream, floor, preroll=None):
    audio = record(stream, floor, preroll)
    if audio is None:
        audio = getattr(record, "last", None)    # noisy rooms: let Whisper's own voice filter decide
        if audio is None or len(audio) < RATE // 2:
            say("NOSPEECH"); return
    text = transcribe(audio)
    say(f"HEARD {text}" if text else "NOSPEECH")


def dictate(stream, floor, preroll=None):
    """Dictation: no time cap and no silence stop. It records until STOP (his second press) or
    CANCEL. Long takes are transcribed in ~20-30 s pieces in the background while he talks, then joined in order."""
    import queue, threading
    say("LISTENING")
    floor = max(floor, 60.0)
    work, texts = queue.Queue(), {}

    def worker():
        while True:
            item = work.get()
            if item is None:
                return
            i, audio = item
            try:
                texts[i] = transcribe(audio)
            except Exception as e:
                print(f"dictate piece {i} failed: {e}", file=sys.stderr, flush=True); texts[i] = ""
    th = threading.Thread(target=worker, daemon=True); th.start()
    chunk, chunk_s, quiet, n = list(preroll or []), 0.0, 0.0, 0
    while True:
        frame, _ = stream.read(FRAME)
        mono = frame[:, 0].copy()
        cmds = commands()
        if "CANCEL" in cmds:
            work.put(None); say("NOSPEECH"); return
        stop = "STOP" in cmds
        chunk.append(mono); chunk_s += FRAME / RATE
        lv = level(mono)
        say(f"LEVEL {min(1.0, lv / (floor * 10)):.2f}")
        quiet = quiet + FRAME / RATE if lv < floor * 1.6 else 0.0
        # cut a piece at a pause once it's 20 s long (never mid-word if he pauses), or at 28 s regardless
        if stop or (chunk_s >= 20 and quiet >= 0.5) or chunk_s >= 28:
            work.put((n, np.concatenate(chunk))); n += 1; chunk, chunk_s = [], 0.0
        if stop:
            break
    work.put(None); th.join()
    text = " ".join(texts[i] for i in range(n) if texts.get(i)).strip()
    say(f"HEARD {text}" if text else "NOSPEECH")


def main():
    os.makedirs(CONF, exist_ok=True)
    open(CMD, "w").close()                      # start clean
    stt()                                        # load Whisper before READY, so the first request is quick
    floor, last_wake = 200.0, -COOLDOWN
    if WAKE_MODE:
        import openwakeword
        from openwakeword.model import Model
        from collections import deque
        wake = Model(wakeword_model_paths=[p for p in openwakeword.get_pretrained_model_paths() if "hey_jarvis" in p])
        ring = deque(maxlen=38)
        hot_buf, hot_quiet = [], 0.0
        with open_mic() as stream:
            say(f"MIC {stream.name}"); say("READY")
            clock = 0.0                          # audio time (cooldown works for file replays too)
            while True:
                frame, _ = stream.read(FRAME)
                clock += FRAME / RATE
                mono = frame[:, 0]
                ring.append(mono.copy())
                lvl = level(mono)
                floor = min(0.98 * floor + 0.02 * lvl, max(lvl, 60.0) * 1.5) if lvl < floor else 0.995 * floor + 0.005 * lvl
                cmds = list(commands())
                hot = HOT["on"]
                if not hot:
                    hot_buf = []
                if hot and "LISTEN" not in cmds and "DICTATE" not in cmds:
                    if lvl > floor * 2.2:
                        if not hot_buf:
                            hot_buf = list(ring)[-3:-1]
                        hot_buf.append(mono.copy()); hot_quiet = 0.0
                    elif hot_buf:
                        hot_buf.append(mono.copy()); hot_quiet += FRAME / RATE
                    dur = len(hot_buf) * FRAME / RATE
                    if hot_buf and (hot_quiet >= 0.9 or dur > 5.0):
                        if dur <= 5.0:
                            try:
                                text = transcribe(np.concatenate(hot_buf))
                            except Exception as e:
                                print(f"hot transcribe failed: {e}", file=sys.stderr, flush=True); text = ""
                            if text:
                                say("HOTHEARD " + text)
                        hot_buf, hot_quiet = [], 0.0
                if "DICTATE" in cmds:
                    dictate(stream, floor, list(ring)[-6:]); ring.clear(); wake.reset(); last_wake = clock; continue
                if "LISTEN" in cmds:
                    handle(stream, floor, list(ring)[-6:]); ring.clear(); wake.reset(); last_wake = clock; continue
                if max(wake.predict(mono).values()) >= WAKE_THRESHOLD and clock - last_wake > COOLDOWN:
                    last_wake = clock; hot_buf = []; say("WAKE")
                    handle(stream, floor, list(ring)); ring.clear(); wake.reset()
                    last_wake = clock
    else:
        say("READY")
        while True:                              # push-to-talk only: mic closed until asked
            cmds = commands()
            if "LISTEN" in cmds or "DICTATE" in cmds:
                with open_mic() as stream:
                    say(f"MIC {stream.name}")
                    noise = [level(stream.read(FRAME)[0][:, 0]) for _ in range(3)]
                    (dictate if "DICTATE" in cmds else handle)(stream, float(np.median(noise)))
                if os.environ.get("JARVIS_MIC_FILE"):
                    say("MICEND"); return
            time.sleep(0.1)


if __name__ == "__main__":
    main()
