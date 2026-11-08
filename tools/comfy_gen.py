"""美咲のキャラクター素材を ComfyUI API 経由で生成する（Issue #65）。

参考画像（docs/images/character-misaki.webp）に「似せる」ことを最優先にした構成:

- stand : 参考シートの全身 figure を初期画像にした img2img
          + ControlNet Union(canny) で線画を固定 + IP-Adapter（正方形パッドした頭部/全身）で外見を参照
- expr  : バスト画像（既定は参考シート「通常」パネル）を
          ① 全体を低 denoise + canny で清書 → ② 顔だけマスクして表情差分を inpaint
          髪・眼鏡・制服はマスク外なので変わらない
- pose  : OpenPose で別ポーズ + IP-Adapter（同一性は stand/expr より落ちる。LoRA 導入までの暫定）

ComfyUI 本体とモデルはリポジトリ外に置ける（COMFY_DIR で指定。既定はリポジトリ直下 ComfyUI/）。
手順・モデル・設定値の記録は docs/image-generation.md を参照。

  export COMFY_DIR=/path/to/ComfyUI        # main.py があるディレクトリ
  $COMFY_DIR/venv/bin/python -m tools.comfy_gen prep
  $COMFY_DIR/venv/bin/python -m tools.comfy_gen gen --preset stand --seed 5
  $COMFY_DIR/venv/bin/python -m tools.comfy_gen gen --preset expr --expression smile --seed 5
  $COMFY_DIR/venv/bin/python -m tools.comfy_gen all --seed 5     # 立ち絵1 + 表情6 をまとめて

生成物は --out（既定 output/comfy/<preset>/）に PNG と実行パラメータ JSON（ワークフロー全体）を保存する。
ドット感・減色・ディザ・透過は後処理 tools/misaki_postprocess.py で付与する。
"""
import argparse
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMFY = os.environ.get("COMFY_DIR", os.path.join(ROOT, "ComfyUI"))
SERVER = os.environ.get("COMFY_SERVER", "http://127.0.0.1:8188")
SRC = os.path.join(ROOT, "docs", "images", "character-misaki.webp")

CHECKPOINT = "animagine-xl-3.1.safetensors"
IPADAPTER_PRESET = "PLUS (high strength)"     # ip-adapter-plus_sdxl_vit-h + CLIP-ViT-H
CONTROLNET = "controlnet-union-sdxl-1.0-promax.safetensors"

# ComfyUI/input に置く参照画像（他の作業と衝突しないよう ms_ 接頭辞）
IN_STAND = "ms_stand_init.png"    # 全身 figure を 832x1216 白キャンバスに配置（img2img + canny 元）
IN_BUST = "ms_bust_init.png"      # 「通常」バストを 896x1152 に拡大（expr の初期画像）
IN_BUST_MASK = "ms_bust_mask.png"  # 上記の顔（眉・目・口）マスク
IN_HEAD_SQ = "ms_head_sq.png"     # 頭部を正方形パッド（IP-Adapter。CLIP は 224 正方形に center crop するため）
IN_FIG_SQ = "ms_fig_sq.png"       # 全身を正方形パッド（IP-Adapter）

STAND_WH = (832, 1216)   # SDXL の ~1MP バケット。最終的に 640x480 画面へ縮小する
BUST_WH = (896, 1152)
PANEL_FIGURE = (0, 0, 392, 1295)      # 参考シートの全身 figure
PANEL_BUST = (396, 6, 668, 352)       # 参考シートの「通常」バスト（tools/import_misaki.py と同じ箱）
FIG_HEAD = (60, 10, 340, 330)         # figure 内の頭部
BUST_FACE = (52, 92, 208, 232)        # バストパネル内の顔（眉〜あご）

# ── プロンプト（Animagine XL 3.1 の Danbooru タグ語彙）──────────────────
# Pony 系の score_X タグは Animagine では無意味なので使わない。
QUALITY = "masterpiece, best quality, very aesthetic"
STYLE = ("retro artstyle, 1990s (style), official art, game cg, "
         "cel shading, clean lineart, flat color")
