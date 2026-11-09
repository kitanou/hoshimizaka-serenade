"""フォルマント合成による女性ボーカル（#83）。

90 年代 FM 音源の声風: 声門パルス（加算調波）→ 母音フォルマント 3 共振
（FFT 領域で 1 セグメントずつ適用）→ 子音付与。1 音符=モーラ列（複数可）。
タイミングは songs.py のメロディと同一 → 歌詞字幕（op.rpy OP_LYRICS）と完全同期。
既存の歌詞・歌い出し仕様（docs/op-storyboard.md §2/§8）は崩さない。
"""
import numpy as np

from .synth import SR, mtof

# 母音フォルマント（女性声道を想定。freq/bandwidth[Hz], gain）
VOWELS = {
    "a": ((800, 90, 1.00), (1150, 110, 0.62), (2800, 180, 0.42)),
    "i": ((300, 80, 1.00), (2250, 110, 0.55), (3000, 180, 0.40)),
    "u": ((350, 80, 1.00), (720, 100, 0.52), (2500, 180, 0.34)),
    "e": ((520, 85, 1.00), (2150, 110, 0.55), (2550, 180, 0.40)),
    "o": ((480, 85, 1.00), (850, 100, 0.55), (2450, 180, 0.36)),
    "n": ((250, 70, 1.00), (1050, 160, 0.20), (2300, 200, 0.05)),  # ん（撥音）
}

STOP = {"k", "t", "p"}
FRIC = {"s", "sh", "h", "f"}
NAS = {"n", "m"}
GLIDE = {"r", "y", "w"}
DIGRAPHS = ("sh", "ch", "ts")
VOW_CHARS = "aiueon"


def parse_mora(m):
    """'ka','shi','to.tsu','ha.' 等 → (consonant, vowel)。長音・促音は直前の母音継続。"""
    cons = ""
    for d in DIGRAPHS:
        if m.startswith(d):
            cons = d
            break
    if not cons and m and m[0] not in VOW_CHARS:
        cons = m[0]
    vowel = ""
    for ch in reversed(m):
        if ch in VOW_CHARS:
            vowel = ch
            break
    if not vowel:
        vowel = "n"
    return cons, vowel


def _formant_h(n, forms):
    """セグメント長 n の rfft 用 magnitude response（3 共振和、ピーク 1 に正規化）。"""
    f = np.fft.rfftfreq(n, 1.0 / SR)
    H = np.zeros_like(f)
    for fc, bw, g in forms:
        H += g * bw * bw / (((f - fc) ** 2 + bw * bw) + ((f + fc) ** 2 + bw * bw))
    return H / (H.max() or 1.0)


def _apply_formant(x, forms):
    """FFT 領域でフォルマント適用。丸め込み防止にゼロパディング→切り出し。"""
    m = len(x)
    n = 1 << (2 * m).bit_length()
    X = np.fft.rfft(x, n)
    y = np.fft.irfft(X * _formant_h(n, forms), n)
    return y[:m]


