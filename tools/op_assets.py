"""OP 専用素材（絵コンテ docs/op-storyboard.md）。 usage: python -m tools.op_assets

- 背景プレート（人物なし）: 320x240 で描いて 32 色に減色。Ren'Py 側で 2 倍・Nearest で拡大 → ドットが見える
- キャラクター（透過）: 立ち絵 300x450 / アップ用 600x900 を 48 色に減色（ディザあり）
- 後ろ姿（ミサキ／冬華）
出力: hoshimizaka/game/images/op/
"""
import io
import os

import numpy as np
from PIL import Image

from tools.svg import backgrounds as B
from tools.svg import chars as C

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "hoshimizaka", "game", "images", "op")
BUSTS = os.path.join(ROOT, "hoshimizaka", "game", "images", "chars", "misaki")


def render(svg, w, h):
    import cairosvg  # SVG を描くときだけ必要（ComfyUI の venv には無い）
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=w, output_height=h)
    return Image.open(io.BytesIO(png)).convert("RGBA")


def reduce_colors(im, colors, dither):
    """RGBA を減色する。アルファは 2 値化（ドット絵の縁にする）。"""
    a = np.asarray(im.getchannel("A"))
    rgb = im.convert("RGB").quantize(colors=colors, method=Image.Quantize.MEDIANCUT,
                                     dither=Image.Dither.FLOYDSTEINBERG if dither else Image.Dither.NONE).convert("RGB")
    out = rgb.convert("RGBA")
    out.putalpha(Image.fromarray(np.where(a >= 128, 255, 0).astype(np.uint8)))
    return out


def save(im, name):
    path = os.path.join(OUT, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.save(path, optimize=True)
    print(name, im.size)


def backgrounds():
    for name, fn in B.OP_BG.items():
        im = render(fn(), 320, 240).convert("RGB")
        im = im.quantize(colors=32, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert("RGB")
        save(im, f"{name}.png")


def misaki():
    """美咲（OP 用表情）。本編と同じ layeredimage のパーツ差分（tools/misaki_parts.py）を合成して減色する。"""
    from tools import misaki_parts as P
    src = os.path.join(ROOT, "hoshimizaka", "game", "images", "chars", "misaki")
    poses = {
        "smile": ("open", "smile", "normal", False),
        "blush": ("open", "smile", "normal", True),
        "surprise": ("surprise", "surprise", "up", False),
    }
    for name, (e, m, b, bl) in poses.items():
        big = P.compose(src, e, m, b, bl)
        save(reduce_colors(big.resize((300, 450), Image.LANCZOS), 48, True), f"chars/misaki_{name}.png")
        save(reduce_colors(big, 64, True), f"chars/misaki_{name}_hi.png")


def touka():
    """冬華（OP 用表情）。ComfyUI 生成のパーツ差分（tools/misaki_parts.py --char touka）を合成して減色する。"""
    from tools import misaki_parts as P
    src = os.path.join(ROOT, "hoshimizaka", "game", "images", "chars", "touka")
    poses = {
        "cool": ("open", "cool", "cool", False),
        "smile": ("open", "smile", "normal", False),
        "surprise": ("surprise", "surprise", "up", False),
        "blush": ("open", "smile", "normal", True),
    }
    for name, (e, m, b, bl) in poses.items():
        big = P.compose(src, e, m, b, bl)
        save(reduce_colors(big.resize((300, 450), Image.LANCZOS), 40, True), f"chars/touka_{name}.png")
        save(reduce_colors(big, 56, True), f"chars/touka_{name}_hi.png")


def backs():
    """後ろ姿は ComfyUI 生成（tools/char_back.py）に移行した。旧 SVG 版は使わない。"""
    raise SystemExit("後ろ姿は python -m tools.char_back install misaki|touka で作る")


def glow():
    n = 400
    yy, xx = np.mgrid[0:n, 0:n]
    r = np.sqrt((xx - n / 2) ** 2 + (yy - n / 2) ** 2) / (n / 2)
    a = np.clip(1 - r, 0, 1) ** 1.8
    im = np.zeros((n, n, 4), np.uint8)
    im[..., 0], im[..., 1], im[..., 2] = 255, 236, 180
    im[..., 3] = (a * 255).astype(np.uint8)
    save(Image.fromarray(im, "RGBA"), "glow.png")


if __name__ == "__main__":
    # OP 背景（bg_op_*.png）は ComfyUI 生成（tools/bg_gen.py）に移行したので、ここでは作り直さない。
    # 旧ベクター調に戻したいときだけ backgrounds() を明示的に呼ぶこと。

    # misaki(): 美咲の OP 表情は chars/misaki/bust_*.png から。touka(): 新パーツから。
    # 後ろ姿は tools/char_back.py。ここでは glow だけ再生成しても害がない
    misaki()
    touka()
    glow()