CHAR = ("1girl, solo, misaki, pink hair, short hair, bob cut, swept bangs, "
        "brown eyes, round eyewear, glasses, (thin-framed eyewear:1.3), (black-framed eyewear:1.2), "
        "serafuku, white shirt, short sleeves, blue sailor collar, white stripes, "
        "red bowtie, blue pleated skirt")
FRAMING_STAND = ("full body, standing, arms behind back, looking at viewer, "
                 "white socks, brown loafers, white background, simple background")
FRAMING_BUST = "upper body, portrait, looking at viewer, white background, simple background"
NEG = ("lowres, bad anatomy, bad hands, text, error, missing fingers, extra digits, fewer digits, "
       "cropped, worst quality, low quality, jpeg artifacts, signature, watermark, username, "
       "blurry, artist name, chromatic aberration, 3d, photorealistic, "
       "blue hair, purple hair, blonde hair, white hair, long hair, no eyewear, sunglasses, "
       "red-framed eyewear, thick eyewear, "
       "midriff, crop top, navel, multiple girls, speech bubble, nsfw")

# 表情キーは tools/import_misaki.py / images.rpy と同一
EXPRESSIONS = {
    "normal":   "closed mouth, expressionless, calm",
    "smile":    "(smile:1.3), closed mouth, happy, (closed eyes:0.6), light smile",
    "blush":    "(blush:1.4), (embarrassed:1.2), nose blush, looking away, wavy mouth",
    "surprise": "(surprised:1.3), (open mouth:1.3), wide-eyed, constricted pupils, :o",
    "sad":      "(sad:1.4), (frown:1.2), (tearing up:1.2), downcast eyes, worried eyebrows, closed mouth",
    "angry":    "(angry:1.4), (v-shaped eyebrows:1.4), (glaring:1.2), clenched teeth, annoyed",
}


# ── 参照画像の前処理 ─────────────────────────────────────────────
def _clean_figure(fig):
    """figure パネルの薄青い印刷オフセット影と外周白を純白にする（IP-Adapter が青髪化するのを防ぐ）。"""
    import numpy as np
    from tools.import_misaki import largest_component
    arr = np.asarray(fig).copy()
    rgb = arr.astype(int)
    r, b = rgb[..., 0], rgb[..., 2]
    mx, mn = rgb.max(axis=2), rgb.min(axis=2)
    pale_blue = (mn >= 150) & (b >= r + 18) & (mx - mn < 90)
    keep = largest_component(~(pale_blue | (mn >= 236)))
    arr[~keep] = 255
    return arr


