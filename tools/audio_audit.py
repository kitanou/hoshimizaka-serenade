#!/usr/bin/env python3
"""音響方針の静的監査（#41「音量制御をシナリオ各所へ重複実装せず、共通の音響方針を使う」）.

方針（docs/audio-design.md に記録）:
  1. `play music` は fadein 付き（例外: OP 冒頭 `play music audio.op noloop` は
     ゲーム起動同時の開始でフェード inception 不要な意図的例外）
  2. `stop music` は fadeout 付き（音切れ防止。重複再生なし）
  3. 音量操作は 設定画面(screens.rpy) と testcase だけ（脚本での preferences.volumes 直呼び禁止）
  4. audio.rpy の宣言ファイルが game/audio 配下に実在する
違反があればExit 1。run_tests.sh がテストスイートの前に実行する。
"""
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "hoshimizaka", "game")
FADEIN_ALLOW = ("play music audio.op noloop",)  # OP冒頭の意図的例外
VOLUME_ALLOWED_FILES = {"screens.rpy", "testcases.rpy"}  # 設定画面とQAテストのみ許容


def main():
    viol = []
    for dirpath, _dirnames, filenames in os.walk(ROOT):
        for fn in sorted(filenames):
            if not fn.endswith(".rpy"):
                continue
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, ROOT)
            with open(path, encoding="utf-8") as fh:
                for lineno, line in enumerate(fh, 1):
                    s = line.strip()
                    code = s.split("#", 1)[0].strip()
                    if not code:
                        continue
                    if re.match(r"play music\b", code):
                        if "fadein" not in code and not any(a in code for a in FADEIN_ALLOW):
                            viol.append("%s:%d play music に fadein なし: %s" % (rel, lineno, code))
                    if re.match(r"stop music\b", code) and "fadeout" not in code:
                        viol.append("%s:%d stop music に fadeout なし: %s" % (rel, lineno, code))
                    if "preferences.volumes" in code and fn not in VOLUME_ALLOWED_FILES:
                        viol.append("%s:%d 音量の直接操作（設定画面以外）: %s" % (rel, lineno, code))

    audio_rpy = os.path.join(ROOT, "audio.rpy")
    with open(audio_rpy, encoding="utf-8") as fh:
        for name, path in re.findall(r'define audio\.(\w+) = "([^"]+)"', fh.read()):
            if not os.path.exists(os.path.join(ROOT, path)):
                viol.append("audio.rpy 宣言 %s が実在しない: %s" % (name, path))

    if viol:
        print("AUDIT VIOLATIONS:")
        for v in viol:
            print("  " + v)
        return 1
    print("audio audit: OK（fadein/fadeout 方針・音量一元化・宣言実在 すべて適合）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
