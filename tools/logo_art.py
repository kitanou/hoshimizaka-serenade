#!/usr/bin/env python3
"""タイトルロゴ・会社名プレート画像の生成（#56）。決定論的 PIL レンダリング。

出力:
  hoshimizaka/game/gui/title_logo.png    … 日本語+英字タイトルロゴ（透過・1x 560x116）
  hoshimizaka/game/gui/company_plate.png … 星屑工房 STARDUST WORKS 名 plate（300x24）

画風: テーマ色（ミサキ=Pink #ff5fa2 / 冬華=Cyan #7fe3ff / 濃紫 #2a0f5c）で
现有 GUI・背景と同じ 96色+白黒・Bayer 4x4 ディザに量子化。フォントは同梱の
Source Han Sans Lite（SIL OFL。hoshimizaka/game/fonts/OFL.txt）。
usage: python3 tools/logo_art.py
"""
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GUI = os.path.join(ROOT, "hoshimizaka", "game", "gui")
FONT = os.path.join(ROOT, "hoshimizaka", "game", "fonts", "SourceHanSansLite.ttf")

# テーマパレット（GUI・背景仕様に合わせる）
DARK = (42, 15, 92)        # 濃紫アウトライン/影
DEEP = (28, 16, 61)        # 一段暗い影
PINK = (255, 47, 134)      # ミサキテーマ輪郭
PINK_HI = (255, 225, 240)  # 見出しハイライト
Cyan = (127, 227, 255)     # 冬華テーマ（英字行）
GOLD = (255, 226, 122)     # 星スパーク
WHITE = (255, 255, 255)

# Bayer 4x4 閾値行列（正規化）
BAYER4 = [
    [0, 8, 2, 10],
    [12, 4, 14, 6],
    [3, 11, 1, 9],
    [15, 7, 13, 5],
]


def font(sz):
    return ImageFont.truetype(FONT, sz)


def draw_text_mask(mask_dr, xy, s, f, anchor="la", stroke=0):
    mask_dr.text(xy, s, font=f, fill=255, anchor=anchor, stroke_width=stroke)


def quantize_dither(img, colors=96):
    """テーマ固定色へ量子化し、残りは Bayer 4x4 オーディザで疑似階調化する。"""
    pal = [DARK, DEEP, PINK, PINK_HI, Cyan, GOLD, WHITE, (0, 0, 0),
           (255, 95, 162), (150, 60, 140), (95, 60, 160), (40, 140, 200)]
    quantize_dither._pal = pal
    px = img.load()
    w, h = img.size
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    op = out.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            # 元ピクセルを最近傍テーマ色へスナップ後、誤差をディザ閾値で別色へ丸める
            rr, gg, bb = _snap_with_dither(r, g, b, x, y)
            op[x, y] = (rr, gg, bb, a)
    return out


def _snap_with_dither(r, g, b, x, y):
    thr = (BAYER4[y % 4][x % 4] + 0.5) / 16.0 * 96.0 - 48.0
    best, bestd = None, 1 << 30
    for c in quantize_dither._pal:
        dr = r - c[0] - thr
        dg = g - c[1] - thr
        db = b - c[2] - thr
        d = dr * dr + dg * dg + db * db
        if d < bestd:
            bestd, best = d, c
    return best


def star(dr, cx, cy, r, col):
    """四芒星（90s スパーク）。"""
    dr.polygon([(cx, cy - r), (cx + r // 4, cy - r // 4), (cx + r, cy),
                (cx + r // 4, cy + r // 4), (cx, cy + r), (cx - r // 4, cy + r // 4),
                (cx - r, cy), (cx - r // 4, cy - r // 4)], fill=col)


def make_title_logo():
    W, H = 560, 116
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    fmain = font(44)
    teng = "H O S H I M I Z A K A   S E R E N A D E"
    feng = font(14)
    jp = "星見坂のセレナーデ"

    # 1) 洋硬影（オフセット 2x）
    dr.text((W // 2 + 3, 30 + 3), jp, font=fmain, fill=(20, 8, 44, 255), anchor="mm")
    dr.text((W // 2 + 2, 30 + 2), jp, font=fmain, fill=DEEP + (255,), anchor="mm")
    # 2) 濃紫太アウトライン
    dr.text((W // 2, 30), jp, font=fmain, fill=DARK + (255,), anchor="mm", stroke_width=6)
    # 3) ピンク細アウトライン
    dr.text((W // 2, 30), jp, font=fmain, fill=PINK + (255,), anchor="mm", stroke_width=2)
    # 4) グラデ塗り（上:白→下:ピンク）をテキストマスクで合成
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    md.text((W // 2, 30), jp, font=fmain, fill=255, anchor="mm")
    grad = Image.new("RGBA", (W, H))
    gd = ImageDraw.Draw(grad)
    for y in range(H):
        t = y / (H - 1)
        if t < 0.45:
            k = t / 0.45
            c = tuple(int(WHITE[i] + (PINK_HI[i] - WHITE[i]) * k) for i in range(3))
        else:
            k = (t - 0.45) / 0.55
            c = tuple(int(PINK_HI[i] + (255, 140, 190)[i] * k) for i in range(3))
            c = tuple(int(c[i]) for i in range(3))
        gd.line([(0, y), (W, y)], fill=c + (255,))
    img.paste(grad, (0, 0), mask)

    # 5) 英字行（冬華テーマ色・濃紺縁）
    dr.text((W // 2 + 1, 87 + 1), teng, font=feng, fill=DEEP + (255,), anchor="mm", stroke_width=3)
    dr.text((W // 2, 87), teng, font=feng, fill=Cyan + (255,), anchor="mm")

    # 6) スパーク（決定点。テーマカラーの四芒星）
    for cx, cy, r, col in [(36, 22, 9, WHITE), (522, 18, 8, Cyan), (30, 96, 6, Cyan),
                           (532, 100, 6, PINK), (96, 8, 5, GOLD), (468, 8, 5, WHITE),
                           (120, 108, 4, PINK_HI), (440, 110, 4, GOLD)]:
        star(dr, cx, cy, r, col + (255,))
    # 微細な星の粒（決定的）
    for i in range(40):
        x = (i * 83 + 17) % W
        y = (i * 51 + 9) % H
        if abs(x - W // 2) < 210 and 4 < y < 104:
            continue
        dr.point((x, y), fill=(WHITE if i % 3 else Cyan) + (150,))

    out = quantize_dither(img, 96)
    os.makedirs(GUI, exist_ok=True)
    out.save(os.path.join(GUI, "title_logo.png"))
    print("wrote gui/title_logo.png", out.size)


def make_company_plate():
    W, H = 300, 24
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    dr.rounded_rectangle([0, 0, W - 1, H - 1], radius=4, fill=(26, 16, 80, 235),
                         outline=PINK + (255,), width=1)
    dr.line([(3, 2), (W - 4, 2)], fill=GOLD + (200,), width=1)
    f = font(12)
    dr.text((W // 2, 13), "星屑工房 STARDUST WORKS", font=f, fill=WHITE + (255,), anchor="mm")
    star(dr, 16, 13, 5, GOLD + (255,))
    star(dr, W - 16, 13, 5, GOLD + (255,))
    out = quantize_dither(img, 96)
    out.save(os.path.join(GUI, "company_plate.png"))
    print("wrote gui/company_plate.png", out.size)


if __name__ == "__main__":
    make_title_logo()
    make_company_plate()
