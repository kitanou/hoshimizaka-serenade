"""OP 専用素材（絵コンテ docs/op-storyboard.md）。 usage: python -m tools.op_assets

- 背景プレート（人物なし）: 320x240 で描いて 32 色に減色。Ren'Py 側で 2 倍・Nearest で拡大 → ドットが見える
- キャラクター（透過）: 立ち絵 300x450 / アップ用 600x900 を 48 色に減色（ディザあり）
- 後ろ姿（ミサキ／冬華）
出力: hoshimizaka/game/images/op/
"""
import io
import os

import cairosvg
import numpy as np
from PIL import Image

from tools.svg import backgrounds as B
from tools.svg import chars as C

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "hoshimizaka", "game", "images", "op")
BUSTS = os.path.join(ROOT, "hoshimizaka", "game", "images", "chars", "misaki")


def render(svg, w, h):
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
    for expr in ("smile", "blush", "surprise"):
        src = Image.open(os.path.join(BUSTS, f"bust_{expr}.png")).convert("RGBA")
        save(reduce_colors(src.resize((300, 450), Image.LANCZOS), 48, True), f"chars/misaki_{expr}.png")
        save(reduce_colors(src, 64, True), f"chars/misaki_{expr}_hi.png")


def touka():
    poses = {
        "cool": dict(eyes="open", mouth="cool", brows="cool"),
        "smile": dict(eyes="open", mouth="smile", brows="normal"),
        "surprise": dict(eyes="surprise", mouth="surprise", brows="up"),
        "blush": dict(eyes="open", mouth="smile", brows="normal", blush=True),
    }
    for name, kw in poses.items():
        big = render(C.flat("touka", **kw), 600, 900)
        save(reduce_colors(big.resize((300, 450), Image.LANCZOS), 40, True), f"chars/touka_{name}.png")
        save(reduce_colors(big, 56, True), f"chars/touka_{name}_hi.png")


def backs():
    for cid in ("misaki", "touka"):
        big = render(C.back_svg(cid), 600, 900)
        save(reduce_colors(big.resize((300, 450), Image.LANCZOS), 32, True), f"chars/{cid}_back.png")


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

    misaki()
    touka()
    backs()
    glow()
