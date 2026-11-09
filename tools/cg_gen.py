"""予告END イベントCG を ComfyUI で作る（Issue #85）。構図の根拠は issue 本文、脚本は endings.rpy。

一度は txt2img で「夜景＋人物」をまとめて描かせたが（seed 5..9、コードは git 履歴）、
夜景タグが人物タグに負けて昼空になった / 2人CGは髪色交換とシルエット破綻が出た。
そこで **2段階制作**（issue のフォールバック計画どおり）:

1. 場面: bg_gen で採用済みの ComfyUI 背景（night s8 / rooftop_night s9 / slope_night s8）を
   シーンとして使う。ゲーム本編の背景と完全に一致し、夜景の説得力も実証済み。
2. 人物: 場面の上に IP-Adapter 参照つきの inpaint でキャラを置く（表情差分で作った配線、
   comfy_gen preset "expr" を init/mask/positive を差し替えて使用）。
   人物だけ描き足す。normal_end は 2人を別のマスクで順に（横向き・頭肩。髪色の取り違えと顔破綻防止）。

生成後は bg_gen と同じラスター化: 640x480 で 96 色 ordered dither → Nearest 2 倍 → 1280x960、
hoshimizaka/game/images/cg/ へ置く（images.rpy の宣言は変更不要）。
流れ星・花びらは CG に焼き込まない（endings.rpy で shoot_fx を重ねる。OP の no meteors と同じ）。

  export COMFY_DIR=/path/to/ComfyUI
  PY=$COMFY_DIR/venv/bin/python
  $PY -m tools.cg_gen prep_refs        # 冬華の head 正方形（IP-Adapter 参照）を input へ
  $PY -m tools.cg_gen stage misaki_end --seed 5   # 1 本鎖（場面→人物 inpaint）→ output/cg/expr/<id>_s<seed>.png
  $PY -m tools.cg_gen stages all      # 全 CG x SEEDS
  $PY -m tools.cg_gen sheet           # seed 比較シート output/cg/sheet.png
  $PY -m tools.cg_gen raster <id>    # 採用 seed（CHOSEN）を 640x480 96色 dither → 1280x960
  $PY -m tools.cg_gen install all    # hoshimizaka/game/images/cg/ へ配置
"""
import argparse
import glob
import os
import re

from PIL import Image

from tools import comfy_gen as G
from tools.misaki_parts import TOUKA_CHAR, TOUKA_NEG

ROOT = G.ROOT
CG_DIR = os.path.join(ROOT, "hoshimizaka", "game", "images", "cg")
GEN_DIR = os.path.join(ROOT, "output", "cg", "expr")         # G.run の保存先（out=output/cg + preset expr）
RASTER_DIR = os.path.join(ROOT, "output", "cg", "raster")
SCENE_DIR = os.path.join(ROOT, "output", "cg", "scenes")    # シーンソースの自前コピー
GEN_WH = (1152, 864)                                        # シーン（bg_gen の生成解像度）と同じ
SCREEN = (640, 480)
SEEDS = [5, 6, 7]

TK_HEAD_SQ = "tk_head_sq.png"

QUALITY = G.QUALITY
STYLE = ("retro artstyle, 1990s (style), official art, game cg, cel shading, clean lineart, flat color, "
         "hand-painted anime background art, watercolor texture, halftone dither, muted colors, "
         "deep blue night palette, deep shadows, quiet")
# 背景 NEG と違い人物を描く。昼・天気・服違い・fx 側にあるものなど
NEG = ("lowres, bad anatomy, bad hands, text, error, missing fingers, extra digits, fewer digits, "
       "cropped, worst quality, low quality, jpeg artifacts, signature, watermark, username, "
       "blurry, artist name, chromatic aberration, 3d, photorealistic, modern anime, glossy, cgi, "
       "speech bubble, ui, letterboxed, black bars, scanlines, oversaturated, pastel, washed out, faded, "
       "(shooting star:1.4), (meteor:1.4), comet, falling star, constellation chart, "
       "cherry blossom petals, petals, snow, rain, umbrella, nightdress, pajama, swimsuit, "
       "day, daytime, (blue sky:1.5), clouds, sunny, sunlight, bright sky, daylight, flat lighting")

# 人物 inpaint で夜景トーンに溶かすための共通ライティング（マスク内は照明指定がないと昼の塗りになる）
NIGHT_LIT = ("(night:1.4), (dark blue lighting:1.4), (moonlight:1.2), rim light, dark blue shading, "
             "shadows, cinematic night scene")

