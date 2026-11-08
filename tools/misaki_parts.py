"""美咲の立ち絵パーツ差分（layeredimage 用レイヤー）を作る（docs/demo-design.md §7.1, Issue #65）。

1 枚の基準バスト（tools.comfy_gen の expr ①清書パスの出力）に対し、
部位ごとのマスク（目・口・眉）だけを ComfyUI で inpaint して差分を作る。
どの差分も同じ基準画像の上で生成するので、目・口・眉を自由に組み合わせても顔が崩れない。

レイヤー（すべて 600x900・同じ座標系・下揃え。tools/import_misaki.py の bust_*.png と同じ規約）:
  base_back.png         基準バスト全体（後ろ髪・体・顔）
  eyes_<kind>.png       目の領域（既定の open は透明＝基準のまま）
  mouth_<kind>.png      口の領域
  blush.png             頬の斜線（手続き描画）
  base_front.png        眼鏡フレーム（基準から抽出。目の差分が眼鏡を描き替えても上から戻す）
  brows_<kind>.png      眉の領域（前髪の上に重なる）
kind の一覧は tools/svg/chars.py（EYE_KINDS / MOUTH_KINDS / BROW_KINDS）と同一。

ラスター化（減色・ordered dither）は全レイヤー共通パレット・共通 Bayer 格子で行い、
各レイヤーは「その差分を合成した完成画像」をラスター化したものから、基準と異なる画素だけを残す。
したがって base_back + 任意のレイヤーの重ねは、ComfyUI の合成結果のラスター化と画素単位で一致する。

usage:
  export COMFY_DIR=/path/to/ComfyUI
  $COMFY_DIR/venv/bin/python -m tools.comfy_gen prep
  $COMFY_DIR/venv/bin/python -m tools.misaki_parts gen        # 基準 + 差分を生成（output/parts/）
  $COMFY_DIR/venv/bin/python -m tools.misaki_parts build      # レイヤー化 → hoshimizaka/game/images/chars/misaki/
  $COMFY_DIR/venv/bin/python -m tools.misaki_parts sheet      # 全プリセットの確認シート（output/parts/sheet.png）
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from tools import comfy_gen as G
from tools import misaki_postprocess as PP
from tools.svg.chars import BROW_KINDS, EYE_KINDS, MOUTH_KINDS

ROOT = G.ROOT
WORK = os.path.join(ROOT, "output", "parts")
GAME_DIR = os.path.join(ROOT, "hoshimizaka", "game", "images", "chars", "misaki")
WH = G.BUST_WH  # 896x1152（基準バストの生成解像度）
SEED = 5

# ── 基準バスト（896x1152）上の部位座標。seed 5 の基準画像で目視計測 ──
LENS_L = (290, 553, 75, 58)   # 眼鏡レンズ (cx, cy, rx, ry)
LENS_R = (515, 515, 87, 65)
BRIDGE = (355, 495, 455, 530)
REGIONS = {  # 楕円 (l, t, r, b), feather
    "brows": ((180, 335, 660, 458), 8),   # 下端は右目の上まつ毛（y≈460）より上
    "eyes":  ((165, 445, 660, 610), 10),
    "mouth": ((330, 612, 500, 705), 8),
}
# まつ毛・目尻とフレームが重なる所（フレーム抽出から除外し、目の差分側に任せる）
LASH_ZONES = [(190, 465, 268, 605), (262, 478, 335, 516), (450, 435, 645, 492), (592, 435, 650, 575)]
CHEEKS = [(205, 590, 290, 640), (560, 575, 645, 625)]  # 頬染めの楕円

# ── キャラ別設定（--char で切り替え。既定は misaki）────────────────────
# 冬華は参考画像がないので、txt2img + 弱い IP-Adapter（美咲の画風・制服）で作った基準バストから始める。
TOUKA_STYLE = ("retro artstyle, 1990s (style), official art, game cg, cel shading, soft shading, "
               "thin dark lineart, delicate lineart, soft colors")
TOUKA_CHAR = ("1girl, solo, (very long hair:1.3), straight hair, (blue hair:1.5), (royal blue hair:1.3), "
              "(indigo blue hair:1.1), hime cut, blunt bangs, sidelocks, white hairband, (blue eyes:1.2), "
              "large eyes, calm, serious, cool, tsurime, serafuku, white shirt, short sleeves, "
              "(navy blue sailor collar:1.3), white stripes, red bowtie")
TOUKA_FRAME = ("upper body, portrait, straight-on, front-facing, looking at viewer, symmetrical, "
               "white background, simple background")
TOUKA_NEG = ("lowres, bad anatomy, bad hands, text, error, cropped, worst quality, low quality, jpeg artifacts, "
             "signature, watermark, blurry, 3d, photorealistic, chromatic aberration, glasses, eyewear, "
             "black hair, dark hair, cyan hair, light blue hair, purple hair, lavender hair, violet hair, "
             "pink hair, blonde hair, short hair, twintails, ponytail, high contrast, heavy shadow, thick outlines, "
             "light blue collar, multiple girls, speech bubble, nsfw, sparkle eyes, star pupils")

CONFIGS = {
    "misaki": {},
    "touka": dict(
        work="parts_touka", game="touka",
        base_src="output/touka/base.png",          # 基準バスト（tools/misaki_parts の docs 参照）
        lens=None, pale_fringe=False,
        positive=lambda tags: ", ".join([G.QUALITY, TOUKA_STYLE, TOUKA_CHAR, TOUKA_FRAME, tags]),
        negative=TOUKA_NEG, cheek_rgb=(236, 120, 140),
        regions={"brows": ((310, 262, 592, 312), 6), "eyes": ((305, 298, 600, 398), 10),
                 "mouth": ((408, 412, 502, 472), 8)},
        cheeks=[(325, 385, 400, 418), (505, 385, 580, 415)],
        lash_zones=[], sheet_crop=(60, 100, 540, 460),
        # 冬華は前髪が眉に被るので、眉は弱め・目の pout は上まぶたを落とし過ぎない（帯状の破綻を防ぐ）
        tags={("eyes", "pout"): "(jitome:1.2), (glaring:1.2), annoyed, sharp eyes",
              ("brows", "up"): "(raised eyebrows:1.2), surprised"},
        denoise={("brows", "up"): 0.75, ("eyes", "pout"): 0.75},
    ),
}
CHAR_NAME = "misaki"
POSITIVE = None      # tags → Positive 全文（None なら comfy_gen の美咲用ブロック）
NEGATIVE = None
BASE_SRC = None      # 設定時はこの画像を基準として使い、ComfyUI で基準を作らない
PALE_FRINGE = True   # 参考シートの印刷オフセット（薄青いフチ）を白扱いにする（美咲のみ）
CHEEK_RGB = (236, 110, 130)
SHEET_CROP = (60, 260, 540, 620)   # 確認シートで切り出す顔まわり（600x900 キャンバス上）


def use(char):
    """キャラ設定をモジュール定数へ反映する。"""
    global WORK, GAME_DIR, CHAR_NAME, POSITIVE, NEGATIVE, BASE_SRC, PALE_FRINGE, CHEEK_RGB
    global LENS_L, LENS_R, REGIONS, CHEEKS, LASH_ZONES, SHEET_CROP
    c = CONFIGS[char]
    CHAR_NAME = char
    if not c:
        return
    WORK = os.path.join(ROOT, "output", c["work"])
    GAME_DIR = os.path.join(ROOT, "hoshimizaka", "game", "images", "chars", c["game"])
    BASE_SRC = os.path.join(ROOT, c["base_src"])
    POSITIVE, NEGATIVE, PALE_FRINGE, CHEEK_RGB = c["positive"], c["negative"], c["pale_fringe"], c["cheek_rgb"]
    if c["lens"] is None:
        LENS_L = LENS_R = None
    REGIONS, CHEEKS, LASH_ZONES, SHEET_CROP = c["regions"], c["cheeks"], c["lash_zones"], c["sheet_crop"]
    for (part, kind), t in c.get("tags", {}).items():
        TAGS[part][kind] = t
    for (part, kind), d in c.get("denoise", {}).items():
        DENOISE_KIND[(part, kind)] = d


# 各差分の inpaint 用タグ（表情タグのみ。キャラ・画風は comfy_gen と共通）
TAGS = {
    "eyes": {
        "open": None,  # 基準のまま
        "happy": "(closed eyes:1.5), (^_^:1.4), (both eyes closed:1.3), happy, smile",
        "surprise": "(wide-eyed:1.4), (surprised:1.3), small pupils",
        "pout": "(half-closed eyes:1.3), (glaring:1.3), annoyed, jitome",
        "closed": "(closed eyes:1.5), sleeping, calm",
    },
    "mouth": {
        "neutral": None,
        "smile": "(smile:1.3), closed mouth",
        "happy": "(open mouth:1.3), (:d:1.3), smile, happy",
        "surprise": "(open mouth:1.3), (:o:1.4), surprised",
        "pout": "(pout:1.4), closed mouth, annoyed",
        "cool": "closed mouth, (serious:1.2), expressionless",
    },
    "brows": {
        "normal": None,
        "cool": "(serious:1.3), expressionless, straight eyebrows",
        "up": "(raised eyebrows:1.5), surprised",
        "angry": "(v-shaped eyebrows:1.5), (angry:1.3)",
        "sad": "(worried eyebrows:1.5), (sad:1.3), furrowed brow",
    },
}
# 部位別に Negative へ足すタグ（片目だけ閉じるウインクを防ぐ）
NEG_EXTRA = {"eyes": "(wink:1.4), (one eye closed:1.4)"}
DENOISE = {"eyes": 0.85, "mouth": 0.85, "brows": 0.9}
DENOISE_KIND = {}   # (部位, 種類) ごとの上書き
KINDS = {"eyes": EYE_KINDS, "mouth": MOUTH_KINDS, "brows": BROW_KINDS}

# 表情プリセット（hoshimizaka/game/characters.rpy の _BASE と同じ）。確認シート用
PRESETS = {
    "normal": ("open", "neutral", "normal", False), "smile": ("open", "smile", "normal", False),
    "happy": ("happy", "happy", "normal", True), "surprise": ("surprise", "surprise", "up", False),
    "pout": ("pout", "pout", "angry", True), "blush": ("open", "smile", "normal", True),
    "cool": ("open", "cool", "cool", False), "sad": ("open", "neutral", "sad", False),
    "angry": ("open", "pout", "angry", False), "closed": ("closed", "smile", "normal", False),
}


def ellipse_mask(box, feather):
    m = Image.new("L", WH, 0)
    ImageDraw.Draw(m).ellipse(box, fill=255)
    return m.filter(ImageFilter.GaussianBlur(feather)) if feather else m


def glasses_mask(base):
    """基準画像から眼鏡フレームの画素を抜き出す（レンズ楕円の輪帯 + ブリッジ内の暗い画素）。"""
    if LENS_L is None:  # 眼鏡なし（冬華）
        return Image.new("L", WH, 0)
    band = Image.new("L", WH, 0)
    d = ImageDraw.Draw(band)
    for cx, cy, rx, ry in (LENS_L, LENS_R):
        d.ellipse((cx - rx - 12, cy - ry - 12, cx + rx + 12, cy + ry + 12), fill=255)
        d.ellipse((cx - rx + 9, cy - ry + 9, cx + rx - 9, cy + ry - 9), fill=0)
    d.rectangle(BRIDGE, fill=255)
    for z in LASH_ZONES:
        d.rectangle(z, fill=0)
    rgb = np.asarray(base.convert("RGB")).astype(int)
    dark = (rgb.sum(axis=2) < 420)
    m = (np.asarray(band) > 0) & dark
    m = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3))
    return m


def masks(base):
    """部位マスク。目は眼鏡フレームを除外（フレームは基準のまま残す）。"""
    g = np.asarray(glasses_mask(base)).astype(float) / 255
    out = {}
    for part, (box, f) in REGIONS.items():
        m = np.asarray(ellipse_mask(box, f)).astype(float) / 255
        if part == "eyes":
            m = m * (1 - g)
        out[part] = Image.fromarray((m * 255).astype(np.uint8))
    return out


def _args(**kw):
    p = argparse.ArgumentParser()
    G.add_gen_args(p)
    a = p.parse_args([])
    a.cmd = "gen"
    for k, v in kw.items():
        setattr(a, k, v)
    return a


def gen(only=None, kinds=None):
    os.makedirs(WORK, exist_ok=True)
    base_path = os.path.join(WORK, "expr", f"base_s{SEED}.png")
    if BASE_SRC:
        os.makedirs(os.path.dirname(base_path), exist_ok=True)
        Image.open(BASE_SRC).convert("RGB").save(base_path)
    elif not (only and os.path.exists(base_path)):
        G.run(_args(preset="expr", denoise=0.0, name="base", seed=SEED, out=os.path.relpath(WORK, ROOT)))
    base = Image.open(base_path)
    inp = os.path.join(G.COMFY, "input")
    base.save(os.path.join(inp, f"ms_{CHAR_NAME}_parts_base.png"))
    for part, m in masks(base).items():
        m.save(os.path.join(inp, f"ms_{CHAR_NAME}_mask_{part}.png"))
        m.save(os.path.join(WORK, f"mask_{part}.png"))
    for part, table in TAGS.items():
        if only and part not in only:
            continue
        for kind, tags in table.items():
            if tags is None or (kinds and f"{part}_{kind}" not in kinds):
                continue
            # 基準画像を初期画像に、清書パスなしで該当部位だけ inpaint
            extra = ", " + NEG_EXTRA[part] if part in NEG_EXTRA else ""
            kw = dict(positive=POSITIVE(tags), ip_weight=0.0) if POSITIVE else {}
            G.run(_args(preset="expr", init=f"ms_{CHAR_NAME}_parts_base.png", mask=f"ms_{CHAR_NAME}_mask_{part}.png",
                        refine=0.0, denoise=DENOISE_KIND.get((part, kind), DENOISE[part]), tags=tags, name=f"{part}_{kind}",
                        negative=(NEGATIVE or G.NEG) + extra,
                        seed=SEED, out=os.path.relpath(WORK, ROOT), **kw))


# ── レイヤー化 ────────────────────────────────────────────────
def _gen_path(name):
    return os.path.join(WORK, "expr", f"{name}_s{SEED}.png")


class Raster:
    """全レイヤー共通の縮小・パレット・ディザ。画面解像度（300x450 相当）で処理して 2 倍 Nearest。"""

    def __init__(self, base, colors=64):
        # 参考画像の印刷オフセット由来の薄青いフチは白とみなして透過する（髪の外周に残るため）
        rgb = np.asarray(base.convert("RGB")).copy()
        ci = rgb.astype(int)
        mx, mn = ci.max(axis=2), ci.min(axis=2)
        if PALE_FRINGE:
            pale = (mn >= 150) & (ci[..., 2] >= ci[..., 0] + 12) & (mx - mn < 100)
            rgb[pale] = 255
        self.alpha_full = PP.remove_white_bg(Image.fromarray(rgb), side_limit=0.62,
                                             bottom=False).getchannel("A")
        self.bbox = self.alpha_full.getbbox()
        bw, bh = self.bbox[2] - self.bbox[0], self.bbox[3] - self.bbox[1]
        self.size = (round(bw * PP.TARGET_H["bust"] / bh), PP.TARGET_H["bust"])
        small = self._small(base)
        self.palette = small.quantize(colors=colors, method=Image.Quantize.MEDIANCUT,
                                      dither=Image.Dither.NONE)
        self.colors = colors
        self.alpha = np.asarray(self._small_l(self.alpha_full)) >= 128

    def _small(self, im):
        return im.convert("RGB").crop(self.bbox).resize(self.size, Image.LANCZOS)

    def _small_l(self, m):
        return m.crop(self.bbox).resize(self.size, Image.LANCZOS)

    def rgb(self, im):
        arr = np.asarray(self._small(im)).astype(np.float32)
        h, w, _ = arr.shape
        t = np.tile(PP.BAYER4, (h // 4 + 1, w // 4 + 1))[:h, :w, None]
        arr = np.clip(arr + t * (255.0 / self.colors ** (1 / 3)), 0, 255).astype(np.uint8)
        return np.asarray(Image.fromarray(arr).quantize(palette=self.palette,
                                                        dither=Image.Dither.NONE).convert("RGB"))

    def place(self, rgb, alpha):
        """画面解像度の RGB + 2 値 alpha → 600x900 キャンバス（2 倍 Nearest・下揃え）。"""
        im = Image.fromarray(np.dstack([rgb, np.where(alpha, 255, 0).astype(np.uint8)]), "RGBA")
        im = im.resize((im.width * 2, im.height * 2), Image.NEAREST)
        c = Image.new("RGBA", (600, 900), (0, 0, 0, 0))
        c.alpha_composite(im, ((600 - im.width) // 2, 900 - im.height))
        return c


def blush_layer(R):
    """頬の斜線（90 年代のセル画風）。半透明の赤み + 濃い斜線 3 本。"""
    over = Image.new("RGBA", WH, (0, 0, 0, 0))
    d = ImageDraw.Draw(over)
    for l, t, r, b in CHEEKS:
        d.ellipse((l, t, r, b), fill=(*CHEEK_RGB, 110))
    over = over.filter(ImageFilter.GaussianBlur(6))
    d = ImageDraw.Draw(over)
    for l, t, r, b in CHEEKS:
        w = r - l
        for i in range(3):
            x = l + w * (0.25 + 0.22 * i)
            d.line((x + 10, t + 10, x - 6, b - 10), fill=(205, 60, 90, 230), width=4)
    return over


def build(dest=GAME_DIR, colors=64):
    base = Image.open(_gen_path("base"))
    R = Raster(base, colors)
    base_rgb = R.rgb(base)
    os.makedirs(dest, exist_ok=True)
    layers = {"base_back": R.place(base_rgb, R.alpha)}
    region_small = {p: np.asarray(R._small_l(Image.open(os.path.join(WORK, f"mask_{p}.png")))) > 8
                    for p in REGIONS}

    for part, kinds in KINDS.items():
        for kind in kinds:
            src = _gen_path(f"{part}_{kind}")
            if TAGS[part].get(kind) is None or not os.path.exists(src):
                if TAGS[part].get(kind) is not None:
                    print("missing", src, "→ 基準で代用", file=sys.stderr)
                # 既定（open/neutral/normal）は透明。下の base_back がそのまま見える。
                # 基準画素で埋めると、上に重なる眉レイヤーが閉じ目の上に開いた目を描き戻してしまう
                layers[f"{part}_{kind}"] = R.place(base_rgb, np.zeros_like(R.alpha))
                continue
            rgb = R.rgb(Image.open(src))
            diff = (rgb != base_rgb).any(axis=2) & region_small[part] & R.alpha
            layers[f"{part}_{kind}"] = R.place(rgb, diff)

    # 頬染め: 基準 + 斜線をラスター化し、変化した画素だけ
    blushed = base.convert("RGBA")
    blushed.alpha_composite(blush_layer(R))
    rgb = R.rgb(blushed)
    layers["blush"] = R.place(rgb, (rgb != base_rgb).any(axis=2) & R.alpha)

    # 前側: 眼鏡フレーム（基準画素）。目の差分がフレームを描き替えても上から戻す
    g = np.asarray(R._small_l(glasses_mask(base))) >= 96
    layers["base_front"] = R.place(base_rgb, g & R.alpha)

    for name, im in layers.items():
        im.save(os.path.join(dest, f"{name}.png"), optimize=True)
    print("wrote", len(layers), "layers →", dest)


def compose(dest, eyes, mouth, brows, blush):
    order = ["base_back", f"eyes_{eyes}", f"mouth_{mouth}"] + (["blush"] if blush else []) + \
            ["base_front", f"brows_{brows}"]
    out = Image.new("RGBA", (600, 900), (0, 0, 0, 0))
    for n in order:
        out.alpha_composite(Image.open(os.path.join(dest, f"{n}.png")))
    return out


def sheet(dest=GAME_DIR):
    """全プリセットを重ね合わせた確認シート（顔まわりを等倍で切り出し）。"""
    tiles = []
    for name, (e, m, b, bl) in PRESETS.items():
        im = compose(dest, e, m, b, bl)
        bbox = im.getbbox()
        crop = im.crop(SHEET_CROP)  # 顔まわり
        bg = Image.new("RGBA", crop.size, (180, 200, 220, 255))
        bg.alpha_composite(crop)
        d = ImageDraw.Draw(bg)
        d.rectangle((0, 0, 110, 22), fill=(0, 0, 0, 255))
        d.text((6, 5), name, fill=(255, 255, 255, 255))
        tiles.append(bg.convert("RGB"))
    w, h = tiles[0].size
    s = Image.new("RGB", (w * 5, h * 2), "gray")
    for i, t in enumerate(tiles):
        s.paste(t, ((i % 5) * w, (i // 5) * h))
    os.makedirs(WORK, exist_ok=True)
    path = os.path.join(WORK, "sheet.png")
    s.save(path)
    print("wrote", path)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("cmd", choices=["gen", "build", "sheet", "masks"])
    p.add_argument("--char", choices=list(CONFIGS), default="misaki")
    p.add_argument("--dest", default=None, help="既定: そのキャラの images/chars/<char>/")
    p.add_argument("--colors", type=int, default=64)
    p.add_argument("--only", default=None, help="gen: 生成する部位（例: brows,eyes）")
    p.add_argument("--kinds", default=None, help="gen: 生成する差分（例: eyes_pout,brows_up）")
    a = p.parse_args()
    use(a.char)
    a.dest = a.dest or GAME_DIR
    if a.cmd == "gen":
        gen(a.only.split(",") if a.only else None, a.kinds.split(",") if a.kinds else None)
    elif a.cmd == "masks":  # マスク位置の確認用
        base = Image.open(_gen_path("base")).convert("RGB")
        over = base.copy()
        tint = {"brows": (0, 200, 0), "eyes": (0, 80, 255), "mouth": (255, 0, 0)}
        for part, m in masks(base).items():
            over = Image.composite(Image.new("RGB", WH, tint[part]), over, m.point(lambda v: v // 2))
        over = Image.composite(Image.new("RGB", WH, (255, 255, 0)), over, glasses_mask(base))
        os.makedirs(WORK, exist_ok=True)
        over.save(os.path.join(WORK, "masks.png"))
        print("wrote", os.path.join(WORK, "masks.png"))
    elif a.cmd == "build":
        build(a.dest, a.colors)
    else:
        sheet(a.dest)


if __name__ == "__main__":
    main()
