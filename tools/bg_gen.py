"""本編背景を ComfyUI で作り直す（Issue #67）。仕様と判断の根拠は docs/background-art-spec.md。

既存背景（ベタ塗りのベクター調）の構図（キャラ配置の余白・消失点）を ControlNet canny で固定したまま、
画風だけを 90 年代の手描き背景美術に差し替える。生成後は tools.misaki_postprocess と同じ
「640x480 で減色 + ordered dither → Nearest 2 倍」でラスター化し、1280x960 PNG として書き出す。

  export COMFY_DIR=/path/to/ComfyUI
  PY=$COMFY_DIR/venv/bin/python
  $PY -m tools.bg_gen gen slope              # 1 枚生成 → output/bg/gen/slope_s<seed>.png
  $PY -m tools.bg_gen gen all                # 11 枚（black は対象外）
  $PY -m tools.bg_gen raster slope           # ラスター化 → output/bg/raster/slope.png
  $PY -m tools.bg_gen install slope          # hoshimizaka/game/images/bg/ へ配置（元画像は git 履歴に残る）
  $PY -m tools.bg_gen sheet                  # 一覧シート output/bg/sheet.png

人物・文字・UI は描かせない。桜の花びら・流れ星は fx（images/fx, transforms.rpy）に任せるので描かせない。
"""
import argparse
import os

import numpy as np
from PIL import Image

from tools import comfy_gen as G

ROOT = G.ROOT
BG_DIR = os.path.join(ROOT, "hoshimizaka", "game", "images", "bg")
ORIG_DIR = os.path.join(ROOT, "output", "bg", "orig")      # 構図ガイド（元の背景のコピー）
GEN_DIR = os.path.join(ROOT, "output", "bg", "gen")
RASTER_DIR = os.path.join(ROOT, "output", "bg", "raster")
GEN_WH = (1152, 864)      # SDXL の 1MP 付近で 4:3
SCREEN = (640, 480)
SEED = 7

QUALITY = "masterpiece, best quality, very aesthetic, absurdres"
STYLE = ("scenery, no humans, background, 1990s (style), retro artstyle, game cg, "
         "hand-painted anime background art, natural colors, bright daylight, clear contrast, deep shadows, "
         "simple composition, eye-level view, wide shot, open space in the center, "
         "bishoujo adventure game background, school life game background")
NEG = ("lowres, worst quality, low quality, jpeg artifacts, blurry, "
       "1girl, 1boy, multiple girls, people, human, character, silhouette of person, "
       "text, logo, watermark, signature, speech bubble, ui, window frame border, "
       "photorealistic, 3d, cgi, vector art, smooth gradient, glossy, modern anime, "
       "chromatic aberration, vignette, letterboxed, black bars, scanlines, "
       "falling petals, shooting star, meteor, fantasy, ghibli, oversaturated, pastel, washed out, faded, "
       "busy composition, cluttered, aerial view, bird's eye view, castle, temple, bridge")

# 各背景の個別プロンプト（意図は docs/background-art-spec.md）と生成パラメータ
# denoise: 元画像からの変化量。1.0 に近いほど画風を作り替える。cn: canny の強さ（構図の固定度）
BG = {
    "slope": dict(
        p="ordinary japanese seaside town street, a straight asphalt road sloping down toward the sea at the center, "
          "spring morning, clear blue sky with a few white clouds, cherry blossom trees on both sides, "
          "utility poles with power lines, modern japanese suburban houses with concrete walls, "
          "the blue ocean visible at the end of the road, the road slopes down to the vanishing point",
        denoise=0.9, cn=0.6),
    "slope_sunset": dict(
        p="japanese seaside town, a gently sloping road going down to the sea, sunset, "
          "orange and pink gradient sky, setting sun over the ocean, cherry blossom trees, "
          "utility pole with power lines, houses with warm lit windows, long shadows, evening light",
        denoise=0.9, cn=0.6),
    "slope_night": dict(
        p="japanese seaside town, a gently sloping road going down to the sea, night, "
          "starry sky, crescent moon, cherry blossom trees in the dark, "
          "street lamp glowing, utility pole with power lines, houses with yellow lit windows, deep blue night",
        denoise=0.9, cn=0.6),
    "rooftop": dict(
        p="school rooftop, chain-link fence, water tank, sunset, orange and purple sky, "
          "silhouette of the town and the sea in the distance, concrete floor, evening light",
        denoise=0.9, cn=0.6),
    "rooftop_night": dict(
        p="school rooftop at night, chain-link fence, water tank, starry sky, crescent moon, "
          "a refracting astronomical telescope on a tripod in the foreground, town lights far below, deep blue night",
        denoise=0.9, cn=0.6),
    "night": dict(
        p="night sky full of stars, milky way, dark hill silhouette against the sky, "
          "small town lights twinkling below the hill, deep blue to black gradient sky, quiet and wide open",
        denoise=0.95, cn=0.5),
    "classroom": dict(
        p="japanese high school classroom, daytime, large window with blue sky and pink cherry blossoms outside, "
          "green blackboard with chalk marks, wall clock, wooden student desks, wooden floor, warm sunlight",
        denoise=0.9, cn=0.6),
    "classroom_evening": dict(
        p="japanese high school classroom, after school, sunset, orange light pouring through the window, "
          "green blackboard with chalk marks, wall clock, wooden student desks, wooden floor, long soft shadows",
        denoise=0.9, cn=0.6),
    "hallway": dict(
        p="japanese high school hallway, daytime, row of windows on one side, grey shoe lockers, "
          "wooden floor, ceiling fluorescent light, perspective view, bright",
        denoise=0.9, cn=0.6),
    "clubroom": dict(
        p="school astronomy club room, big star chart on the wall, wooden table, window with warm light, "
          "books and papers, wooden floor, cozy, a little messy, evening",
        denoise=0.9, cn=0.6),
    "home": dict(
        p="boy's bedroom at night, bed with blanket, wooden desk with a small lamp, "
          "window showing a starry night sky and the moon, dim blue light, cozy room",
        denoise=0.9, cn=0.6),
}