# 各 CG: シーンは bg_gen の採用素材（bg 名と seed）→ 人物 inpaint 本鎖。
# steps の box は楕円マスク（1152x864。キャンバス枠外へはみ出して下辺シームを消す）。
# pos は [キャラブロック, ポーズ, 周辺描写] を ", ".join して使う。
SCG = {
    "misaki_end": dict(
        scene=("night", 8),
        steps=[dict(
            part="misaki", box=(560, 170, 1160, 900), feather=28, ip=0.6, ref=G.IN_HEAD_SQ,
            pos=[G.CHAR,
                 "(upper body:1.3), (turning around:1.4), (looking back at viewer:1.5), (from side:1.2), "
                 "(smiling:1.4), (blush:1.3), happy, (hair blowing in the wind:1.3), character on the right side",
                 "night sky with stars behind her, distant town lights in the lower background, "
                 "(red bowtie:1.3)"],
            neg=("blue hair, purple hair, blonde hair, white hair, orange hair, long hair, twintails, "
                 "no eyewear, sunglasses, red-framed eyewear, thick eyewear, green bowtie, "
                 "multiple girls, 2girls, 3girls, fence, railing, new scenery, new background"))]),
    "touka_end": dict(
        # 望遠鏡は背景側で描けなかったのでこのマスクに込みで描かせる（rooftop_night にも描画実績なし）
        scene=("rooftop_night", 9),
        steps=[dict(
            part="touka", box=(60, 150, 760, 900), feather=28, ip=0.6, ref=TK_HEAD_SQ,
            pos=[TOUKA_CHAR,
                 "(upper body:1.3), standing, (gentle smile:1.4), (blush:1.3), (looking at viewer:1.2), "
                 "character on the left side",
                 "(a refracting astronomical telescope on a tripod beside her:1.3), "
                 "chain-link fence behind her, crescent moon in the dark sky"],
            neg_add=("telescope broken, two telescopes, multiple girls, 2girls, 3girls, indoor, classroom, "
                     "hallway, new scenery, white background, " + TOUKA_NEG))]),
    "normal_end": dict(
        # 2人後ろ姿の inpaint は冬華が「髪だけの塊」になる（very long hair がマスクいっぱいに膨らむ）ため、
        # 「並んで空を見上げる横向き（profile）」に切り替えた。顔は IP-Adapter で一致性を取る
        scene=("slope_night", 8),
        steps=[
            dict(part="misaki", box=(240, 460, 560, 900), feather=16, ip=0.65, ref=G.IN_HEAD_SQ,
                 pos=[G.CHAR + ", (pink hair:1.5), (head and shoulders:1.3), (side profile:1.5), facing right, "
                      "(looking up at the sky:1.4), (happy smile:1.3), (blush:1.2), "
                      "(glasses:1.3), (round glasses:1.5), (temples of glasses:1.3), "
                      "shoulder length bob blowing in the night breeze, (red bowtie:1.3)",
                      "night street with lit windows behind her, warm streetlamp glow from the right"],
                 neg=("blue hair, purple hair, blonde hair, white hair, orange hair, brown hair, "
                      "very long hair, twintails, front view, facing camera, back view, from behind, "
                      "full body, legs, multiple girls, 2girls, new scenery, new background")),
            dict(part="touka", box=(585, 445, 905, 900), feather=16, ip=0.7, ref=TK_HEAD_SQ,
                 pos=[TOUKA_CHAR + ", (blue hair:1.6), (head and shoulders:1.3), (side profile:1.5), facing right, "
                      "(looking up at the sky:1.4), (gentle smile:1.3), (blush:1.2), "
                      "hime cut with cheek hair framing her face, very long straight blue hair down her back, "
                      "(navy blue sailor collar:1.3), white shirt shoulder, same height as the girl on the left",
                      "night street with lit windows behind her, warm streetlamp glow"],
                 neg=("pink hair, brown hair, orange hair, white hair, short hair, bob cut, glasses, "
                      "(hair blob:1.8), (hair only:1.8), (faceless:1.6), no face, headless, "
                      "no uniform, no shoulders, dress, "
                      "front view, facing camera, back view, from behind, full body, legs, "
                      "multiple girls, 2girls, new scenery, new background, " + TOUKA_NEG)),
        ]),
}

# 採用シード（sheet で目視選択後に記録。意図は docs/image-generation.md CG の項）
# normal_end は 5..13 で後ろ姿破綻（冬華が髪の塊）→ 横向き頭肩に作り直した 14..18 から 17
CHOSEN = {"misaki_end": 7, "touka_end": 5, "normal_end": 17}


