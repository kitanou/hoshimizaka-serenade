"""images.rpy を生成する。 usage: python -m tools.gen_rpy

layeredimage 宣言は 3 キャラ分でほぼ同一なので、ここから書き出して手書きの重複をなくす。
"""
import os

from tools.svg import chars as C
from tools.svg import backgrounds as B

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME = os.path.join(ROOT, "hoshimizaka", "game")


def layered(cid):
    p = f"images/chars/{cid}"
    L = [f"layeredimage {cid}:", "    at char_zoom", "", f'    always "{p}/base_back.png"', "", "    group eyes:"]
    for k in C.EYE_KINDS:
        if k == "open":
            L += [f"        attribute e_open default:", f'            "{cid}_eyes_open"']
        else:
            L += [f"        attribute e_{k}:", f'            "{p}/eyes_{k}.png"']
    L += ["", "    group mouth:"]
    for k in C.MOUTH_KINDS:
        d = " default" if k == "neutral" else ""
        L += [f"        attribute m_{k}{d}:", f'            "{p}/mouth_{k}.png"']
    L += ["", "    group cheek:", "        attribute no_blush default null", "        attribute blush:",
          f'            "{p}/blush.png"', "", f'    always "{p}/base_front.png"', "", "    group brows:"]
    for k in C.BROW_KINDS:
        d = " default" if k == "normal" else ""
        L += [f"        attribute b_{k}{d}:", f'            "{p}/brows_{k}.png"']
    L += [""]
    return "\n".join(L)


def blink(cid):
    p = f"images/chars/{cid}"
    return f'''image {cid}_eyes_open:
    "{p}/eyes_open.png"
    choice:
        3.2
    choice:
        4.4
    choice:
        5.2
    "{p}/eyes_closed.png"
    0.12
    repeat
'''


## ミサキは参考画像（docs/images/character-misaki.webp）から切り出した 6 表情のバストアップ。
## 差分レイヤーは無いので、表情名ごとに 1 枚の画像を割り当てる（tools/import_misaki.py）。
MISAKI_FILES = {"normal": "normal", "smile": "smile", "blush": "blush", "surprise": "surprise",
                "sad": "sad", "angry": "angry"}
MISAKI_ALIAS = {"happy": "smile", "pout": "angry", "closed": "blush", "cool": "normal"}


def misaki_images():
    L = []
    for expr, f in MISAKI_FILES.items():
        L.append(f'image misaki {expr} = At("images/chars/misaki/bust_{f}.png", char_zoom)')
    for expr, f in MISAKI_ALIAS.items():
        L.append(f'image misaki {expr} = At("images/chars/misaki/bust_{MISAKI_FILES[f]}.png", char_zoom)')
    return "\n".join(L) + "\n"


def main():
    out = ["## 自動生成: python -m tools.gen_rpy  （手で編集しない）", "",
           "## ---- 背景 (1280x960 の画像を 0.5 倍で 640x480 に) ----"]
    for name in B.ALL:
        out.append(f'image bg {name} = Transform("images/bg/{name}.png", zoom=0.5)')
    out += ["", "## ---- CG ----"]
    for name in ("misaki_end", "touka_end", "normal_end"):
        out.append(f'image cg {name} = Transform("images/cg/{name}.png", zoom=0.5)')
    out += ["", "## ---- 立ち絵 ----", ""]
    out += [misaki_images()]
    for cid in C.CH:
        if cid != "misaki":
            out += [blink(cid), layered(cid)]
    open(os.path.join(GAME, "images.rpy"), "w", encoding="utf-8").write("\n".join(out) + "\n")
    print("images.rpy")


if __name__ == "__main__":
    main()