def _pad_square(im, size=None):
    from PIL import Image
    s = max(im.size)
    c = Image.new("RGB", (s, s), (255, 255, 255))
    c.paste(im, ((s - im.width) // 2, (s - im.height) // 2))
    return c.resize((size, size), Image.LANCZOS) if size else c


def _fit(im, wh, margin=0.02):
    """白キャンバス wh の中央に、上下 margin を残して収める。戻り値: (画像, scale, (ox, oy))"""
    from PIL import Image
    w, h = wh
    s = min(w / im.width, h * (1 - 2 * margin) / im.height)
    r = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    c = Image.new("RGB", wh, (255, 255, 255))
    ox, oy = (w - r.width) // 2, (h - r.height) // 2
    c.paste(r, (ox, oy))
    return c, s, (ox, oy)


def face_mask(wh, box, feather=18):
    """box (l,t,r,b) を白にした楕円マスク（ぼかし付き）。"""
    from PIL import Image, ImageDraw, ImageFilter
    m = Image.new("L", wh, 0)
    ImageDraw.Draw(m).ellipse(box, fill=255)
    return m.filter(ImageFilter.GaussianBlur(feather))


def prep():
    import numpy as np
    from PIL import Image
    inp = os.path.join(COMFY, "input")
    os.makedirs(inp, exist_ok=True)
    sheet = Image.open(SRC).convert("RGB")
    fig = Image.fromarray(_clean_figure(sheet.crop(PANEL_FIGURE)))

    stand, _, _ = _fit(fig, STAND_WH)
    stand.save(os.path.join(inp, IN_STAND))
    _pad_square(fig.crop(FIG_HEAD), 448).save(os.path.join(inp, IN_HEAD_SQ))
    _pad_square(fig, 448).save(os.path.join(inp, IN_FIG_SQ))

    bust = sheet.crop(PANEL_BUST)
    bust_arr = np.asarray(bust).copy()
    bust_arr[np.asarray(bust).min(axis=2) >= 236] = 255
    bust_img, s, (ox, oy) = _fit(Image.fromarray(bust_arr), BUST_WH, margin=0.0)
    bust_img.save(os.path.join(inp, IN_BUST))
    l, t, r, b = BUST_FACE
    face_mask(BUST_WH, (ox + l * s, oy + t * s, ox + r * s, oy + b * s)).save(
        os.path.join(inp, IN_BUST_MASK))
    for n in (IN_STAND, IN_HEAD_SQ, IN_FIG_SQ, IN_BUST, IN_BUST_MASK):
        print("wrote", os.path.join(inp, n))


# ── ワークフロー ────────────────────────────────────────────────
class WF:
    def __init__(self):
        self.g, self.n = {}, 100

    def add(self, cls, **inputs):
        self.n += 1
        self.g[str(self.n)] = {"class_type": cls, "inputs": inputs}
        return [str(self.n), 0]

    @staticmethod
    def out(ref, i):
        return [ref[0], i]


def build_workflow(a):
    w = WF()
    ckpt = w.add("CheckpointLoaderSimple", ckpt_name=CHECKPOINT)
    model, vae = ckpt, WF.out(ckpt, 2)
    clip = w.add("CLIPSetLastLayer", clip=WF.out(ckpt, 1), stop_at_clip_layer=-2)

    expr = a.tags or EXPRESSIONS[a.expression or "normal"]
    if a.preset == "expr":
        pos_txt = ", ".join([QUALITY, STYLE, CHAR, FRAMING_BUST, expr])
    else:
        pos_txt = ", ".join([QUALITY, STYLE, CHAR, FRAMING_STAND, expr])
    pos = w.add("CLIPTextEncode", clip=clip, text=pos_txt)
    neg = w.add("CLIPTextEncode", clip=clip, text=a.negative or NEG)

    # IP-Adapter: 頭部（色・顔）と全身（服・シルエット）を正方形で与える
    if a.ip_weight > 0:
        ipl = w.add("IPAdapterUnifiedLoader", model=model, preset=IPADAPTER_PRESET)
        refs = [IN_HEAD_SQ] if a.preset == "expr" else [IN_HEAD_SQ, IN_FIG_SQ]
        imgs = [w.add("LoadImage", image=r) for r in refs]
        img = imgs[0]
        if len(imgs) > 1:
            img = w.add("ImageBatch", image1=imgs[0], image2=imgs[1])
        img = w.add("PrepImageForClipVision", image=img, interpolation="LANCZOS",
                    crop_position="pad", sharpening=0.0)
        model = w.add("IPAdapterAdvanced", model=WF.out(ipl, 0), ipadapter=WF.out(ipl, 1),
                      image=img, weight=a.ip_weight, weight_type="linear",
                      combine_embeds="average", start_at=0.0, end_at=1.0,
                      embeds_scaling="V only")

    def controlnet(p, n, image, kind, strength, end):
        cn = w.add("ControlNetLoader", control_net_name=CONTROLNET)
        cn = w.add("SetUnionControlNetType", control_net=cn, type=kind)
        app = w.add("ControlNetApplyAdvanced", positive=p, negative=n, control_net=cn,
                    image=image, strength=strength, start_percent=0.0, end_percent=end)
        return app, WF.out(app, 1)

    def sample(m, p, n, latent, denoise, seed_offset=0):
        return w.add("KSampler", model=m, seed=a.seed + seed_offset, steps=a.steps, cfg=a.cfg,
                     sampler_name=a.sampler, scheduler=a.scheduler, positive=p, negative=n,
                     latent_image=latent, denoise=denoise)

    if a.preset == "stand":
        init = w.add("LoadImage", image=a.init or IN_STAND)
        latent = w.add("VAEEncode", pixels=init, vae=vae)
        edges = w.add("Canny", image=init, low_threshold=0.15, high_threshold=0.4)
        p, n = controlnet(pos, neg, edges, "canny/lineart/anime_lineart/mlsd", a.cn_weight, a.cn_end)
        out = sample(model, p, n, latent, a.denoise)
    elif a.preset == "expr":
        init = w.add("LoadImage", image=a.init or IN_BUST)
        mask = w.add("LoadImageMask", image=a.mask or IN_BUST_MASK, channel="red")
        latent = w.add("VAEEncode", pixels=init, vae=vae)
        # ① 拡大でぼけた参考パネルを、線画固定のまま低 denoise で清書（表情は neutral のまま）
        if a.refine > 0:
            edges = w.add("Canny", image=init, low_threshold=0.15, high_threshold=0.4)
            base_pos = w.add("CLIPTextEncode", clip=clip,
                             text=", ".join([QUALITY, STYLE, CHAR, FRAMING_BUST, EXPRESSIONS["normal"]]))
            p, n = controlnet(base_pos, neg, edges, "canny/lineart/anime_lineart/mlsd",
                              a.cn_weight, a.cn_end)
            latent = sample(model, p, n, latent, a.refine)
        # ② 顔だけ inpaint して表情を差し替え（seed は表情によらず固定）
        masked = w.add("SetLatentNoiseMask", samples=latent, mask=mask)
        # normal も同じ inpaint を通す（通過しないと眼鏡などの描き方が他の5種とずれる）
        out = sample(model, pos, neg, masked, a.denoise, seed_offset=1) if a.denoise > 0 else latent
    elif a.preset == "pose":
        pimg = w.add("LoadImage", image=a.init or IN_STAND)
        skel = w.add("OpenposePreprocessor", image=pimg, detect_body="enable",
                     detect_hand="enable", detect_face="disable", resolution=1024)
        p, n = controlnet(pos, neg, skel, "openpose", a.cn_weight, a.cn_end)
        latent = w.add("EmptyLatentImage", width=STAND_WH[0], height=STAND_WH[1], batch_size=1)
        out = sample(model, p, n, latent, 1.0)
    else:
        raise SystemExit(f"unknown preset {a.preset}")

    dec = w.add("VAEDecode", samples=out, vae=vae)
    if a.preset == "expr":
        # マスク外はピクセル単位で清書結果（①）のまま残す
        base = w.add("VAEDecode", samples=latent, vae=vae) if a.refine > 0 else init
        dec = w.add("ImageCompositeMasked", destination=base, source=dec, x=0, y=0,
                    resize_source=False, mask=mask)
    tag = a.preset + (f"_{a.expression}" if a.preset == "expr" and a.expression else "")
    w.add("SaveImage", images=dec, filename_prefix=f"misaki_c2/{tag}")
    return w.g


# ── 実行 ────────────────────────────────────────────────────────
def _get(path):
    with urllib.request.urlopen(SERVER + path, timeout=30) as r:
        return json.loads(r.read())


def _post(path, obj):
    req = urllib.request.Request(SERVER + path, data=json.dumps(obj).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"ComfyUI error {e.code}: {e.read().decode('utf-8', 'replace')}")


def run(a):
    try:
        _get("/system_stats")
    except urllib.error.URLError:
        raise SystemExit(f"ComfyUI が起動していません: cd {COMFY} && "
                         "venv/bin/python main.py --port 8188 --listen 127.0.0.1")
    if a.seed < 0:
        a.seed = int(time.time()) % 2**31
    wf = build_workflow(a)
    pid = _post("/prompt", {"prompt": wf, "client_id": "comfy_gen"})["prompt_id"]
    peak = {"ram_used": 0, "vram_used": 0}
    t0 = time.time()
    while True:
        h = _get(f"/history/{pid}").get(pid)
        st = _get("/system_stats")
        mem, dev = st.get("system", {}), (st.get("devices") or [{}])[0]
        peak["ram_used"] = max(peak["ram_used"], mem.get("ram_total", 0) - mem.get("ram_free", 0))
        peak["vram_used"] = max(peak["vram_used"], dev.get("vram_total", 0) - dev.get("vram_free", 0))
        if h:
            break
        time.sleep(1.5)
    elapsed = time.time() - t0
    status = (h.get("status") or {}).get("status_str")
    if status != "success":
        raise SystemExit("ComfyUI failed: " + json.dumps(h.get("status"), ensure_ascii=False)[:2000])

    tag = a.name or (a.preset + (f"_{a.expression}" if a.preset == "expr" and a.expression else ""))
    outdir = os.path.join(ROOT, a.out, a.preset)
    os.makedirs(outdir, exist_ok=True)
    saved = []
    for node in h.get("outputs", {}).values():
        for img in node.get("images", []):
            q = urllib.parse.urlencode({"filename": img["filename"], "subfolder": img.get("subfolder", ""),
                                        "type": img["type"]})
            data = urllib.request.urlopen(f"{SERVER}/view?{q}", timeout=60).read()
            path = os.path.join(outdir, f"{tag}_s{a.seed}.png")
            with open(path, "wb") as f:
                f.write(data)
            saved.append(path)
    meta = {"prompt_id": pid, "seed": a.seed, "elapsed_sec": round(elapsed, 1), "peak": peak,
            "args": vars(a), "workflow": wf}
    with open(os.path.join(outdir, f"{tag}_s{a.seed}.json"), "w") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"{tag} seed={a.seed} {elapsed:.1f}s peak ram {peak['ram_used']/2**30:.1f}GB", *saved)
    return saved


def add_gen_args(g):
    g.add_argument("--preset", choices=["stand", "expr", "pose"], default="stand")
    g.add_argument("--expression", choices=list(EXPRESSIONS), default=None)
    g.add_argument("--init", default=None, help="初期画像（ComfyUI/input 内）。既定は prep の参照")
    g.add_argument("--mask", default=None, help="expr: 顔マスク（ComfyUI/input 内）")
    g.add_argument("--denoise", type=float, default=None,
                   help="stand: img2img 強度（既定 0.5） / expr: 顔 inpaint 強度（既定 0.8）")
    g.add_argument("--refine", type=float, default=0.35, help="expr: ①清書パスの denoise（0 で無効）")
    g.add_argument("--ip-weight", type=float, default=0.6)
    g.add_argument("--cn-weight", type=float, default=0.6)
    g.add_argument("--cn-end", type=float, default=0.8)
    g.add_argument("--steps", type=int, default=28)
    g.add_argument("--cfg", type=float, default=6.0)
    g.add_argument("--sampler", default="euler_ancestral")
    g.add_argument("--scheduler", default="normal")
    g.add_argument("--seed", type=int, default=5)
    g.add_argument("--negative", default=None)
    g.add_argument("--tags", default=None, help="表情タグを直接指定（パーツ差分用。--expression より優先）")
    g.add_argument("--name", default=None, help="出力ファイル名の接頭辞（既定: preset_expression）")
    g.add_argument("--out", default="output/comfy")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("prep", help="参照画像の切り出しを ComfyUI/input に作成")
    add_gen_args(sub.add_parser("gen", help="1 枚生成"))
    add_gen_args(sub.add_parser("all", help="立ち絵 1 + 表情 6 を生成"))
    a = p.parse_args()
    if a.cmd == "prep":
        return prep()
    user_denoise = a.denoise
    jobs = [("stand", None)] if a.cmd == "gen" and a.preset != "expr" else []
    if a.cmd == "gen" and a.preset == "expr":
        jobs = [("expr", a.expression)]
    if a.cmd == "all":
        jobs = [("stand", None)] + [("expr", e) for e in EXPRESSIONS]
    if a.cmd == "gen" and a.preset == "pose":
        jobs = [("pose", None)]
    for preset, expr in jobs:
        a.preset, a.expression = preset, expr
        a.denoise = user_denoise if user_denoise is not None else (0.8 if preset == "expr" else 0.5)
        run(a)


if __name__ == "__main__":
    main()