def _inp(name, st):
    pos = ", ".join([QUALITY, STYLE, NIGHT_LIT] + st["pos"])
    neg = ", ".join(x for x in (NEG, st.get("neg"), st.get("neg_add")) if x)
    return pos, neg


def scene_gen(bgname, seed):
    """シーン専用の txt2img（canny なし・人物なし）。bg_gen と同じ場面タグだが、
    CG に必要な小道具（望遠鏡など）が既定 seed で描けなかった時のバリエーション作り。
    選ばれたら output/cg/scenes/<bgname>_s<seed>.png へコピーして scene= で参照する。"""
    from tools import bg_gen as B
    cfg = B.BG[bgname]
    a = G.make_args(preset="bg", positive=", ".join([B.QUALITY, B.STYLE, cfg["p"]]),
                    negative=B.NEG, ip_weight=0.0, cn_weight=0.0, denoise=1.0,
                    width=GEN_WH[0], height=GEN_WH[1], name=bgname, seed=seed, out="output/cg_scenes")
    return G.run(a)


def scene_src(bg, seed):
    """シーン画像を探す: 自前コピー → bg_gen の生成中間 → インストール済み背景（フォールバック）。"""
    cands = [os.path.join(SCENE_DIR, f"{bg}_s{seed}.png"),
             os.path.join(ROOT, "output", "bg", "bg", f"{bg}_s{seed}.png"),
             os.path.join(ROOT, "hoshimizaka", "game", "images", "bg", f"{bg}.png")]
    p = next((c for c in cands if os.path.exists(c)), None)
    if p is None:
        raise SystemExit(f"シーン素材がない: {bg}_s{seed}（output/cg/scenes/ か output/bg/bg/ に置くか、"
                         "bg_gen を先に実行）")
    if "hoshimizaka" in p:
        print("警告: インストール済み背景（dither 焼き込み）をフォールバック使用:", p)
    return p


def prep_scene(name):
    """シーンを ComfyUI/input へ 1152x864 で置く。"""
    bg, seed = SCG[name]["scene"]
    inp = os.path.join(G.COMFY, "input")
    os.makedirs(inp, exist_ok=True)
    im = Image.open(scene_src(bg, seed)).convert("RGB")
    if im.size != GEN_WH:
        im = im.resize(GEN_WH, Image.LANCZOS)
    im.save(os.path.join(inp, f"cg_{name}_scene.png"))
    return f"cg_{name}_scene.png"


def prep_mask(name, i, st):
    m = G.face_mask(GEN_WH, st["box"], st["feather"])
    p = os.path.join(G.COMFY, "input", f"cg_{name}_m{i}.png")
    m.save(p)
    return f"cg_{name}_m{i}.png"


def stage(name, seed):
    """1 本鎖: 場面 inpaint →（複数人なら次の人物へ）。最終出力のパスを返す。"""
    cur = prep_scene(name)
    steps = SCG[name]["steps"]
    saved = None
    for i, st in enumerate(steps):
        pos, neg = _inp(name, st)
        last = i == len(steps) - 1
        a = G.make_args(preset="expr", init=cur, mask=prep_mask(name, i, st), refine=0.0,
                        denoise=st.get("denoise", 0.95), positive=pos, negative=neg,
                        ip_weight=st["ip"], ip_refs=[st["ref"]],
                        name=f"{name}" if last else f"{name}_p{i}", seed=seed, out="output/cg")
        saved = G.run(a)[0]
        if not last:  # 次段の init に渡す（input へコピー）
            nxt = f"cg_{name}_p{i}.png"
            Image.open(saved).convert("RGB").save(os.path.join(G.COMFY, "input", nxt))
            cur = nxt
    return saved


# ── IP-Adapter 参照画像 ─────────────────────────────────────────
# 冬華の head 正方形。base_src と同じ output/touka/base.png があればそこから、
# git 管理外なので無ければインストール済みレイヤー（64色だが IP-Adapter 用途には十分）から作る。
TK_CROPS = {"base": ((896, 1152), (165, 95, 735, 665)),        # 基準バスト（ComfyUI 生成時）から頭部
            "layer": ((600, 900), (95, 220, 505, 640))}        # レイヤー版（base_back.png）から頭部


