"""Script tooling: one structured source (explainer/script.yaml) -> script.md, timing, TTS.

    python explainer/script_tool.py md                 # script.md with ~150 wpm timestamps
    python explainer/script_tool.py tts [--voice V]    # scratch narration (piper, offline)
                                                       # -> output/audio/scratch_narration.wav
                                                       #    + explainer/timing.json (scene timing)

script.yaml layout::

    title: ...
    wpm: 150
    sections:
      - id: hook
        title: Hook
        lines:
          - id: hook_q
            say: "What happens if our universe collided with another one?"
            screen: "What happens if our universe collided with another one?"
            visual: "engine footage: the two galaxies approaching"
            label: "N-body simulation"          # or "illustration", "illustration (toy model)"
            sources: [S1, S2]                    # keys into sources.md
            pause_after: 0.6                     # seconds of silence after the line
"""
import argparse
import json
import re
import subprocess
import sys
import wave
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "explainer" / "script.yaml"
TIMING = REPO / "explainer" / "timing.json"
AUDIO_DIR = REPO / "output" / "audio"
VOICE_DIR = REPO / "output" / "voices"


def load():
    return yaml.safe_load(SCRIPT.read_text())


def words(text):
    return len(re.findall(r"[A-Za-z0-9'’-]+", text or ""))


def wpm_durations(doc):
    wpm = float(doc.get("wpm", 150))
    out = {}
    for sec in doc["sections"]:
        for ln in sec["lines"]:
            out[ln["id"]] = words(ln.get("say", "")) / wpm * 60.0 + float(ln.get("hold", 0.0))
    return out


def schedule(doc, durations):
    """Start/end time of every line, given each line's spoken duration."""
    t = float(doc.get("lead_in", 0.0))
    rows = []
    for sec in doc["sections"]:
        t += float(sec.get("gap_before", 0.0))
        for ln in sec["lines"]:
            d = durations[ln["id"]]
            rows.append({"section": sec["id"], "id": ln["id"], "start": round(t, 3),
                         "end": round(t + d, 3)})
            t += d + float(ln.get("pause_after", 0.4))
    total = t + float(doc.get("tail", 0.0))
    return rows, total


def fmt(t):
    m, s = divmod(t, 60)
    return f"{int(m)}:{s:04.1f}"


def write_md(doc, rows, total, how):
    by_id = {r["id"]: r for r in rows}
    n_words = sum(words(ln.get("say", "")) for s in doc["sections"] for ln in s["lines"])
    L = [f"# {doc['title']}", "",
         f"Narration script: {n_words} words, {fmt(total)} total; timestamps {how}.",
         "Every claim cites a source key from `sources.md` (section 5). On-screen labels mark what",
         "is simulated, what is an illustration, and what is speculative.", ""]
    for sec in doc["sections"]:
        first = by_id[sec["lines"][0]["id"]]["start"]
        last = by_id[sec["lines"][-1]["id"]]["end"]
        L += [f"## {sec['title']}  ({fmt(first)}–{fmt(last)})", ""]
        if sec.get("note"):
            L += [f"*{sec['note']}*", ""]
        for ln in sec["lines"]:
            r = by_id[ln["id"]]
            L.append(f"**[{fmt(r['start'])}–{fmt(r['end'])}]** {ln.get('say', '').strip()}")
            L.append("")
            meta = []
            if ln.get("screen"):
                meta.append(f"On screen: {ln['screen']}")
            if ln.get("visual"):
                meta.append(f"Visual: {ln['visual']}")
            if ln.get("label"):
                meta.append(f"Label: \"{ln['label']}\"")
            if ln.get("sources"):
                meta.append("Sources: " + ", ".join(ln["sources"]))
            for m in meta:
                L.append(f"- {m}")
            L.append("")
    (REPO / "script.md").write_text("\n".join(L))


def wav_duration(p):
    with wave.open(str(p)) as w:
        return w.getnframes() / w.getframerate()


def tts(doc, voice):
    VOICE_DIR.mkdir(parents=True, exist_ok=True)
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    model = VOICE_DIR / f"{voice}.onnx"
    if not model.exists():
        subprocess.run([sys.executable, "-m", "piper.download_voices", "--data-dir", str(VOICE_DIR), voice],
                       check=True)
    durs = {}
    parts = []
    for sec in doc["sections"]:
        for ln in sec["lines"]:
            out = AUDIO_DIR / f"line_{ln['id']}.wav"
            text = ln.get("tts", ln.get("say", ""))   # optional phonetic spelling for TTS
            if not text.strip():                       # silent line (e.g. end card)
                durs[ln["id"]] = float(ln.get("hold", 0.0))
                continue
            subprocess.run([sys.executable, "-m", "piper", "-m", str(model), "-f", str(out),
                            "--", text], check=True, capture_output=True)
            durs[ln["id"]] = wav_duration(out) + float(ln.get("hold", 0.0))
            parts.append((ln["id"], out))
    rows, total = schedule(doc, durs)
    # assemble the scratch track on the schedule with ffmpeg (silence between lines)
    inputs, filt = [], []
    for k, (lid, p) in enumerate(parts):
        start_ms = int(round(next(r for r in rows if r["id"] == lid)["start"] * 1000))
        inputs += ["-i", str(p)]
        filt.append(f"[{k}:a]adelay={start_ms}|{start_ms}[a{k}]")
    mix = "".join(f"[a{k}]" for k in range(len(parts)))
    filt.append(f"{mix}amix=inputs={len(parts)}:normalize=0,apad=whole_dur={total:.3f}[out]")
    track = AUDIO_DIR / "scratch_narration.wav"
    subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(filt),
                    "-map", "[out]", "-ar", "48000", "-ac", "1", str(track)], check=True)
    return rows, total, track


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["md", "tts"])
    ap.add_argument("--voice", default="en_US-lessac-medium")
    a = ap.parse_args(argv)
    doc = load()
    if a.cmd == "md":
        rows, total = schedule(doc, wpm_durations(doc))
        write_md(doc, rows, total, f"estimated at {doc.get('wpm', 150)} words per minute")
    else:
        rows, total, track = tts(doc, a.voice)
        TIMING.write_text(json.dumps({"total": total, "lines": rows}, indent=2))
        print("wrote", track, "and", TIMING)
    print(f"total {fmt(total)}")


if __name__ == "__main__":
    main()