class Voice:
    """女性ボーカルトラック。note 単位で add_note を呼ぶ（外部の Mix バッファへ積む）。"""

    def __init__(self, rng, vol=1.0):
        self.rng = rng
        self.vol = vol
        K = 26
        self.hk = np.arange(1, K + 1, dtype=float)
        self.ampk = 1.0 / self.hk ** 1.35          # 声門開き関数風の rolloff
        self.ampk[1::2] *= 1.06                    # 女性寄りの倍音バランス

    def _pulse(self, f0, n, vib_cents=11.0, vib_hz=5.3):
        """f0 列に対する声門パルス（加算調波）。ビブラート・ゆらぎ・付点スコープ込み。"""
        t = np.arange(n) / SR
        f0 = np.asarray(f0, dtype=float)
        vib = vib_cents * np.clip((t - 0.18) / 0.35, 0, 1) * np.sin(2 * np.pi * vib_hz * t)
        jit = np.convolve(self.rng.normal(0, 1.4, n), np.ones(64) / 8, mode="same")
        f = f0 * (2.0 ** ((vib + jit) / 1200.0))
        phase = np.cumsum(2 * np.pi * f) / SR
        sig = np.zeros(n)
        for k, a in zip(self.hk, self.ampk):
            sig += a * np.sin(k * phase)
        sig /= np.max(np.abs(sig)) or 1.0
        breath = np.convolve(self.rng.normal(0, 0.05, n), np.ones(8) / 8, mode="same")
        return sig + breath

    def _consonant(self, cons, dur, amp):
        """子音セグメント（母音直前の調音噪声/鼻声/グライド）。"""
        n = max(8, int(dur * SR))
        if cons in STOP:
            x = np.zeros(n)
            burst = max(4, int(0.012 * SR))
            x[:burst] = self.rng.uniform(-1, 1, burst) * 0.5
            return _apply_formant(x, VOWELS["a"]) * amp
        if cons in FRIC:
            x = self.rng.uniform(-1, 1, n)
            xc = np.cumsum(x)
            x = np.where(cons in ("s", "sh"), (x - 0.6 * xc / np.arange(1, n + 1)), x)
            if cons == "s":
                x = np.convolve(x, np.array([1, -2, 3, -2, 1.0]) / 5, mode="same")
            return x * amp * 0.5
        if cons in NAS:
            tt = np.arange(n) / SR
            hum = np.sin(2 * np.pi * 240 * tt) + 0.4 * np.sin(2 * np.pi * 720 * tt)
            env = amp * np.sin(np.pi * tt / (dur + 1e-6)) ** 0.6
            return hum * env * 0.5
        if cons in GLIDE:
            return None  # 母音側のフォルマント ramp で処理
        return np.zeros(n)

    def add_note(self, midi, dur, syls, gain=1.0):
        """dur 秒、midi 音程でモーラ列 syls を歌い、サンプル列を返す。"""
        syls = [s for s in syls if s]
        if not syls:
            return
        f_base = mtof(midi)
        total = dur
        # モーラ重み（長い母音は長め）
        ws = []
        for s in syls:
            cons, vow = parse_mora(s)
            w = 1.0 + (0.35 if cons in STOP else 0.12 if cons in FRIC else 0.2 if cons in NAS else 0)
            if vow == "n":
                w = 0.8
            ws.append(w)
        tw = sum(ws)
        segs = np.cumsum([w / tw * total for w in ws])
        out = np.zeros(int(total * SR) + 8)

        prev_vow = None
        for i, (s, tend) in enumerate(zip(syls, segs)):
            cons, vow = parse_mora(s)
            t0 = 0.0 if i == 0 else segs[i - 1]
            d = tend - t0
            n = max(16, int(d * SR))
            c, pv = parse_mora(syls[i - 1]) if i else ("", None)
            # 語頭モーラだけ軽い上昇（スコープ）
            if i == 0:
                f0 = f_base * 2.0 ** (np.interp(np.arange(n), [0, 0.10 * SR, n], [1.2, 0.0, 0.0]) / 12.0)
            else:
                f0 = np.full(n, f_base)
            src = self._pulse(f0, n)
            forms = VOWELS[vow]
            if cons in GLIDE:  # y/w/r: 直前母音→目標母音のフォルマント移動
                src = _apply_formant(src, VOWELS[pv or "u"])
                src = 0.6 * src + 0.4 * _apply_formant(self._pulse(f0, n), forms)
                forms = None
            if forms is not None:
                src = _apply_formant(src, forms)
            # 調音
            cs = None
            if cons and cons not in GLIDE:
                cdur = {"k": 0.05, "t": 0.05, "p": 0.05, "s": 0.075, "sh": 0.085,
                        "h": 0.05, "f": 0.06, "n": 0.06, "m": 0.06}.get(cons, 0.04)
                cdur = min(cdur, 0.45 * d)
                cn = int(cdur * SR)
                cs = self._consonant(cons, cdur, self.vol)
                src = src[: n - cn]
            # 母音エンベロープ
            nn = len(src)
            tt = np.arange(nn) / SR
            att = 0.028 if not cons else 0.012
            rel = min(0.05, 0.3 * d)
            env = np.interp(tt, [0, att, max(att + 1e-4, d - rel), d], [0, 1, 0.92, 0], right=0.0)
            vseg = src * env
            i0 = int(t0 * SR)
            if i0 >= len(out):
                break
            if cs is not None:
                j0 = max(0, i0 - len(cs))
                out[j0: j0 + len(cs)] += cs * gain
            out[i0: i0 + len(vseg)] += vseg[: len(out) - i0] * self.vol * gain
        return out


def add_voice(mix, v, t, midi, dur, syls, vol=1.0, send=0.0, cut=5200):
    """mix（Mix）の指定カットトラックへボーカル 1 音を追加する（v は Voice インスタンス）。"""
    seg = v.add_note(midi, dur, syls)
    i = int(t * SR)
    j = min(mix.n, i + len(seg))
    buf = mix._buf(cut)
    buf[i:j] += seg[: j - i] * vol
    if send:
        mix.send[i:j] += seg[: j - i] * vol * send
