# キャラクター素材のローカル生成（Issue #65）

美咲の参考シート `docs/images/character-misaki.webp` を基準に、ComfyUI で立ち絵・表情差分を生成し、
後処理で 640×480 ゲーム向けのラスター（減色・ディザ）素材にする手順と設定値の記録。

## なぜ「参考画像に似なかった」か（推定原因と対策）

個別に切り分け検証はしていない。最も効いたのは img2img + canny（参考画像を初期画像にする）への変更。

| 旧構成の推定原因 | 症状 | 対策（現構成） |
|---|---|---|
| IP-Adapter に縦長の全身画像を渡していた。CLIP-ViT-H は短辺 224 に縮めて**中央を正方形に切る**ため、頭部・髪がほぼ写らない | 青髪・金髪化、別人化 | 頭部と全身を**正方形パッド**して渡す（`PrepImageForClipVision crop_position=pad`） |
| txt2img + IP-Adapter だけで造形を作っていた | ポーズ・服・顔立ちが毎回変わる | 立ち絵は**参考 figure からの img2img（denoise 0.5）+ ControlNet canny** で線画を固定 |
| 576×1024（約 0.59MP）で生成 | 頭切れ・端に別キャラの断片 | SDXL の 1MP バケット（立ち絵 832×1216 / バスト 896×1152） |
| Pony 用の `score_9…` タグを Animagine に使用 | 効果なし | Animagine XL 3.1 の Danbooru タグ（`round eyewear, serafuku, red bowtie …`） |
| 90s VHS 風 LoRA | 色収差・青フリンジ（サターン風ではない） | 既定 off（比較用に残すなら別途 A/B） |
| 表情を全体 img2img で作成 | 表情ごとに顔立ちがずれる | **顔だけマスク inpaint**（髪・眼鏡・制服はマスク外で不変） |
| ドット感を生成側に描かせようとした | ノイズ・グリッチ | 生成はセル画まで。ドット・減色・ディザは `tools/misaki_postprocess.py` |

## 環境

- Apple M5 Max 64GB, macOS, Python 3.12, torch 2.15.0 (MPS)
- ComfyUI `0decb39`（2026-11-08）
- custom_nodes: `ComfyUI_IPAdapter_plus` `a0f451a`, `comfyui_controlnet_aux` `a587a4c`

| 種類 | ファイル（`ComfyUI/models/…`） |
|---|---|
| checkpoint | `checkpoints/animagine-xl-3.1.safetensors`（Cagliostro Lab。ライセンス: Fair AI Public License 1.0-SD とされる・**要確認**） |
| IP-Adapter | `ipadapter/ip-adapter-plus_sdxl_vit-h.safetensors` |
| CLIP Vision | `clip_vision/CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors` |
| ControlNet | `controlnet/controlnet-union-sdxl-1.0-promax.safetensors`（xinsir。ライセンス**要確認**） |

ComfyUI 本体・モデルは git 管理外（`.gitignore` の `ComfyUI/`）。リポジトリ外に置く場合は `COMFY_DIR` で指定する。

```sh
git clone https://github.com/comfyanonymous/ComfyUI && cd ComfyUI
python3.12 -m venv venv && venv/bin/pip install -r requirements.txt
git -C custom_nodes clone https://github.com/cubiq/ComfyUI_IPAdapter_plus
git -C custom_nodes clone https://github.com/Fannovel16/comfyui_controlnet_aux
venv/bin/pip install -r custom_nodes/comfyui_controlnet_aux/requirements.txt
# 上表のモデルを models/ 以下に配置
venv/bin/python main.py --port 8188 --listen 127.0.0.1
```

## 生成手順

```sh
export COMFY_DIR=/path/to/ComfyUI
PY=$COMFY_DIR/venv/bin/python
$PY -m tools.comfy_gen prep              # 参考シート → ComfyUI/input/ms_*.png
$PY -m tools.comfy_gen all --seed 5      # 立ち絵1 + 表情6 → output/comfy/{stand,expr}/
$PY -m tools.misaki_postprocess output/comfy/stand/stand_s5.png --kind stand
$PY -m tools.misaki_postprocess output/comfy/expr/*.png --kind bust
# → output/comfy/*/pp/<名前>_<変種>.png と 640x480 プレビュー <名前>_preview.png
# ゲームへ書き出し（600x900 透明キャンバス、char_zoom 0.5 規約）
$PY -m tools.misaki_postprocess output/comfy/expr/expr_smile_s5.png --kind bust --variants C \
    --dest hoshimizaka/game/images/chars/misaki/gen_bust_smile.png
```

各生成で `output/comfy/<preset>/<名前>.json` にワークフロー全体・seed・所要時間・ピーク RAM を保存する。

