"""生成画像を 90 年代家庭用機のゲーム素材風ラスターに変換する（Issue #65 後処理）。

生成モデルにはドットを描かせず、ここで「画面解像度への縮小 → 減色 → ディザ → 透過」を行う。
ゲームは 640x480（gui.init）で、立ち絵は 2 倍解像度で保存して char_zoom 0.5 で表示する規約のため、
画面解像度でディザを打ってから Nearest Neighbor で 2 倍にして保存する（ドットが 1 画面ピクセルに揃う）。

変種（Issue「5. 生成後のドット処理・比較」）:
  A: 画面解像度へ縮小のみ（LANCZOS）
  B: さらに 1/2 に縮小 → Nearest で戻す（粗いドット）
  C: 画面解像度で減色 + ordered dither（Bayer 4x4）
  D: C + Floyd–Steinberg を併用せず、B の粗さで減色 + ordered dither
  FS: 画面解像度で減色 + Floyd–Steinberg（比較用）

usage:
  python -m tools.misaki_postprocess output/comfy/expr/expr_smile_s5.png --kind bust
  python -m tools.misaki_postprocess output/comfy/stand/stand_s5.png --kind stand --variants A,C,FS
  python -m tools.misaki_postprocess <png> --kind bust --variant C --colors 64 --dest hoshimizaka/game/images/chars/misaki/gen_bust_smile.png
出力（--dest なし）: <入力と同じ場所>/pp/<名前>_<変種>.png と 640x480 プレビュー <名前>_preview.png
"""
import argparse
import os

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BG = os.path.join(ROOT, "hoshimizaka", "game", "images", "bg", "classroom.png")
SCREEN = (640, 480)
# 画面上の表示サイズ（char_zoom 0.5 適用後）。bust は既存 bust_*.png（600x900 → 300x450）に合わせる
TARGET_H = {"bust": 450, "stand": 468}
BAYER4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0 - 0.5


def remove_white_bg(im, thr=236, side_limit=1.0, bottom=True):
    """外周から連続する白を透過にする（tools/import_misaki.cutout と同じ考え方）。
    バストは白い制服が下辺・左右下部に接するため、bottom=False / side_limit<1 で起点から外す。"""
    from collections import deque
    rgb = np.asarray(im.convert("RGB")).astype(np.int16)
    h, w, _ = rgb.shape
    white = rgb.min(axis=2) >= thr
    bg = np.zeros((h, w), bool)
    q = deque()
    for x in range(w):
        for y in ((0, h - 1) if bottom else (0,)):
            if white[y, x]:
                q.append((y, x))
    for y in range(int(h * side_limit)):
        for x in (0, w - 1):
            if white[y, x]:
                q.append((y, x))
    while q:
        y, x = q.popleft()
        if bg[y, x] or not white[y, x]:
            continue
        bg[y, x] = True
        for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
            if 0 <= ny < h and 0 <= nx < w and not bg[ny, nx] and white[ny, nx]:
                q.append((ny, nx))
    if not bottom:
        # 胸元（下 30%）は白い制服の輪郭が薄く背景とつながるため、
        # 行ごとに最左〜最右のインク（非白）の間を不透明にして穴を塞ぐ
        ink = rgb.min(axis=2) < 225
        for y in range(int(h * 0.7), h):
            xs = np.flatnonzero(ink[y])
            if len(xs) > 1:
                bg[y, xs[0]:xs[-1] + 1] = False
    a = np.where(bg, 0, 255).astype(np.uint8)
    out = im.convert("RGBA")
    out.putalpha(Image.fromarray(a))
    return out


