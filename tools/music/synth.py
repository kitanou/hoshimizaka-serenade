"""FM音源風シンセ（numpy）。index.html の tone()/noiseHit()/kick()/snare() の移植。

Web Audio との違い:
- ノート毎の BiquadFilter は、同じカットオフのノートを1本のトラックにまとめて
  FFT で一括ローパスする（Python ループを避けるため）。
- ディレイ送り（send）も同様にトラック単位でまとめて処理する。
"""
import numpy as np

SR = 44100


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


class Mix:
    """全トラックを蓄積して最後に1本へミックスする。"""

    def __init__(self, seconds):
        self.n = int((seconds + 3.0) * SR)  # 余韻ぶんを足す
        self.tracks = {}   # (cut,) -> buffer
        self.send = np.zeros(self.n)
        self.dry = np.zeros(self.n)
        self.rng = np.random.default_rng(1)

    def _buf(self, cut):
        if cut not in self.tracks:
            self.tracks[cut] = np.zeros(self.n)
        return self.tracks[cut]

    def add(self, buf, t, sig):
        i = int(t * SR)
        if i >= self.n:
            return
        j = min(self.n, i + len(sig))
        buf[i:j] += sig[: j - i]

    # ---- 基本波形 -----------------------------------------------------
    def _osc(self, kind, freq, n, vib=0.0, detune=0.0):
        t = np.arange(n) / SR
        f = freq * 2 ** (detune / 1200.0)
        if vib:
            ramp = np.clip(t / 0.3, 0, 1)
            f = f * 2 ** ((vib * ramp * np.sin(2 * np.pi * 5.5 * t)) / 1200.0)
            phase = np.cumsum(f) / SR
        else:
            phase = f * t
        ph = phase % 1.0
        if kind == "square":
            return np.where(ph < 0.5, 1.0, -1.0)
        if kind == "sawtooth":
            return 2.0 * ph - 1.0
        if kind == "triangle":
            return 4.0 * np.abs(ph - 0.5) - 1.0
        return np.sin(2 * np.pi * ph)

    def tone(self, t, midi, dur, type="square", vol=.08, a=.01, r=.06, sus=.8,
             cut=None, vib=0.0, send=0.0, detune=0.0, target="bus"):
        n = int((dur + 0.05) * SR)
        sig = self._osc(type, mtof(midi), n, vib, detune)
        tt = np.arange(n) / SR
        t_rel = max(a + 1e-4, dur - r)
        env = np.interp(tt, [0, a, t_rel, max(dur, t_rel + 1e-4)], [0, vol, vol * sus, 0], right=0.0)
        sig = sig * env
        self.add(self._buf(cut), t, sig)
        if send:
            self.add(self.send, t, sig * send)

    def noise(self, t, vol=.2, dur=.1, kind="highpass", freq=6000):
        n = int((dur + 0.02) * SR)
        x = self.rng.uniform(-1, 1, n)
        x = _fft_filter(x, kind, freq)
        env = vol * np.exp(-np.linspace(0, 7, n))
        self.add(self._buf(None), t, x * env)

    def kick(self, t):
        n = int(0.22 * SR)
        tt = np.arange(n) / SR
        f = 42 + (150 - 42) * np.exp(-tt / 0.04)
        ph = np.cumsum(f) / SR
        env = .55 * np.exp(-tt / 0.06)
        self.add(self._buf(None), t, np.sin(2 * np.pi * ph) * env)

    def snare(self, t, v=1.0):
        self.noise(t, vol=.22 * v, dur=.14, kind="bandpass", freq=1900)
        self.tone(t, 55, .08, type="triangle", vol=.1 * v, a=.002, r=.06)

    # ---- ミックスダウン -----------------------------------------------
    def render(self, delay=(0.28, 0.3, 0.22)):
        out = self.dry.copy()
        for cut, buf in self.tracks.items():
            out += _fft_filter(buf, "lowpass", cut) if cut else buf
        # フィードバックディレイ
        dt, fb, wet = delay
        d = int(dt * SR)
        s = _fft_filter(self.send, "lowpass", 4000)
        tap = s.copy()
        acc = np.zeros(self.n)
        k = 1
        while k < 9:
            sh = k * d
            if sh >= self.n:
                break
            acc[sh:] += tap[: self.n - sh] * (fb ** (k - 1))
            k += 1
        out = out + acc * wet
        peak = np.max(np.abs(out)) or 1.0
        return out / peak * 0.89


def _fft_filter(x, kind, freq):
    """2次相当のなだらかなフィルタ（位相は気にしない）。"""
    n = len(x)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    r = f / float(freq)
    if kind == "lowpass":
        H = 1 / np.sqrt(1 + r ** 4)
    elif kind == "highpass":
        H = (r ** 2) / np.sqrt(1 + r ** 4)
    else:  # bandpass
        q = 1.5
        H = (r / q) / np.sqrt((1 - r ** 2) ** 2 + (r / q) ** 2)
    return np.fft.irfft(X * H, n)