def prep_refs(src=None):
    from PIL import ImageDraw
    cands = ([src] if src else []) + [
        os.path.join(ROOT, "output", "touka", "base.png"),
        os.path.join(ROOT, "hoshimizaka", "game", "images", "chars", "touka", "base_back.png")]
    path = next((p for p in cands if os.path.exists(p)), None)
    if path is None:
        raise SystemExit("冬華の基準画像が見つからない: output/touka/base.png か "
                         "hoshimizaka/game/images/chars/touka/base_back.png、または --src で指定")
    im = Image.open(path).convert("RGB")
    kind = "base" if im.size == (896, 1152) else "layer"
    box = TK_CROPS[kind][1]
    sq = G._pad_square(im.crop(box), 448)
    inp = os.path.join(G.COMFY, "input")
    os.makedirs(inp, exist_ok=True)
    out = os.path.join(inp, TK_HEAD_SQ)
    sq.save(out)
    print(f"wrote {out} (from {path}, {kind} crop {box})")
    os.makedirs(os.path.join(ROOT, "output", "cg"), exist_ok=True)
    chk = sq.copy()
    ImageDraw.Draw(chk).rectangle((0, 0, chk.width - 1, chk.height - 1), outline="red")
    chk.save(os.path.join(ROOT, "output", "cg", "prep_refs.png"))
    return out


# ── ラスター化（640x480 で減色 + ordered dither → Nearest 2 倍。bg_gen と同じ）──
def raster(name, seed=None, colors=96):
    from tools import misaki_postprocess as PP
    seed = seed or CHOSEN[name]
    src = os.path.join(GEN_DIR, f"{name}_s{seed}.png")
    im = Image.open(src).convert("RGB").resize(SCREEN, Image.LANCZOS)
    out = PP._quantize(im, colors, "ordered").resize((SCREEN[0] * 2, SCREEN[1] * 2), Image.NEAREST)
    os.makedirs(RASTER_DIR, exist_ok=True)
    path = os.path.join(RASTER_DIR, f"{name}.png")
    out.save(path, optimize=True)
    return path


def install(name):
    path = os.path.join(RASTER_DIR, f"{name}.png")
    assert os.path.exists(path), f"先に raster {name}"
    Image.open(path).save(os.path.join(CG_DIR, f"{name}.png"), optimize=True)
    print("installed", name)


def sheet():
    """CG x seed の比較シート（最終鎖のみ。中間 _p* は除く）。"""
    from PIL import ImageDraw
    W, H = 448, 336
    rows = []
    for name in SCG:
        files = [f for f in glob.glob(os.path.join(GEN_DIR, f"{name}_s*.png"))
                 if not re.search(r"_p\d+_s", os.path.basename(f))]
        files.sort(key=lambda p: int(re.search(r"_s(\d+)\.png", p).group(1)))
        rows.append((name, files))
    cols = max(len(f) for _, f in rows)
    s = Image.new("RGB", (W * cols, H * len(rows)), "gray")
    for r, (name, files) in enumerate(rows):
        for c, f in enumerate(files):
            im = Image.open(f).convert("RGB").resize((W, H))
            seed = re.search(r"_s(\d+)\.png", f).group(1)
            mark = " *CHOSEN" if CHOSEN.get(name) == int(seed) else ""
            ImageDraw.Draw(im).text((6, 6), f"{name} seed {seed}{mark}", fill="yellow")
            s.paste(im, (c * W, r * H))
    path = os.path.join(ROOT, "output", "cg", "sheet.png")
    s.save(path)
    print("wrote", path)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("cmd", choices=["prep_refs", "scene", "stage", "stages", "raster", "install", "sheet"])
    p.add_argument("name", nargs="?", default="all")
    p.add_argument("--seed", type=int, default=5)
    p.add_argument("--seeds", default=None, help="stages/scene: カンマ区切り seed 一覧（stages 既定 5,6,7）")
    p.add_argument("--colors", type=int, default=96)
    p.add_argument("--src", default=None, help="prep_refs: 冬華基準画像の明示指定")
    a = p.parse_args()
    names = list(SCG) if a.name == "all" else [a.name]
    if a.cmd == "prep_refs":
        prep_refs(a.src)
    elif a.cmd == "scene":
        for s0 in [int(x) for x in (a.seeds or str(a.seed)).split(",")]:
            scene_gen(a.name, s0)
    elif a.cmd == "stage":
        for n in names:
            stage(n, a.seed)
    elif a.cmd == "stages":
        for s0 in [int(x) for x in (a.seeds or ",".join(map(str, SEEDS))).split(",")]:
            for n in names:
                stage(n, s0)
    elif a.cmd == "raster":
        for n in names:
            print(raster(n, colors=a.colors))
    elif a.cmd == "install":
        for n in names:
            install(n)
    if a.cmd == "sheet":
        sheet()


if __name__ == "__main__":
    main()