## パーツ差分（layeredimage 用）

```sh
$PY -m tools.comfy_gen prep
$PY -m tools.misaki_parts masks     # 部位マスクと眼鏡抽出の確認画像 output/parts/masks.png
$PY -m tools.misaki_parts gen       # 基準 + 目4・口5・眉4 の差分（約5分。--only eyes などで部位だけ）
$PY -m tools.misaki_parts build     # レイヤー化 → hoshimizaka/game/images/chars/misaki/
$PY -m tools.misaki_parts sheet     # 10 プリセットの確認シート output/parts/sheet.png
python -m tools.gen_rpy             # images.rpy を再生成
```

- 部位マスク（基準 896×1152 上の楕円）: 眉 (180,335)-(660,458)、目 (165,445)-(660,610)、口 (330,612)-(500,705)。座標は seed 5 の基準画像で目視計測した値で、**基準を作り直したら測り直す**（`masks` で確認）。
- inpaint 強度: 目・口 0.85、眉 0.9。表情タグは `misaki_parts.TAGS`。目は Negative に `(wink:1.4), (one eye closed:1.4)` を追加（ないと笑い目・閉じ目が片目ウインクになった）。
- 眼鏡: 目のマスクから眼鏡フレームを除外して基準の線を残し、さらに `base_front` として上に重ねる。
- 既知の課題: 怒り眉は前髪に隠れて弱い。頬染めは控えめ。参考パネル自体が左端で髪を切っているため、髪の左端が直線になる。

## 確定設定（seed 5 で検証）

共通: steps 28 / cfg 6.0 / euler_ancestral / normal / clip skip 2 / IP-Adapter PLUS weight 0.6（linear, V only）

| preset | 初期画像 | denoise | ControlNet | IP-Adapter 参照 |
|---|---|---|---|---|
| `stand` | 参考 figure（青い影除去）を 832×1216 に配置 | 0.5 | union canny 0.6, end 0.8 | 頭部 + 全身（正方形・平均） |
| `expr` | 参考「通常」バストを 896×1152 に拡大 | ① 清書 0.35（canny 0.6）→ ② 顔マスク inpaint **0.8** | ①のみ | 頭部 |
| `pose` | OpenPose 用ポーズ画像 | 1.0（txt2img） | union openpose | 頭部 + 全身 |

- 表情 inpaint 0.7 + 重みなしタグでは「悲しみ」「怒り」が通常顔と区別しにくかった。denoise 0.8 と重み付きタグ（`(angry:1.4), (v-shaped eyebrows:1.4)` 等。`EXPRESSIONS`）を同時に変更して改善（どちらが効いたかは未切り分け）。
- `normal` も同じ顔 inpaint を通す。通さないと眼鏡の描き方が他 5 種とずれる。眼鏡は `(thin-framed eyewear:1.3), (black-framed eyewear:1.2)` で 6 種を統一（参考より線がやや太く黒い）。
- 実測（M5 Max 64GB）: 1 枚 18〜26 秒、ピーク RAM 約 42〜43GB（システム全体）。

## 後処理（ラスター化）の比較

画面解像度（バスト高 450px / 立ち絵高 468px）で処理し、Nearest で 2 倍にして保存（ドットが 1 画面ピクセルに揃う）。

| 変種 | 内容 | 所見 |
|---|---|---|
| A | 縮小のみ | 綺麗すぎて現代寄り |
| B | 1/2 縮小 → Nearest | 未評価（粗いドット化の比較用） |
| **C** | 64 色 + Bayer 4×4 ordered dither | **採用候補**。網点が出つつ顔・眼鏡が読める |
| D | B + C | 立ち絵の脚・スカートに網点が強く出る。表情の視認性は落ちる |
| FS | 64 色 + Floyd–Steinberg | 粒状感は自然だが、参考のような規則的な網点にはならない |

背景透過: 外周から連続する白を透過。バストは白い制服が下辺に接するため、下 30% は行ごとに最左〜最右のインク間を不透明化。アルファは 2 値。

## 既知の課題・次の一手

- 眼鏡フレームが参考（細いグレー）より太く黒い。6 種で統一はされている。マスクから眼鏡を外す方法も候補。
- 64 色だと肌がややピンク寄りになる。`--colors 96〜128` も比較候補。
- **`pose`（ゼロから構図を作る生成）はまだ参考に似ない**: 髪が明るい、目が赤い、リボンがスカーフ状、靴下が長い（`--ip-weight 0.85` でも同様）。参考画像を初期画像にできないため。美咲専用 LoRA（stand/expr の出力を学習素材に）で解決するのが本筋。
- 背景は `tools/bg_gen.py` で生成する（手順・プロンプトは [background-art-spec.md](background-art-spec.md)）。イベント CG は未着手。
