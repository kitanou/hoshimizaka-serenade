"""ミサキ・冬華の後ろ姿（OP CUT 10 / 12 用）を ComfyUI で生成し、OP 用の 300x450 透過 PNG にする。

  export COMFY_DIR=/path/to/ComfyUI
  $COMFY_DIR/venv/bin/python -m tools.char_back gen misaki --seed 1   # → output/back/<char>/..._s<seed>.png
  $COMFY_DIR/venv/bin/python -m tools.char_back install misaki         # 採用 seed でラスター化・配置

後ろ姿は参考画像・IP-Adapter が使えない（顔が写る）ので、プロンプトだけで作る。髪色・制服は前面立ち絵と合わせる。
出力: hoshimizaka/game/images/op/chars/<char>_back.png（300x450・48 色・ordered dither・アルファ 2 値）
"""
import argparse
import os

import numpy as np
from PIL import Image

from tools import comfy_gen as G
from tools import misaki_postprocess as PP

ROOT = G.ROOT
OUT = os.path.join(ROOT, "hoshimizaka", "game", "images", "op", "chars")
STYLE = ("retro artstyle, 1990s (style), official art, game cg, cel shading, soft shading, "
         "thin dark lineart, delicate lineart, soft colors")
FRAME = ("(from behind:1.5), (back view:1.4), (facing away:1.4), (back of head:1.3), upper body, "
         "standing, straight-on from behind, white background, simple background")
UNIFORM = ("serafuku, (white short-sleeved shirt:1.4), (navy blue sailor collar from the back:1.3), "
           "white stripes on the collar, red ribbon")
CHARS = {
    "misaki": dict(
        p="1girl, solo, (pink hair:1.2), (rose pink hair:1.3), (deep pink hair:1.1), short hair, bob cut, layered hair strands, hair highlights, " + UNIFORM,
        seed=2, pale_bg=True),
    "touka": dict(
        p="1girl, solo, (very long hair:1.4), straight hair, (blue hair:1.5), (royal blue hair:1.5), (medium blue hair:1.2), "
          "white hairband, hair covering the back, " + UNIFORM,
        seed=1, zoom=1.6),
}
NEG = ("lowres, bad anatomy, text, error, cropped, worst quality, low quality, jpeg artifacts, signature, "
       "watermark, blurry, 3d, photorealistic, chromatic aberration, glasses, eyewear, face, looking back, "
       "looking at viewer, front view, profile, from side, multiple girls, speech bubble, nsfw, "
       "high contrast, heavy shadow, thick outlines")
NEG_BY = {"misaki": ", blue hair, long hair, twintails, ponytail, purple hair, pastel pink, light pink hair, "
                    "green shirt, beige shirt, pink shirt, colored background",
          "touka": ", pink hair, purple hair, short hair, black hair, twintails, ponytail, cyan hair, "
                   "light blue hair, pastel, green shirt, beige shirt, colored background"}


def gen(char, seed=None):
    c = CHARS[char]
    seed = seed or c["seed"]
    pos = ", ".join([G.QUALITY, STYLE, c["p"], FRAME])
    return G.run(G.make_args(preset="bg", positive=pos, negative=NEG + NEG_BY[char], width=896, height=1152,
                             cn_weight=0, ip_weight=0, cfg=6.0, name=f"{char}_back", seed=seed,
                             out="output/back"))


def install(char, seed=None, colors=48):
    seed = seed or CHARS[char]["seed"]
    src = os.path.join(ROOT, "output", "back", "bg", f"{char}_back_s{seed}.png")
    im = Image.open(src).convert("RGB")
    if CHARS[char].get("pale_bg"):  # 背景に淡い青のグラデーションが乗る場合（髪が青系でないキャラのみ）
        a = np.asarray(im).copy()
        c = a.astype(int)
        pale = (c.min(axis=2) >= 150) & (c[..., 2] >= c[..., 0] + 8) & (c.max(axis=2) - c.min(axis=2) < 100)
        a[pale] = 255
        im = Image.fromarray(a)
    im = PP.remove_white_bg(im, side_limit=0.62, bottom=False)
    bb = im.getbbox()
    im = im.crop(bb)
    # 高さ 450 に揃えた上で zoom 倍する（冬華は細身で小さく見えるので、ミサキの頭・肩の大きさに合わせる）。
    # 上端揃え・左右中央で 300x450 に切る
    s = 450 / im.height * CHARS[char].get("zoom", 1.0)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    canvas = Image.new("RGBA", (300, 450), (0, 0, 0, 0))
    canvas.alpha_composite(im, ((300 - im.width) // 2, 0))
    a = canvas.getchannel("A")
    rgb = PP._quantize(canvas.convert("RGB"), colors, "ordered")
    out = rgb.convert("RGBA")
    out.putalpha(a.point(lambda v: 255 if v >= 128 else 0))
    path = os.path.join(OUT, f"{char}_back.png")
    out.save(path, optimize=True)
    print("wrote", path)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("cmd", choices=["gen", "install"])
    p.add_argument("char", choices=list(CHARS))
    p.add_argument("--seed", type=int, default=None)
    a = p.parse_args()
    gen(a.char, a.seed) if a.cmd == "gen" else install(a.char, a.seed)


if __name__ == "__main__":
    main()