# 採用シード（seed 7 / 8 の 2 案から、立ち絵を置く余白・時間帯の読みやすさで選んだもの）
CHOSEN = {"slope": 8, "slope_sunset": 7, "slope_night": 8, "rooftop": 8, "rooftop_night": 9,
          "night": 8, "classroom": 8, "classroom_evening": 8, "hallway": 8, "clubroom": 7, "home": 8}


# OP 背景（docs/op-storyboard.md §7）。流星・光・星の瞬きは op.rpy 側のエフェクトなので描かせない。
# 構図ガイドなし。op.rpy が zoom / 移動を掛けるので、画面端まで主題を寄せず余白を残す。
OP = {
    "op_starry_sky": dict(
        p="sky only, starry night sky, dense small stars, faint milky way, smooth deep navy to indigo gradient",
        neg="mountain, hill, ground, horizon, land, trees, buildings, moon, ring, circle, swirl",
        denoise=1.0, cn=0, file="bg_op_starry_sky"),
    "op_title_sky": dict(
        p="sky only, dark starry night sky, sparkling stars, soft purple and blue glow in the center, "
          "smooth gradient, minimal, calm",
        neg="mountain, hill, ground, horizon, land, trees, buildings, ring, circle, swirl, ornament, "
            "decoration, moon, sun, planet, floor, tiles",
        denoise=1.0, cn=0, file="bg_op_title_sky"),
    "op_observatory_night": dict(
        p="a small astronomical observatory building with a white dome roof and white walls, "
          "standing on a grassy hill at night, glowing yellow windows, starry sky, crescent moon, "
          "wooden fence, wide shot, the building is small in the frame, plenty of sky",
        neg="giant, huge, abstract, ring, circle, swirl, ornament, green, crescent shaped building, close-up",
        denoise=1.0, cn=0, file="bg_op_observatory_night"),
    "op_slope_lamp": dict(
        p="ordinary japanese seaside town street, a straight asphalt road sloping down toward the sea at the center, "
          "clear morning sky with bright light at the end of the road, street lamp, cherry blossom trees, "
          "utility poles with power lines, houses on both sides, the road leads to the vanishing point",
        denoise=1.0, cn=0, file="bg_op_slope_lamp"),
    "op_town_twilight": dict(
        p="ordinary japanese seaside town street, a straight asphalt road sloping down toward the sea at the center, "
          "twilight, the sun setting over the ocean, purple and orange sky, first stars appearing, "
          "utility poles with power lines, houses with lit windows, the road leads to the vanishing point",
        denoise=1.0, cn=0, file="bg_op_town_twilight"),
    "op_hill_meteor_shower": dict(
        p="wide shot from a hill looking over a small town at night, vast starry sky filling the upper half, "
          "town lights twinkling in the lower half, dark hill silhouette in the foreground, no meteors",
        denoise=1.0, cn=0, file="bg_op_hill_meteor_shower"),
}
BG.update(OP)
CHOSEN.update({"op_starry_sky": 9, "op_title_sky": 9, "op_observatory_night": 8, "op_slope_lamp": 7,
               "op_town_twilight": 7, "op_hill_meteor_shower": 7})


