"""画像素材の一括生成。 usage: python -m tools.gen_images

出力先: hoshimizaka/game/images/ と hoshimizaka/game/gui/
cairo を Homebrew から読むため、macOS では次のように実行する:
  DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib ~/hoshimizaka-venv/bin/python -m tools.gen_images
"""
import io
import math
import os
import random
import sys

import cairosvg
from PIL import Image, ImageDraw, ImageFilter

from tools.svg import backgrounds as B
from tools.svg import chars as C

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME = os.path.join(ROOT, "hoshimizaka", "game")
IMG = os.path.join(GAME, "images")
GUI = os.path.join(GAME, "gui")


def out(path):
    full = os.path.join(GAME, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    return full


def svg_to_image(svg, w, h):
    png = cairosvg.svg2png(bytestring=svg.encode("utf-8"), output_width=w, output_height=h)
    return Image.open(io.BytesIO(png)).convert("RGBA")


def gen_backgrounds():
    for name, fn in B.ALL.items():
        svg_to_image(fn(), 1280, 960).convert("RGB").save(out(f"images/bg/{name}.png"), optimize=True)
        print("bg", name)


def gen_sprites():
    for cid in C.CH:
        if cid == "misaki":
            continue  # ミサキは参考画像から切り出す（tools/import_misaki.py）
        for name, svg in C.layers(cid).items():
            svg_to_image(svg, 600, 900).save(out(f"images/chars/{cid}/{name}.png"), optimize=True)
        print("chars", cid)


def paste_center(base, im, cx, y):
    base.alpha_composite(im, (int(cx - im.width / 2), int(y)))


def gen_cg():
    def char(cid, scale, **kw):
        if cid == "misaki":
            expr = "smile" if kw.get("eyes") != "happy" else "smile"
            im = Image.open(os.path.join(IMG, "chars", "misaki", f"bust_{expr}.png")).convert("RGBA")
            return im.resize((int(600 * scale), int(900 * scale)), Image.LANCZOS)
        im = svg_to_image(C.flat(cid, **kw), 600, 900)
        return im.resize((int(600 * scale), int(900 * scale)), Image.LANCZOS)

    def vignette(im):
        w, h = im.size
        mask = Image.new("L", (w, h), 0)
        ImageDraw.Draw(mask).ellipse((-w * .15, -h * .15, w * 1.15, h * 1.15), fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(90))
        dark = Image.new("RGBA", (w, h), (4, 4, 20, 255))
        return Image.composite(im, dark, mask)

    # ミサキEND: 夜の丘で振り向く
    bg = svg_to_image(B.night(True), 1280, 960)
    c = char("misaki", 1.5, eyes="happy", mouth="happy", blush=True)
    paste_center(bg, c, 640, -80)
    vignette(bg).convert("RGB").save(out("images/cg/misaki_end.png"), optimize=True)
    # 冬華END: 夜の屋上、望遠鏡のそば
    bg = svg_to_image(B.rooftop(True), 1280, 960)
    c = char("touka", 1.5, eyes="open", mouth="smile", blush=True)
    paste_center(bg, c, 880, -60)
    vignette(bg).convert("RGB").save(out("images/cg/touka_end.png"), optimize=True)
    # ノーマルEND: 坂の上で二人並んで星空を見上げる
    bg = svg_to_image(B.slope("night"), 1280, 960)
    paste_center(bg, char("misaki", 1.0, eyes="happy", mouth="smile"), 420, 150)
    paste_center(bg, char("touka", 1.0, eyes="open", mouth="smile"), 860, 150)
    vignette(bg).convert("RGB").save(out("images/cg/normal_end.png"), optimize=True)
    print("cg")


def gen_fx():
    # 花びら（ピンクの小さな楕円を回転）
    im = Image.new("RGBA", (36, 28), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((4, 6, 30, 20), fill=(255, 209, 224, 255), outline=(224, 122, 156, 255))
    im.rotate(25, expand=True, resample=Image.BICUBIC).save(out("images/fx/petal.png"))
    # 流れ星
    w, h = 360, 12
    s = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = s.load()
    for x in range(w):
        a = int(255 * (x / w) ** 1.6)
        for y in range(h):
            dy = abs(y - h / 2) / (h / 2)
            px[x, y] = (255, 246, 214, int(a * max(0, 1 - dy) ** 1.5))
    s.save(out("images/fx/shoot.png"))
    # 星の輝き（スパーク）
    sp = svg_to_image(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">'
        '<polygon points="50,0 60,40 100,50 60,60 50,100 40,60 0,50 40,40" fill="#fff"/></svg>', 68, 68)
    sp.save(out("images/fx/spark.png"))
    # 星屑レイヤー（OP背景用・2枚）
    rnd = random.Random(7)
    for n in (1, 2):
        st = Image.new("RGBA", (640, 960), (0, 0, 0, 0))
        d = ImageDraw.Draw(st)
        for _ in range(90 * n):
            x, y = rnd.randrange(640), rnd.randrange(960)
            r = rnd.choice([1, 1, 1, 2]) if n == 1 else rnd.choice([1, 2, 2, 3])
            a = rnd.randrange(120, 255)
            d.rectangle((x, y, x + r, y + r), fill=(255, 250, 230, a))
        st.save(out(f"images/fx/stars{n}.png"))
    print("fx")


def gen_op_art():
    """OP用の背景パーツ（ストライプ・円・サンバースト・集中線・ハーフトーン）。"""
    import numpy as np
    # ストライプ: 水平周期 96px（ループ用）。832x480
    w, h = 832, 480
    yy, xx = np.mgrid[0:h, 0:w]
    k = (((xx + yy) % 96) // 48).astype(int)
    pal = np.array([[255, 127, 176], [255, 182, 211]], dtype=np.uint8)
    Image.fromarray(pal[k], "RGB").save(out("images/op/stripes.png"))
    # 円
    n = 420
    yy, xx = np.mgrid[0:n, 0:n]
    r = np.sqrt((xx - n / 2) ** 2 + (yy - n / 2) ** 2) / (n / 2)
    cols = np.zeros((n, n, 4), dtype=np.uint8)
    for c, (a, b) in enumerate(zip((255, 246, 176), (255, 159, 63))):
        pass
    t = np.clip(r, 0, 1)
    cols[..., 0] = 255
    cols[..., 1] = (246 - (246 - 159) * t).astype(np.uint8)
    cols[..., 2] = (176 - (176 - 63) * t).astype(np.uint8)
    cols[..., 3] = np.where(r <= 1, 230, 0)
    Image.fromarray(cols, "RGBA").save(out("images/op/circle.png"))
    # 放射パターン（サンバースト/集中線）
    m = 1300
    yy, xx = np.mgrid[0:m, 0:m]
    ang = (np.degrees(np.arctan2(yy - m / 2, xx - m / 2)) + 360) % 360
    k = ((ang // 9) % 2).astype(int)
    pal = np.array([[255, 210, 63], [255, 143, 184]], dtype=np.uint8)
    Image.fromarray(pal[k], "RGB").save(out("images/op/sunburst.png"))
    ang2 = ang % 13
    k2 = (ang2 < 2).astype(int) + 2 * ((ang2 >= 2) & (ang2 < 7)).astype(int)
    pal2 = np.array([[255, 233, 242], [255, 255, 255], [255, 208, 228]], dtype=np.uint8)
    Image.fromarray(pal2[np.where(ang2 < 2, 1, np.where(ang2 < 7, 2, 0))], "RGB").save(out("images/op/speed.png"))
    # ハーフトーン
    for name, bg, dot in (("halftone_y", (255, 228, 107), (255, 184, 0)), ("halftone_c", (166, 236, 255), (43, 181, 232))):
        im = Image.new("RGB", (640, 480), bg)
        d = ImageDraw.Draw(im)
        for y in range(0, 480, 14):
            for x in range(0, 640, 14):
                d.ellipse((x, y, x + 8, y + 8), fill=dot)
        im.save(out(f"images/op/{name}.png"))
    print("op art")


def rounded_frame(w, h, margin, radius, top=(28, 34, 96, 224), bottom=(10, 12, 44, 230),
                  line=(207, 224, 255, 255), glow=True):
    """90年代風の二重線ウィンドウ。(w,h) の画像の margin 内に描く。"""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    inner = Image.new("RGBA", (w - 2 * margin, h - 2 * margin))
    px = inner.load()
    for y in range(inner.height):
        t = y / max(1, inner.height - 1)
        col = tuple(int(top[i] * (1 - t) + bottom[i] * t) for i in range(4))
        for x in range(inner.width):
            px[x, y] = col
    mask = Image.new("L", inner.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, inner.width - 1, inner.height - 1), radius, fill=255)
    im.paste(inner, (margin, margin), mask)
    d = ImageDraw.Draw(im)
    box = (margin, margin, w - margin - 1, h - margin - 1)
    d.rounded_rectangle((box[0] - 2, box[1] - 2, box[2] + 2, box[3] + 2), radius + 2, outline=(26, 31, 85, 255), width=1)
    d.rounded_rectangle(box, radius, outline=line, width=1)
    d.rounded_rectangle((box[0] + 2, box[1] + 2, box[2] - 2, box[3] - 2), max(1, radius - 2), outline=line, width=1)
    if glow:
        g = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(g).rounded_rectangle((box[0] + 4, box[1] + 4, box[2] - 4, box[3] - 4), max(1, radius - 3),
                                            outline=(120, 160, 255, 90), width=3)
        g = g.filter(ImageFilter.GaussianBlur(2))
        im.alpha_composite(g)
    return im


def gen_ui():
    # テキストボックス 640x128（左右14・下12の余白を内包）
    rounded_frame(640, 128, 12, 8).save(out("gui/textbox.png"))
    # 名前欄
    pal = {
        "default": ((154, 166, 200), (90, 100, 136)),
        "yuki": ((168, 230, 160), (63, 154, 90)),
        "misaki": ((255, 166, 204), (224, 80, 138)),
        "touka": ((143, 214, 255), (58, 106, 208)),
        "kaede": ((255, 208, 140), (230, 140, 40)),
        "unknown": ((154, 166, 200), (90, 100, 136)),
    }
    for name, (a, b) in pal.items():
        w, h = 96, 24
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        px = im.load()
        for y in range(h):
            t = y / (h - 1)
            for x in range(w):
                px[x, y] = tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3)) + (255,)
        m = Image.new("L", (w, h), 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), 5, fill=255)
        im.putalpha(m)
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, w - 1, h - 1), 5, outline=(255, 255, 255, 255), width=2)
        im.save(out(f"gui/namebox_{name}.png"))
    # 選択肢ボタン
    for state, (top, bot, line) in {
        "idle": ((40, 44, 130, 235), (16, 16, 60, 242), (207, 224, 255, 255)),
        "hover": ((255, 143, 192, 245), (214, 60, 124, 250), (255, 255, 255, 255)),
    }.items():
        rounded_frame(360, 34, 1, 6, top, bot, line, glow=False).save(out(f"gui/button/choice_{state}_background.png"))
    # CRT オーバーレイ（走査線＋周辺減光）。1280x960 を zoom 0.5 で使う
    w, h = 1280, 960
    crt = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(crt)
    for y in range(0, h, 6):
        d.rectangle((0, y, w, y + 1), fill=(0, 0, 0, 52))
    vig = Image.new("L", (w, h), 0)
    ImageDraw.Draw(vig).ellipse((-w * .18, -h * .18, w * 1.18, h * 1.18), fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(120))
    dark = Image.new("RGBA", (w, h), (0, 0, 0, 115))
    dark.putalpha(Image.eval(vig, lambda v: int(115 * (255 - v) / 255)))
    crt.alpha_composite(dark)
    crt.save(out("gui/crt.png"))
    print("ui")


