"""ミサキの参考画像（docs/images/character-misaki.webp）から表情6種のバストアップを切り出す。

usage: python -m tools.import_misaki
出力: hoshimizaka/game/images/chars/misaki/bust_<表情>.png （600x900 の透明キャンバスに下揃えで配置）
白背景は外周からの塗りつぶしで透過する。最大の連結成分だけを残し、枠外の「!」などを除く。
"""
import os

import numpy as np
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "docs", "images", "character-misaki.webp")
OUT = os.path.join(ROOT, "hoshimizaka", "game", "images", "chars", "misaki")

# 表情ごとの切り出し範囲 (left, top, right, bottom)。ラベル帯（「通常」など）は含めない
PANELS = {
    "normal":   (396, 6, 668, 352),
    "smile":    (672, 6, 945, 352),
    "blush":    (950, 6, 1210, 352),
    "surprise": (396, 408, 668, 732),
    "sad":      (672, 408, 945, 732),
    "angry":    (950, 408, 1210, 732),
}
CANVAS = (600, 900)
BUST_W = 560


def cutout(im):
    """外周の白を透過にして RGBA を返す。"""
    rgb = np.asarray(im.convert("RGB")).astype(np.int16)
    h, w, _ = rgb.shape
    white = (rgb.min(axis=2) >= 236)
    # 外周（上・左・右。下辺は服の白が接するので除く）から白領域を塗りつぶす
    bg = np.zeros((h, w), bool)
    stack = [(0, x) for x in range(w) if white[0, x]]
    stack += [(y, 0) for y in range(h) if white[y, 0]]
    stack += [(y, w - 1) for y in range(h) if white[y, w - 1]]
    while stack:
        y, x = stack.pop()
        if y < 0 or y >= h or x < 0 or x >= w or bg[y, x] or not white[y, x]:
            continue
        bg[y, x] = True
        stack += [(y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)]
    alpha = np.where(bg, 0, 255).astype(np.uint8)
    # 最大の連結成分だけ残す
    keep = largest_component(alpha > 0)
    alpha = np.where(keep, 255, 0).astype(np.uint8)
    a = Image.fromarray(alpha).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.8))
    out = im.convert("RGBA")
    out.putalpha(a)
    return out


def largest_component(mask):
    h, w = mask.shape
    seen = np.zeros_like(mask, bool)
    best = None
    for y0 in range(h):
        for x0 in range(w):
            if mask[y0, x0] and not seen[y0, x0]:
                comp, stack = [], [(y0, x0)]
                seen[y0, x0] = True
                while stack:
                    y, x = stack.pop()
                    comp.append((y, x))
                    for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                        if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = True
                            stack.append((ny, nx))
                if best is None or len(comp) > len(best):
                    best = comp
    out = np.zeros_like(mask)
    for y, x in best:
        out[y, x] = True
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    sheet = Image.open(SRC).convert("RGB")
    for name, box in PANELS.items():
        bust = cutout(sheet.crop(box))
        bbox = bust.getbbox()
        bust = bust.crop(bbox)
        scale = BUST_W / bust.width
        bust = bust.resize((BUST_W, int(bust.height * scale)), Image.LANCZOS)
        canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
        canvas.alpha_composite(bust, ((CANVAS[0] - BUST_W) // 2, CANVAS[1] - bust.height))
        canvas.save(os.path.join(OUT, f"bust_{name}.png"), optimize=True)
        print(name, bust.size)


if __name__ == "__main__":
    main()
