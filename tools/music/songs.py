"""楽曲定義とシーケンサ。index.html の LYR/SONGS/stepNote の移植＋新曲。

メロディは [(midi, 拍数), ...]。midi=0 は休符。1小節=4拍=16ステップ。
"""
import numpy as np

from .synth import Mix, SR

CHORD = {
    "C": (36, (60, 64, 67)), "F": (41, (57, 60, 65)), "G": (43, (59, 62, 67)),
    "Em": (40, (59, 64, 67)), "Am": (45, (57, 60, 64)),
    "Dm": (38, (57, 62, 65)), "E": (40, (56, 59, 64)),
}

# OP 曲「流れ星エチュード」の歌詞とメロディ（歌詞は index.html と同じ）
LYR = [
    ("坂道のむこう　流れ星ひとつ",
     [(69, .5), (72, .5), (72, .5), (74, .5), (76, 1), (74, .5), (72, .5), (74, .5), (76, .5), (79, .5), (76, .5), (74, 1.5), (0, .5)]),
    ("キミの名前を　夜空に呼んだ",
     [(71, .5), (72, .5), (74, .5), (76, .5), (79, 1), (76, .5), (74, .5), (72, .5), (71, .5), (72, .5), (69, .5), (69, 1.5), (0, .5)]),
    ("ときめくハートは　秘密のメロディ",
     [(69, .5), (72, .5), (72, .5), (74, .5), (76, 1), (77, .5), (76, .5), (74, .5), (76, .5), (79, 1), (81, 1), (79, 1)]),
    ("制服のまま　明日へ駆けだそう",
     [(76, .5), (77, .5), (79, .5), (81, .5), (83, 1), (81, .5), (79, .5), (81, 1), (79, .5), (77, .5), (76, 1), (74, 1)]),
    ("Shooting Star!　願いをのせて",
     [(84, 1), (83, .5), (81, .5), (79, 1), (76, .5), (79, .5), (81, .5), (79, .5), (77, .5), (76, .5), (74, 1), (76, 1)]),
    ("この想い　ずっと　輝いて",
     [(76, .5), (79, .5), (81, .5), (84, .5), (83, 1), (81, .5), (79, .5), (81, 1), (83, 1), (84, 2)]),
]
_END = [(81, 1), (79, 1), (77, 1), (76, 1), (72, 4)]

SONGS = {
    "op": dict(bpm=128, loop=False, lead=dict(type="square", vol=.085, vib=9, send=.5), drums=True, arp=True,
               crash=[2, 10, 14], fill=[1, 9],
               bars="F G F G Em Am F G Em Am F G Em Am F C".split(),
               mel=[(0, 8)] + [n for _, m in LYR for n in m] + _END),
    "title": dict(bpm=92, loop=True, lead=dict(type="triangle", vol=.12, vib=6, send=.6), drums=False, arp=True, soft=True,
                  bars="F G Em Am F G C C".split(), mel=LYR[4][1] + LYR[5][1] + LYR[4][1] + _END),
    "day": dict(bpm=112, loop=True, lead=dict(type="square", vol=.05, vib=5, send=.4, cut=2400), drums=True, light=True,
                arp=False, bars="C Am F G C Am F G".split(),
                mel=[(72, 1), (76, 1), (79, 1), (76, 1), (76, .5), (74, .5), (72, 1), (69, 2), (69, 1), (72, 1), (77, 1),
                     (76, .5), (74, .5), (74, 3), (0, 1),
                     (72, 1), (76, 1), (79, 1.5), (81, .5), (79, 1), (76, 1), (72, 2), (77, 1), (76, 1), (74, 1), (72, 1),
                     (71, 2), (74, 2)]),
    # ---- 新曲 ----
    "evening": dict(bpm=84, loop=True, lead=dict(type="triangle", vol=.12, vib=6, send=.6), drums=False, arp=True, soft=True,
                    bars="Am F C G Am F G C".split(),
                    mel=[(76, 1.5), (74, .5), (72, 1), (69, 1), (72, 1.5), (69, .5), (65, 1), (69, 1),
                         (67, 1), (72, 1), (76, 2), (74, 1.5), (72, .5), (71, 1), (67, 1),
                         (76, 1.5), (77, .5), (79, 1), (76, 1), (77, 1.5), (76, .5), (72, 1), (69, 1),
                         (71, 1), (74, 1), (79, 1), (77, 1), (76, 3), (0, 1)]),
    "touka": dict(bpm=72, loop=True, lead=dict(type="triangle", vol=.11, vib=7, send=.7), drums=False, arp=True, soft=True,
                  bars="Am Em F C Dm Am E Am".split(),
                  mel=[(72, 2), (76, 1), (74, 1), (71, 2), (67, 1), (71, 1), (69, 2), (72, 1), (77, 1), (76, 3), (0, 1),
                       (74, 2), (77, 1), (76, 1), (72, 2), (69, 1), (72, 1), (71, 1.5), (68, .5), (71, 1), (76, 1), (69, 4)]),
    "misaki": dict(bpm=124, loop=True, lead=dict(type="square", vol=.055, vib=5, send=.4, cut=2600), drums=True, light=True,
                   arp=False, bars="C G Am F C G F G".split(),
                   mel=[(79, .5), (79, .5), (76, .5), (79, .5), (84, 1), (79, 1), (83, .5), (83, .5), (79, .5), (83, .5), (86, 1), (83, 1),
                        (81, .5), (81, .5), (76, .5), (81, .5), (84, 1), (81, 1), (77, .5), (81, .5), (84, 1), (81, .5), (77, .5), (79, 1),
                        (84, 1), (83, .5), (84, .5), (86, 1), (84, 1), (83, 1), (79, .5), (83, .5), (86, 2),
                        (84, .5), (81, .5), (77, 1), (81, 1), (84, 1), (83, 1.5), (79, .5), (74, 2)]),
    "tension": dict(bpm=100, loop=True, lead=dict(type="sawtooth", vol=.05, vib=6, send=.3, cut=1800), drums=True, light=True,
                    arp=True, bars="Am Am F E Am Dm F E".split(),
                    mel=[(69, 1), (0, 1), (72, .5), (71, .5), (69, 1), (64, 1), (0, 1), (69, .5), (68, .5), (64, 1),
                         (65, 1), (69, 1), (72, 1), (69, 1), (68, 1), (71, 1), (76, 2),
                         (72, 1), (0, .5), (72, .5), (71, 1), (69, 1), (74, 1), (77, 1), (81, 2),
                         (77, 1), (72, 1), (69, 1), (65, 1), (68, .5), (71, .5), (76, 1), (80, 2)]),
}