def _quantize(rgb, colors, dither):
    """rgb: PIL RGB。dither: 'none' | 'ordered' | 'fs'"""
    pal_src = rgb.quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    if dither == "fs":
        return rgb.quantize(palette=pal_src, dither=Image.Dither.FLOYDSTEINBERG).convert("RGB")
    if dither == "ordered":
        arr = np.asarray(rgb).astype(np.float32)
        h, w, _ = arr.shape
        t = np.tile(BAYER4, (h // 4 + 1, w // 4 + 1))[:h, :w, None]
        # 振幅はおおよそパレット間隔。色数が少ないほど網点が強く出る
        amp = 255.0 / (colors ** (1 / 3))
        arr = np.clip(arr + t * amp, 0, 255).astype(np.uint8)
        return Image.fromarray(arr).quantize(palette=pal_src, dither=Image.Dither.NONE).convert("RGB")
    return pal_src.convert("RGB")


def rasterize(rgba, kind, variant, colors=64):
    """透過済み RGBA → 画面解像度でラスター化し、2 倍 Nearest にした RGBA を返す。"""
    bbox = rgba.getbbox()
    rgba = rgba.crop(bbox)
    th = TARGET_H[kind]
    tw = round(rgba.width * th / rgba.height)
    small = rgba.resize((tw, th), Image.LANCZOS)
    if variant in ("B", "D"):
        small = small.resize((tw // 2, th // 2), Image.LANCZOS)
    # 90 年代スプライト同様、アルファは 2 値（半透明の縁を作らない）。縁は白で埋めず近傍色のまま
    alpha = (np.asarray(small)[..., 3] >= 128)
    rgb = Image.fromarray(np.asarray(small)[..., :3])
    if variant in ("C", "D"):
        rgb = _quantize(rgb, colors, "ordered")
    elif variant == "FS":
        rgb = _quantize(rgb, colors, "fs")
    out = np.dstack([np.asarray(rgb), np.where(alpha, 255, 0).astype(np.uint8)])
    out = Image.fromarray(out, "RGBA")
    if variant in ("B", "D"):
        out = out.resize((tw, th), Image.NEAREST)
    return out.resize((out.width * 2, out.height * 2), Image.NEAREST)


def preview(sprites, path):
    """640x480 の教室背景に並べた等倍プレビュー（ゲーム画面での見え方確認用）。"""
    bg = Image.open(BG).convert("RGB").resize(SCREEN) if os.path.exists(BG) else Image.new("RGB", SCREEN, "gray")
    canvas = Image.new("RGB", (SCREEN[0] * len(sprites), SCREEN[1]))
    for i, (name, sp) in enumerate(sprites):
        scr = bg.copy()
        s = sp.resize((sp.width // 2, sp.height // 2), Image.NEAREST)  # char_zoom 0.5
        scr.paste(s, ((SCREEN[0] - s.width) // 2, SCREEN[1] - s.height + 12), s)
        canvas.paste(scr, (i * SCREEN[0], 0))
    canvas.save(path)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("inputs", nargs="+")
    p.add_argument("--kind", choices=list(TARGET_H), default="bust")
    p.add_argument("--variants", default="A,B,C,D,FS")
    p.add_argument("--colors", type=int, default=64)
    p.add_argument("--dest", default=None, help="1 入力・1 変種のとき、その PNG を指定パスに書き出す")
    a = p.parse_args()
    variants = a.variants.split(",")
    for src in a.inputs:
        if a.kind == "bust":
            rgba = remove_white_bg(Image.open(src), side_limit=0.62, bottom=False)
        else:
            rgba = remove_white_bg(Image.open(src))
        if a.dest:
            assert len(a.inputs) == 1 and len(variants) == 1, "--dest は 1 入力・1 変種のみ"
            sp = rasterize(rgba, a.kind, variants[0], a.colors)
            if a.kind == "bust":  # 既存 bust_*.png と同じ 600x900 透明キャンバス・下揃え
                c = Image.new("RGBA", (600, 900), (0, 0, 0, 0))
                c.alpha_composite(sp, ((600 - sp.width) // 2, 900 - sp.height))
                sp = c
            os.makedirs(os.path.dirname(os.path.abspath(a.dest)), exist_ok=True)
            sp.save(a.dest, optimize=True)
            print("wrote", a.dest, sp.size)
            continue
        outdir = os.path.join(os.path.dirname(src), "pp")
        os.makedirs(outdir, exist_ok=True)
        name = os.path.splitext(os.path.basename(src))[0]
        sprites = []
        for v in variants:
            sp = rasterize(rgba, a.kind, v, a.colors)
            sp.save(os.path.join(outdir, f"{name}_{v}.png"), optimize=True)
            sprites.append((v, sp))
        preview(sprites, os.path.join(outdir, f"{name}_preview.png"))
        print("wrote", outdir, name, ",".join(variants))


if __name__ == "__main__":
    main()
