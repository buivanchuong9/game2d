from __future__ import annotations

import math
from pathlib import Path
import wave
import struct


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Sounds"


def _write_wav_mono(path: Path, samples: list[int], sample_rate: int = 44100):
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        frames = b"".join(struct.pack("<h", max(-32768, min(32767, s))) for s in samples)
        wf.writeframes(frames)


def _tone(freq: float, dur_s: float, amp: float, sample_rate: int = 44100):
    n = int(dur_s * sample_rate)
    out = []
    for i in range(n):
        t = i / sample_rate
        env = 1.0
        # quick attack/decay envelope
        if t < 0.01:
            env = t / 0.01
        elif t > dur_s - 0.04:
            env = max(0.0, (dur_s - t) / 0.04)
        val = math.sin(2 * math.pi * freq * t) * amp * env
        out.append(int(val * 32767))
    return out


def _noise(dur_s: float, amp: float, sample_rate: int = 44100, seed: int = 123):
    # simple deterministic LCG noise
    n = int(dur_s * sample_rate)
    x = seed & 0x7FFFFFFF
    out = []
    for i in range(n):
        x = (1103515245 * x + 12345) & 0x7FFFFFFF
        v = ((x / 0x7FFFFFFF) * 2 - 1) * amp
        # envelope
        t = i / sample_rate
        env = 1.0
        if t < 0.01:
            env = t / 0.01
        elif t > dur_s - 0.04:
            env = max(0.0, (dur_s - t) / 0.04)
        out.append(int(v * env * 32767))
    return out


def make_gate_open():
    # metallic thump + small beep
    s = []
    s += _noise(0.09, 0.35, seed=77)
    s += _tone(220, 0.08, 0.20)
    s += _tone(440, 0.07, 0.14)
    return s


def make_item_drop():
    s = []
    s += _tone(660, 0.05, 0.18)
    s += _tone(880, 0.05, 0.14)
    return s


def make_quest_complete():
    s = []
    s += _tone(523.25, 0.07, 0.18)  # C5
    s += _tone(659.25, 0.07, 0.18)  # E5
    s += _tone(783.99, 0.10, 0.18)  # G5
    return s


def make_gun_shot(seed: int = 101):
    # short noise burst + click
    s = []
    s += _noise(0.045, 0.55, seed=seed)
    s += _tone(1400, 0.015, 0.10)
    return s


def make_reload():
    # two quick clicks
    s = []
    s += _tone(900, 0.03, 0.14)
    s += _tone(600, 0.04, 0.14)
    return s


def make_enemy_hit():
    s = []
    s += _noise(0.03, 0.35, seed=33)
    s += _tone(220, 0.03, 0.10)
    return s


def make_enemy_death():
    s = []
    s += _noise(0.12, 0.45, seed=88)
    s += _tone(120, 0.10, 0.18)
    return s


def make_player_hit():
    s = []
    s += _noise(0.06, 0.35, seed=55)
    s += _tone(180, 0.05, 0.16)
    return s


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    files = {
        "sfx_gate_open.wav": make_gate_open(),
        "sfx_item_drop.wav": make_item_drop(),
        "sfx_quest_complete.wav": make_quest_complete(),
        "sfx_gun_shot.wav": make_gun_shot(101),
        "sfx_gun_shot_2.wav": make_gun_shot(202),
        "sfx_reload.wav": make_reload(),
        "sfx_enemy_hit.wav": make_enemy_hit(),
        "sfx_enemy_death.wav": make_enemy_death(),
        "sfx_player_hit.wav": make_player_hit(),
    }
    for name, samples in files.items():
        _write_wav_mono(OUT / name, samples)
        print("Wrote", (OUT / name).relative_to(ROOT))


if __name__ == "__main__":
    main()

