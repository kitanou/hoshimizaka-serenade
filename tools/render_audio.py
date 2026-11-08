"""音源の一括生成。 usage: python -m tools.render_audio [曲名...]

出力: hoshimizaka/game/audio/bgm/*.ogg, hoshimizaka/game/audio/se/*.ogg
"""
import os
import sys

import numpy as np
import soundfile as sf

from tools.music import se
from tools.music.songs import SONGS, render_song
from tools.music.synth import SR

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO = os.path.join(ROOT, "hoshimizaka", "game", "audio")


def save(path, y):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    y = np.clip(y, -1, 1).astype(np.float32)
    sf.write(path, y, SR, format="OGG", subtype="VORBIS")
    print(f"{os.path.relpath(path, ROOT)}  {len(y) / SR:.1f}s")


def main():
    only = set(sys.argv[1:])
    for name in SONGS:
        if not only or name in only:
            save(os.path.join(AUDIO, "bgm", f"{name}.ogg"), render_song(name))
    for name, fn in se.ALL.items():
        if not only or name in only or "se" in only:
            save(os.path.join(AUDIO, "se", f"{name}.ogg"), fn())


if __name__ == "__main__":
    main()