def gen_ui_parts():
    """設定画面などで使う部品（ボタン背景・バー・スライダー・スクロールバー・チェック等）。"""
    def solid(w, h, col, border=None, radius=0):
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, w - 1, h - 1), radius, fill=col, outline=border)
        return im

    DK, MD, LT, PK, GD = (16, 20, 64, 230), (40, 48, 120, 235), (207, 224, 255, 255), (255, 95, 162, 255), (255, 226, 122, 255)
    # 汎用ボタン背景（ほぼ透明。hover で薄く光る）
    solid(150, 22, (0, 0, 0, 0)).save(out("gui/button/idle_background.png"))
    solid(150, 22, (255, 95, 162, 90), None, 3).save(out("gui/button/hover_background.png"))
    # セーブスロット
    solid(150, 114, (16, 20, 64, 200), LT, 4).save(out("gui/button/slot_idle_background.png"))
    solid(150, 114, (60, 40, 120, 220), GD, 4).save(out("gui/button/slot_hover_background.png"))
    # チェック/ラジオ（foreground）
    for name in ("check", "radio"):
        for sel in ("", "selected_"):
            im = Image.new("RGBA", (16, 22), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            box = (1, 5, 13, 17)
            shape = d.rectangle if name == "check" else d.ellipse
            shape(box, outline=LT, width=1)
            if sel:
                (d.rectangle if name == "check" else d.ellipse)((4, 8, 10, 14), fill=PK)
            im.save(out(f"gui/button/{name}_{sel}foreground.png"))
    # バー（Frame 用）
    for pos, size in (("left", (200, 14)), ("right", (200, 14)), ("top", (14, 200)), ("bottom", (14, 200))):
        solid(*size, PK if pos in ("left", "top") else (40, 48, 120, 235), LT, 3).save(out(f"gui/bar/{pos}.png"))
    # スライダー
    for state, thumb in (("idle", LT), ("hover", GD)):
        solid(200, 14, (40, 48, 120, 235), LT, 3).save(out(f"gui/slider/horizontal_{state}_bar.png"))
        solid(8, 14, thumb, None, 2).save(out(f"gui/slider/horizontal_{state}_thumb.png"))
        solid(14, 200, (40, 48, 120, 235), LT, 3).save(out(f"gui/slider/vertical_{state}_bar.png"))
        solid(14, 8, thumb, None, 2).save(out(f"gui/slider/vertical_{state}_thumb.png"))
    # スクロールバー
    for state, thumb in (("idle", (150, 170, 230, 255)), ("hover", GD)):
        solid(300, 6, (16, 20, 64, 200), None, 2).save(out(f"gui/scrollbar/horizontal_{state}_bar.png"))
        solid(300, 6, thumb, None, 2).save(out(f"gui/scrollbar/horizontal_{state}_thumb.png"))
        solid(6, 300, (16, 20, 64, 200), None, 2).save(out(f"gui/scrollbar/vertical_{state}_bar.png"))
        solid(6, 300, thumb, None, 2).save(out(f"gui/scrollbar/vertical_{state}_thumb.png"))
    # メニュー背景: 夜空のグラデ（星付き）
    rnd = random.Random(11)
    for name in ("main_menu", "game_menu"):
        im = Image.new("RGB", (640, 480))
        px = im.load()
        for y in range(480):
            t = y / 479
            c = (int(10 + 30 * t), int(14 + 34 * t), int(50 + 60 * t))
            for x in range(640):
                px[x, y] = c
        d = ImageDraw.Draw(im)
        for _ in range(110):
            x, y = rnd.randrange(640), rnd.randrange(480)
            d.rectangle((x, y, x + 1, y + 1), fill=(255, 250, 230))
        im.save(out(f"gui/{name}.png"))
    # オーバーレイ: ナビゲーション側を暗く
    nav = Image.new("RGBA", (640, 480), (0, 0, 20, 0))
    px = nav.load()
    for x in range(640):
        a = int(170 * max(0, 1 - x / 240))
        for y in range(480):
            px[x, y] = (4, 6, 30, a)
    nav.save(out("gui/overlay/game_menu.png"))
    nav.save(out("gui/overlay/main_menu.png"))
    Image.new("RGBA", (640, 480), (4, 6, 26, 190)).save(out("gui/overlay/confirm.png"))
    print("ui parts")


def main():
    only = set(sys.argv[1:])
    steps = dict(bg=gen_backgrounds, chars=gen_sprites, cg=gen_cg, fx=gen_fx, op=gen_op_art, ui=gen_ui, parts=gen_ui_parts)
    for k, fn in steps.items():
        if not only or k in only:
            fn()


if __name__ == "__main__":
    main()