def render_song(name):
    s = SONGS[name]
    bpm = s["bpm"]
    step = 60.0 / bpm / 4
    beat = step * 4
    nbars = len(s["bars"])
    total_steps = nbars * 16
    length = total_steps * step
    mix = Mix(length)
    # メロディのイベント表（16分ステップ→[(midi, 拍)]）
    ev = {}
    b = 0.0
    for m, d in s["mel"]:
        if m:
            ev.setdefault(round(b * 4), []).append((m, d))
        b += d
    assert abs(b - nbars * 4) < 1e-6, f"{name}: メロディが {b} 拍（小節 {nbars * 4} 拍）"
    soft = s.get("soft", False)
    loop = s["loop"]
    for k in range(total_steps):
        t = k * step
        bar, pos = divmod(k, 16)
        root, tones = CHORD[s["bars"][bar]]
        last = (not loop) and bar == nbars - 1
        if pos == 0:
            for n in tones:
                mix.tone(t, n, beat * 4 if last else beat * 4 - .02, type="triangle" if soft else "sawtooth",
                         vol=.035 if soft else .022, a=.04, r=.2, cut=3000 if soft else 1600)
            if bar in s.get("crash", []):
                mix.noise(t, vol=.16, dur=1.4, freq=4500)
        if last:
            if pos == 0:
                mix.kick(t)
                mix.tone(t, root, beat * 3, type="sawtooth", vol=.12, cut=700)
            continue
        if pos % 2 == 0:
            n = root + (12 if pos % 4 == 2 else 0)
            mix.tone(t, n, step * 1.8, type="triangle" if soft else "sawtooth", vol=.09 if soft else .11,
                     cut=900 if soft else 650, a=.005, r=.04)
        if s.get("arp"):
            n = tones[pos % 3] + 12 + (12 if pos % 8 >= 4 else 0)
            mix.tone(t, n, step * .7, type="square", vol=.018 if soft else .022, a=.003, r=.03, cut=4000)
        if s.get("drums"):
            if s.get("light"):
                if pos in (0, 8):
                    mix.kick(t)
                if pos in (4, 12):
                    mix.snare(t, .5)
                if pos % 2 == 0:
                    mix.noise(t, vol=.04, dur=.04, freq=8000)
            else:
                chorus = bar >= 10
                if pos in (0, 8) or (chorus and pos in (6, 10)):
                    mix.kick(t)
                if bar in s.get("fill", []) and pos >= 8:
                    mix.snare(t, .5 + (pos - 8) / 16)
                elif pos in (4, 12):
                    mix.snare(t)
                if pos % 2 == 0:
                    mix.noise(t, vol=.08 if pos % 4 == 2 else .05, dur=.09 if pos % 4 == 2 else .04, freq=7500)
        for m, d in ev.get(k, []):
            L = s["lead"]
            dur = d * beat * .95
            mix.tone(t, m, dur, type=L["type"], vol=L["vol"], vib=L.get("vib", 0) if dur > .35 else 0,
                     send=L.get("send", 0), cut=L.get("cut"), a=.012, r=.06)
            if not soft:
                mix.tone(t, m, dur, type="triangle", vol=L["vol"] * .6, detune=7, a=.012, r=.06)
    out = mix.render()
    n_total = int(length * SR)
    if loop:
        tail = out[n_total:n_total + int(2.5 * SR)]
        out = out[:n_total].copy()
        out[:len(tail)] += tail  # 余韻を先頭に折り返し、継ぎ目をなくす
        pk = max(1e-9, float(np.abs(out).max()))
        out = out / pk * .89
    else:
        out = out[:n_total + int(1.5 * SR)]
        fade = int(1.0 * SR)
        out[-fade:] *= np.linspace(1, 0, fade)
    return out