def dest_path(name):
    """配置先（OP 背景は images/op/、本編背景は images/bg/）。"""
    if name in OP:
        return os.path.join(os.path.dirname(BG_DIR), "op", OP[name]["file"] + ".png")
    return os.path.join(BG_DIR, f"{name}.png")


def _orig(name):
    return os.path.join(ORIG_DIR, f"{name}.png")


def prep(name):
    """元の背景を構図ガイドとして保存し、ComfyUI/input に GEN_WH で置く。"""
    os.makedirs(ORIG_DIR, exist_ok=True)
    keep = _orig(name)
    if not os.path.exists(keep):  # install 後に元画像が上書きされても、ガイドは最初のものを使う
        Image.open(os.path.join(BG_DIR, f"{name}.png")).convert("RGB").save(keep)
    inp = os.path.join(G.COMFY, "input")
    os.makedirs(inp, exist_ok=True)
    Image.open(keep).resize(GEN_WH, Image.LANCZOS).save(os.path.join(inp, f"ms_bg_{name}.png"))
    return f"ms_bg_{name}.png"


def gen(name, seed=SEED, **over):
    cfg = {**BG[name], **over}
    init = prep(name) if name not in OP else None
    a = G.make_args(preset="bg", init=init, positive=", ".join([QUALITY, STYLE, cfg["p"]]),
                negative=NEG + (", " + cfg["neg"] if cfg.get("neg") else ""), ip_weight=0.0, denoise=cfg["denoise"], cn_weight=cfg["cn"],
                cn_end=cfg.get("cn_end", 0.8), cfg=cfg.get("cfg", 6.0), name=name, seed=seed,
                out="output/bg")
    return G.run(a)


# ── ラスター化（640x480 で減色 + ordered dither → Nearest 2 倍）──────────
def raster(name, seed=None, colors=96):
    seed = seed or CHOSEN[name]
    from tools import misaki_postprocess as PP
    src = os.path.join(ROOT, "output", "bg", "bg", f"{name}_s{seed}.png")
    im = Image.open(src).convert("RGB").resize(SCREEN, Image.LANCZOS)
    out = PP._quantize(im, colors, "ordered").resize((SCREEN[0] * 2, SCREEN[1] * 2), Image.NEAREST)
    os.makedirs(RASTER_DIR, exist_ok=True)
    path = os.path.join(RASTER_DIR, f"{name}.png")
    out.save(path, optimize=True)
    return path


def install(name):
    path = os.path.join(RASTER_DIR, f"{name}.png")
    assert os.path.exists(path), f"先に raster {name}"
    if name not in OP:
        prep(name)  # 元画像のコピーを確保してから上書き
    Image.open(path).save(dest_path(name), optimize=True)
    print("installed", name)


def sheet(src="raster"):
    names = [n for n in BG if os.path.exists(os.path.join(ROOT, "output", "bg", src, f"{n}.png"))]
    W, H = 480, 360
    s = Image.new("RGB", (W * 4, H * ((len(names) + 3) // 4)))
    from PIL import ImageDraw
    for i, n in enumerate(names):
        im = Image.open(os.path.join(ROOT, "output", "bg", src, f"{n}.png")).convert("RGB").resize((W, H))
        ImageDraw.Draw(im).text((6, 6), n, fill="red")
        s.paste(im, ((i % 4) * W, (i // 4) * H))
    path = os.path.join(ROOT, "output", "bg", "sheet.png")
    s.save(path)
    print("wrote", path)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("cmd", choices=["gen", "raster", "install", "sheet"])
    p.add_argument("name", nargs="?", default="all")
    p.add_argument("--seed", type=int, default=None, help="gen: 既定 7 / raster: 採用シード")
    p.add_argument("--denoise", type=float, default=None)
    p.add_argument("--cn", type=float, default=None)
    p.add_argument("--colors", type=int, default=96)
    a = p.parse_args()
    names = list(BG) if a.name == "all" else [a.name]
    over = {k: v for k, v in (("denoise", a.denoise), ("cn", a.cn)) if v is not None}
    for n in names:
        if a.cmd == "gen":
            gen(n, a.seed or SEED, **over)
        elif a.cmd == "raster":
            print(raster(n, a.seed, a.colors))
        elif a.cmd == "install":
            install(n)
    if a.cmd == "sheet":
        sheet()


if __name__ == "__main__":
    main()
