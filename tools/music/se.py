"""効果音（numpy）。"""
import numpy as np

from .synth import Mix, SR, _fft_filter


def _sig(seconds):
    return Mix(seconds)


def hit():
    m = _sig(.5)
    m.noise(0, vol=.35, dur=.25, kind="lowpass", freq=1200)
    m.kick(0)
    return m.render()[: int(.6 * SR)]


def select():
    m = _sig(.5)
    for i, n in enumerate([72, 76, 79, 84]):
        m.tone(i * .05, n, .12, type="square", vol=.05, send=.3)
    return m.render()[: int(.6 * SR)]


def cursor():
    m = _sig(.2)
    m.tone(0, 84, .05, type="square", vol=.05)
    return m.render()[: int(.15 * SR)]


def door():
    m = _sig(.6)
    m.noise(0, vol=.5, dur=.3, kind="lowpass", freq=400)
    m.kick(.02)
    m.noise(.18, vol=.2, dur=.12, kind="bandpass", freq=1500)
    return m.render()[: int(.7 * SR)]


def chime():
    m = _sig(4)
    for i, n in enumerate([72, 67, 69, 62]):
        t = i * .75
        for h, v in ((1, .1), (2, .04), (3, .02)):
            m.tone(t, n + 12 * (h - 1) if h == 1 else n + [0, 12, 19][h - 1], 1.6, type="sine", vol=v, a=.005, r=1.4, sus=.2, send=.3)
    return m.render()[: int(4.2 * SR)]


def footsteps():
    m = _sig(1.6)
    for i in range(5):
        m.noise(i * .3, vol=.25, dur=.08, kind="lowpass", freq=900)
    return m.render()[: int(1.7 * SR)]


def wind():
    n = int(2.5 * SR)
    x = np.random.default_rng(3).uniform(-1, 1, n)
    x = _fft_filter(x, "bandpass", 700)
    env = np.sin(np.linspace(0, np.pi, n)) ** 2 * .6
    y = x * env
    return y / np.abs(y).max() * .6


def shoot():
    n = int(1.0 * SR)
    t = np.arange(n) / SR
    f = 3200 * np.exp(-t * 3.2) + 300
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.0) * .5
    y += np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR) * np.exp(-t * 4.0) * .15
    return y


def page():
    n = int(.4 * SR)
    x = np.random.default_rng(5).uniform(-1, 1, n)
    x = _fft_filter(x, "bandpass", 2500) * np.sin(np.linspace(0, np.pi, n)) ** 2
    return x / np.abs(x).max() * .5


def heart():
    m = _sig(1)
    m.tone(0, 48, .15, type="sine", vol=.3, a=.005, r=.1)
    m.tone(.18, 48, .15, type="sine", vol=.3, a=.005, r=.1)
    m.tone(.4, 91, .4, type="sine", vol=.06, a=.005, r=.3, send=.4)
    return m.render()[: int(1.0 * SR)]


ALL = dict(hit=hit, select=select, cursor=cursor, door=door, chime=chime, footsteps=footsteps,
           wind=wind, shoot=shoot, page=page, heart=heart)
