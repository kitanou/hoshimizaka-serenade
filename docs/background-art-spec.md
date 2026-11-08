# 背景制作仕様書（Issue #67）

『星見坂のセレナーデ』の本編背景 12 枚と OP 背景 6 枚の、用途・構図・色調・画風・生成プロンプト・素材ステータスをまとめる。
画像はすべて `tools/bg_gen.py`（ComfyUI）で生成し、`tools/misaki_postprocess.py` と同じ考え方で 90 年代家庭用機風のラスターに加工している。
環境・モデルは [image-generation.md](image-generation.md)、シナリオは [story-bible.md](story-bible.md) / [route-flow.md](route-flow.md)、OP は [op-storyboard.md](op-storyboard.md)、実装は [demo-design.md](demo-design.md) を参照。

## 1. 共通方針

- **目標**: 1990 年代中期のセガサターン／初代 PlayStation 期の恋愛 ADV の背景 CG。手描きの背景美術の造形を保ち、ゲーム機向けにラスター化・減色された質感にする。
- **避けるもの**: 現代的な高精細アニメ背景、滑らかなデジタルペイント、大きな四角いドットの 8bit 風。
- **質感**: 限定パレット（約 96 色）、段階的な陰影、Bayer 4×4 の ordered dither（網点）。キャラ立ち絵（`images/chars/misaki/`、64 色）と同じ手法。
- **背景に入れないもの**: 人物、文字、UI、ロゴ。桜の花びら（`images/fx/petal.png`）・流れ星（`images/fx/shoot.png`）・星の瞬き・光は fx／ゲーム側で重ねるので、背景には描かせない（Negative に `falling petals, shooting star, meteor`）。
- **走査線・色にじみ（CRT 風）**: 背景には焼き込まない。必要なら画面全体の演出としてゲーム側で掛ける（現状は未適用）。

## 2. 技術仕様と制作フロー

| 項目 | 値 |
|---|---|
| ゲーム画面 | 640×480（4:3）。`gui.init(640, 480)` |
| 納品ファイル | PNG・1280×960（4:3）・RGB。Ren'Py では `Transform("…", zoom=0.5)`（`images.rpy` / `op.rpy`）。ファイル名は従来のまま |
| 生成 | ComfyUI / Animagine XL 3.1、txt2img 1152×864、steps 28、cfg 6.0、euler_ancestral、clip skip 2、ControlNet・IP-Adapter なし |
| ラスター化 | 1152×864 → 640×480（Lanczos）→ 96 色にパレット減色 + Bayer 4×4 ordered dither → 2 倍 Nearest で 1280×960 |
| 生成時間 | 1 枚 約 15〜18 秒（M5 Max 64GB） |

```sh
export COMFY_DIR=/path/to/ComfyUI         # ComfyUI を起動しておく（image-generation.md）
PY=$COMFY_DIR/venv/bin/python
$PY -m tools.bg_gen gen all --cn 0 --seed 7     # 11 枚。--seed 8 も作って比較する
$PY -m tools.bg_gen gen op_slope_lamp --seed 7  # OP 背景は個別名（本編 'all' に含む）
$PY -m tools.bg_gen raster all                  # 採用 seed（tools/bg_gen.py の CHOSEN）でラスター化
$PY -m tools.bg_gen sheet                       # 一覧シート output/bg/sheet.png
$PY -m tools.bg_gen install all                 # images/bg/ と images/op/ へ配置
```

- 生成ごとに `output/bg/bg/<名前>_s<seed>.json` へワークフロー全体・seed・所要時間を記録する（`output/` は git 管理外）。
- 本編は seed 7 / 8 の 2 案を作り、立ち絵を置く余白・時間帯の読みやすさで採用 seed を決めた（§5 の各表）。`rooftop_night` だけは 7/8 の出来が悪く seed 9〜11 を追加で試し 9 を採用。
- 構図ガイド（既存背景の canny）を使う方式も試したが、ベタ塗りの形に引きずられて画風が変わらなかった。ガイドなしの txt2img のほうが目標の画風に近づいたため、**構図は作り直し**とした（立ち絵の余白と視線の抜けは §5 で個別に確認）。

## 3. 棚卸し（旧素材の評価）

旧素材は手続き生成のベクター調（`tools/svg/backgrounds.py`）。ベタ塗り・単純な図形で、参考画像（`docs/images/character-misaki.webp` の学校の背景）にある手描きの陰影・質感・網点がなく、立ち絵（ディザ入り）と並べると画風が浮く。OP 背景は 320×240・32 色の大きな角ドットで、Issue の「大きな四角いピクセルにしない」に反する。

| ファイル | 旧（サイズ / 色数 / 容量） | 新（サイズ / 色数 / 容量） |
|---|---|---|
| `bg/black.png` | 1280×960 / 1 色 / 3KB | **変更なし**（暗転用） |
| `bg/slope.png` | 1280×960 / 3407 色 / 59KB | 1280×960 / 92 色 / 257KB |
| `bg/slope_sunset.png` | 1280×960 / 4167 色 / 62KB | 1280×960 / 96 色 / 183KB |
| `bg/slope_night.png` | 1280×960 / 3679 色 / 63KB | 1280×960 / 94 色 / 386KB |
| `bg/rooftop.png` | 1280×960 / 6730 色 / 142KB | 1280×960 / 96 色 / 151KB |
| `bg/rooftop_night.png` | 1280×960 / 2332 色 / 108KB | 1280×960 / 92 色 / 164KB |
| `bg/night.png` | 1280×960 / 1781 色 / 19KB | 1280×960 / 94 色 / 173KB |
| `bg/classroom.png` | 1280×960 / 1002 色 / 19KB | 1280×960 / 95 色 / 212KB |
| `bg/classroom_evening.png` | 1280×960 / 1337 色 / 20KB | 1280×960 / 96 色 / 201KB |
| `bg/hallway.png` | 1280×960 / 116 色 / 8KB | 1280×960 / 92 色 / 305KB |
| `bg/clubroom.png` | 1280×960 / 489 色 / 14KB | 1280×960 / 96 色 / 267KB |
| `bg/home.png` | 1280×960 / 433 色 / 12KB | 1280×960 / 93 色 / 220KB |
| `op/bg_op_starry_sky.png` | 320×240 / 32 色 / 4KB | 1280×960 / 91 色 / 174KB |
| `op/bg_op_title_sky.png` | 320×240 / 32 色 / 12KB | 1280×960 / 92 色 / 174KB |
| `op/bg_op_observatory_night.png` | 320×240 / 32 色 / 4KB | 1280×960 / 91 色 / 163KB |
| `op/bg_op_slope_lamp.png` | 320×240 / 32 色 / 7KB | 1280×960 / 92 色 / 260KB |
| `op/bg_op_town_twilight.png` | 320×240 / 32 色 / 7KB | 1280×960 / 95 色 / 256KB |
| `op/bg_op_hill_meteor_shower.png` | 320×240 / 32 色 / 4KB | 1280×960 / 90 色 / 129KB |

（旧の色数は AA・グラデーションを含む実色数。新は減色後。容量が増えているのはディザの網点のため。）

## 4. 本編 12 背景の仕様

以下の「判断」はすべて **再生成**（旧素材は共通方針を満たさないため）。`black.png` のみ **そのまま採用**。
キャラクターは Ren'Py の立ち位置 `pos_l / pos_c / pos_r`（`transforms.rpy`）で、画面下部に 300×450 の立ち絵（`char_zoom` 0.5）を置く。背景の下 1/3 は立ち絵・ウィンドウと重なるため、**主題（窓・街灯・ドームなど）は上 2/3、下 1/3 は床・路面などの落ち着いた面**にする。

### 4.1 `slope.png` — 星見坂・朝

| 項目 | 内容 |
|---|---|
| 使用箇所 | 序章 `prologue`（4 月・七年ぶりに帰郷した場面） |
| 構図 | 目線の高さ。中央の道が海へ下る一点透視。左右に住宅と電柱、突き当たりに青い空と海 |
| 時間・光 | 春の朝、快晴。やや高い位置の光で路面に建物の影が落ちる |
| 色 | 主色: 空の青・路面の青灰。補色: 桜のピンク・壁の暖色。明部と影をはっきり分ける |
| 余白 | 中央〜右下の路面が広く、立ち絵 `pos_c` / `pos_r` と重なっても視線が抜ける |
| 判断 | 再生成（seed 8）。旧は桜の塊と家 2 軒だけの構成で、坂の勾配が読みにくかった |

### 4.2 `slope_sunset.png` — 星見坂・夕

| 項目 | 内容 |
|---|---|
| 使用箇所 | 1 日目ミサキルート `day1_misaki`、2 日目夕方 `day2_evening` |
| 構図 | 道が海へ向かう広い構図。電柱と電線が画面を横切り、遠くに海と山の稜線、右に夕日 |
| 時間・光 | 夕暮れ。ピンク〜橙の空、低い太陽、長い影 |
| 色 | 主色: 橙・ピンク・紫。影は青紫〜茶。色温度は暖色寄り |
| 余白 | 左中央に空と道が開いており、`pos_l` の立ち絵を置ける |
| 判断 | 再生成（seed 7） |

### 4.3 `slope_night.png` — 星見坂・夜

| 項目 | 内容 |
|---|---|
| 使用箇所 | 3 日目ミサキルート `day3_misaki`、ノーマル END `end_normal`（「夜の坂道に三つの影が並んだ」） |
| 構図 | 狭い夜の路地。両側の家に黄色い窓明かり、街灯、奥へ続く道。上に三日月と星 |
| 時間・光 | 夜。街灯と窓明かりが主光源。空は深い青 |
| 色 | 主色: 濃紺。補色: 窓・街灯の黄。コントラスト高め |
| 余白 | 中央の路面は暗く静かで、立ち絵の顔が埋もれない（立ち絵は明るい） |
| 判断 | 再生成（seed 8）。「坂」の読みは序章・夕景より弱いが、夜景として自然 |

### 4.4 `rooftop.png` — 学校屋上・夕

| 項目 | 内容 |
|---|---|
| 使用箇所 | 1 日目冬華ルート `day1_touka`、2 日目ミサキルート `day2_misaki` |
| 構図 | 屋上の床を広く取り、奥にフェンスと街のシルエット。右に建物 |
| 時間・光 | 夕焼け。紫から橙の空。床に長い影 |
| 色 | 主色: 紫・橙。床は灰青 |
| 余白 | 下半分が広い床で、立ち絵が余裕を持って立てる |
| 判断 | 再生成（seed 8）。旧にあった水タンク・夕日はなく、フェンスと街のシルエットのみ。**要確認**: 脚本に水タンクへの言及がないため現状で足りる |

### 4.5 `rooftop_night.png` — 学校屋上・夜

| 項目 | 内容 |
|---|---|
| 使用箇所 | 3 日目冬華ルート `day3_touka`、冬華 END `end_touka`（「夜の屋上には、望遠鏡と、ふたつの影」） |
| 構図 | 屋上から見る星空。左奥に水タンク、フェンス、遠くの山。右上に三日月 |
| 時間・光 | 夜。月明かりと星 |
| 色 | 主色: 深い青。補色: 月の白黄 |
| 余白 | 手前の広い床が立ち絵用 |
| 判断 | 再生成（seed 9）。**望遠鏡は背景に描かない**（立ち絵と干渉するため、必要なら別レイヤーの小道具画像で重ねる。§7 の課題）。旧にあった望遠鏡は失われている |

### 4.6 `night.png` — 星降る夜空と丘

| 項目 | 内容 |
|---|---|
| 使用箇所 | ミサキ END `end_misaki` の冒頭（直後に CG `misaki_end` へ切替） |
| 構図 | 上 2/3 が星空と天の川、下に丘のシルエットと街の灯り |
| 時間・光 | 深夜。星明かりのみ |
| 色 | 濃紺〜紺、街灯りの黄 |
| 余白 | 空が広く、タイトル級の文章表示が読みやすい |
| 判断 | 再生成（seed 8）。流れ星は背景に焼き込まない（旧は焼き込み。効果音 `audio.shoot` と fx `shoot_fx` で出す） |

### 4.7 `classroom.png` — 教室・昼

| 項目 | 内容 |
|---|---|
| 使用箇所 | 1 日目冒頭（始業式・自己紹介）`day1`、2 日目授業後 `day2`、3 日目 `day3` |
| 構図 | 教室後方〜中央から窓側を見る。窓の外に満開の桜、黒板、机、時計 |
| 時間・光 | 春の昼。窓から斜めに光が入り、床に明暗の帯 |
| 色 | 主色: 緑（黒板・壁）・木の茶・窓の空色。桜のピンクが差し色 |
| 余白 | 中央〜右の床が広く、立ち絵が置ける |
| 判断 | 再生成（seed 8） |

### 4.8 `classroom_evening.png` — 教室・夕

| 項目 | 内容 |
|---|---|
| 使用箇所 | 1 日目放課後 `day1`、3 日目放課後 `day3`（選択肢） |
| 構図 | `classroom` と同じ視点。窓の外は夕焼けと山 |
| 時間・光 | 夕方。橙の光が床に長く伸びる |
| 色 | 主色: 橙・黄。窓際の影は青緑 |
| 余白 | 床が広い |
| 判断 | 再生成（seed 8）。昼夕で窓と机の位置が完全には一致しない（生成のため）。場面が切り替わる（`with fade`）ので許容 |

### 4.9 `hallway.png` — 学校廊下

| 項目 | 内容 |
|---|---|
| 使用箇所 | 2 日目冒頭 `day2`（楓との初対面） |
| 構図 | 一点透視で奥へ伸びる廊下。左にロッカー、右に窓、天井に蛍光灯 |
| 時間・光 | 昼。窓からの光で床に帯 |
| 色 | 主色: 木の茶・壁の白。蛍光灯の暖白 |
| 余白 | 床の中央が空くが、左右の壁が近く立ち絵 `pos_l` / `pos_r` は壁に被る。中央（`pos_c`）を基本にする |
| 判断 | 再生成（seed 8） |

### 4.10 `clubroom.png` — 天文部室

| 項目 | 内容 |
|---|---|
| 使用箇所 | 2 日目冬華ルート `day2_touka`（父親の望遠鏡・星図の会話） |
| 構図 | 奥に窓（夕日）、左右に壁、手前に机。右の壁に貼り紙（星図の代わり） |
| 時間・光 | 夕方。窓から暖色の光 |
| 色 | 主色: 木の茶・オリーブ。窓の橙 |
| 余白 | 手前に机が入り、下 1/3 は立ち絵と重なる |
| 判断 | 再生成（seed 7）。**星図・望遠鏡は読み取れる形では描けていない**（生成の限界）。星図や望遠鏡が必要なら小道具レイヤーを別途用意する（§7） |

### 4.11 `home.png` — 主人公の部屋・夜

| 項目 | 内容 |
|---|---|
| 使用箇所 | 現行の体験版では未使用（将来の自宅イベント用） |
| 構図 | ベッド、机と小さなランプ、窓から満月と星空 |
| 時間・光 | 夜。月明かりとランプの小さな明かり |
| 色 | 主色: 濃紺。窓の月の白、ランプの暖黄、カーテンの赤紫 |
| 余白 | 中央が窓のため、立ち絵は左右に置く |
| 判断 | 再生成（seed 8）。未使用なので脚本では確認していない |

### 4.12 `black.png` — 黒背景

| 項目 | 内容 |
|---|---|
| 使用箇所 | 序章冒頭の暗転、日付表示などの場面転換 |
| 判断 | **そのまま採用**。 |

## 5. OP 背景と CUT の対応

OP 背景は 320×240・32 色の角ドットだったため **6 枚すべて再生成**した（本編と同じ手順・1280×960。`op.rpy` は `zoom=2, nearest=True` を `zoom=0.5` に変更。移動・ズーム演出の変換は 640×480 換算で同じ）。
背景には流れ星・光のエフェクトを描かず、op.rpy 側で重ねる（絵コンテどおり）。

| ファイル | CUT | 内容 | 判断・備考 |
|---|---|---|---|
| `bg_op_starry_sky.png` | 02 | 流星の背景になる夜空（天の川） | 再生成（seed 9）。下端に丘の細い帯が入った |
| `bg_op_title_sky.png` | 03 / 13 | ロゴの背景の星空 | 再生成（seed 9）。ロゴと重なるので中央に主題を置かない |
| `bg_op_observatory_night.png` | 06 | 丘の上の天文台（ドーム） | 再生成（seed 8）。`op_obs_drift` で横にゆっくり流す |
| `bg_op_slope_lamp.png` | 09 | 朝の坂道。奥に明るい空 | 再生成（seed 7）。`op_slope_forward`（前進ズーム 1.12 倍） |
| `bg_op_town_twilight.png` | 10 | 夕焼けの坂道、太陽 | 再生成（seed 7）。キャラは別 PNG で下部に重なる |
| `bg_op_hill_meteor_shower.png` | 12 | 丘から見る街の夜景。上は星空、下に街の灯り | 再生成（seed 7）。`op_hill_zoomout`（1.3 倍→等倍）。流星は描かない |

**不足候補の判断**

| ファイル | 判断 | 理由 |
|---|---|---|
| `bg_op_meteor_shower.png` | **作らない** | CUT 12 は `bg_op_hill_meteor_shower.png` を使う（絵コンテ・実装とも）。役割が重複する。流星群は fx で描く |
| `bg_op_railway_crossing.png` | **作らない** | どの CUT にも使われない（絵コンテ・脚本に踏切の場面がない） |
| `bg_op_telescope_sky.png` | **作らない** | CUT 06 は天文台背景で足りている |

幾何学エフェクト素材（`stripes` / `circle` / `speed` / `halftone_c` / `halftone_y` / `sunburst` / `glow`）は背景と分けて扱い、今回は変更していない。

## 6. 生成プロンプト

プロンプトの実体は `tools/bg_gen.py`（`STYLE` / `NEG` / `BG` / `OP`）。以下はその時点の全文。意図は各行の前後の説明と §4 の表を参照。
Animagine XL 3.1 の Danbooru タグ語彙で書いている（日本語の補足は §4・§5）。

### 共通 Positive（全背景の先頭に付ける）

```text
masterpiece, best quality, very aesthetic, absurdres,
scenery, no humans, background, 1990s (style), retro artstyle, game cg, hand-painted anime background art, natural colors, bright daylight, clear contrast, deep shadows, simple composition, eye-level view, wide shot, open space in the center, bishoujo adventure game background, school life game background
```

### 共通 Negative

```text
lowres, worst quality, low quality, jpeg artifacts, blurry, 1girl, 1boy, multiple girls, people, human, character, silhouette of person, text, logo, watermark, signature, speech bubble, ui, window frame border, photorealistic, 3d, cgi, vector art, smooth gradient, glossy, modern anime, chromatic aberration, vignette, letterboxed, black bars, scanlines, falling petals, shooting star, meteor, fantasy, ghibli, oversaturated, pastel, washed out, faded, busy composition, cluttered, aerial view, bird's eye view, castle, temple, bridge
```

### 個別 Positive / Negative（追加分）

**`bg/slope.png`**（採用 seed 8）

```text
ordinary japanese seaside town street, a straight asphalt road sloping down toward the sea at the center, spring morning, clear blue sky with a few white clouds, cherry blossom trees on both sides, utility poles with power lines, modern japanese suburban houses with concrete walls, the blue ocean visible at the end of the road, the road slopes down to the vanishing point
```

**`bg/slope_sunset.png`**（採用 seed 7）

```text
japanese seaside town, a gently sloping road going down to the sea, sunset, orange and pink gradient sky, setting sun over the ocean, cherry blossom trees, utility pole with power lines, houses with warm lit windows, long shadows, evening light
```

**`bg/slope_night.png`**（採用 seed 8）

```text
japanese seaside town, a gently sloping road going down to the sea, night, starry sky, crescent moon, cherry blossom trees in the dark, street lamp glowing, utility pole with power lines, houses with yellow lit windows, deep blue night
```

**`bg/rooftop.png`**（採用 seed 8）

```text
school rooftop, chain-link fence, water tank, sunset, orange and purple sky, silhouette of the town and the sea in the distance, concrete floor, evening light
```

**`bg/rooftop_night.png`**（採用 seed 9）

```text
school rooftop at night, chain-link fence, water tank, starry sky, crescent moon, a refracting astronomical telescope on a tripod in the foreground, town lights far below, deep blue night
```

**`bg/night.png`**（採用 seed 8）

```text
night sky full of stars, milky way, dark hill silhouette against the sky, small town lights twinkling below the hill, deep blue to black gradient sky, quiet and wide open
```

**`bg/classroom.png`**（採用 seed 8）

```text
japanese high school classroom, daytime, large window with blue sky and pink cherry blossoms outside, green blackboard with chalk marks, wall clock, wooden student desks, wooden floor, warm sunlight
```

**`bg/classroom_evening.png`**（採用 seed 8）

```text
japanese high school classroom, after school, sunset, orange light pouring through the window, green blackboard with chalk marks, wall clock, wooden student desks, wooden floor, long soft shadows
```

**`bg/hallway.png`**（採用 seed 8）

```text
japanese high school hallway, daytime, row of windows on one side, grey shoe lockers, wooden floor, ceiling fluorescent light, perspective view, bright
```

**`bg/clubroom.png`**（採用 seed 7）

```text
school astronomy club room, big star chart on the wall, wooden table, window with warm light, books and papers, wooden floor, cozy, a little messy, evening
```

**`bg/home.png`**（採用 seed 8）

```text
boy's bedroom at night, bed with blanket, wooden desk with a small lamp, window showing a starry night sky and the moon, dim blue light, cozy room
```

**`op/bg_op_starry_sky.png`**（採用 seed 9）

```text
sky only, starry night sky, dense small stars, faint milky way, smooth deep navy to indigo gradient
```
Negative に追加:
```text
mountain, hill, ground, horizon, land, trees, buildings, moon, ring, circle, swirl
```

**`op/bg_op_title_sky.png`**（採用 seed 9）

```text
sky only, dark starry night sky, sparkling stars, soft purple and blue glow in the center, smooth gradient, minimal, calm
```
Negative に追加:
```text
mountain, hill, ground, horizon, land, trees, buildings, ring, circle, swirl, ornament, decoration, moon, sun, planet, floor, tiles
```

**`op/bg_op_observatory_night.png`**（採用 seed 8）

```text
a small astronomical observatory building with a white dome roof and white walls, standing on a grassy hill at night, glowing yellow windows, starry sky, crescent moon, wooden fence, wide shot, the building is small in the frame, plenty of sky
```
Negative に追加:
```text
giant, huge, abstract, ring, circle, swirl, ornament, green, crescent shaped building, close-up
```

**`op/bg_op_slope_lamp.png`**（採用 seed 7）

```text
ordinary japanese seaside town street, a straight asphalt road sloping down toward the sea at the center, clear morning sky with bright light at the end of the road, street lamp, cherry blossom trees, utility poles with power lines, houses on both sides, the road leads to the vanishing point
```

**`op/bg_op_town_twilight.png`**（採用 seed 7）

```text
ordinary japanese seaside town street, a straight asphalt road sloping down toward the sea at the center, twilight, the sun setting over the ocean, purple and orange sky, first stars appearing, utility poles with power lines, houses with lit windows, the road leads to the vanishing point
```

**`op/bg_op_hill_meteor_shower.png`**（採用 seed 7）

```text
wide shot from a hill looking over a small town at night, vast starry sky filling the upper half, town lights twinkling in the lower half, dark hill silhouette in the foreground, no meteors
```

## 7. 評価・既知の課題

- **画風**: 参考画像の学校の背景に近い、手描き背景＋網点の質感になった。立ち絵（`images/chars/misaki/`）と並べても質感が浮かない（確認画像は PR を参照）。
- **一貫性**: 各背景は別々の生成で、同じ場所の昼・夕・夜（`slope*`、`classroom*`、`rooftop*`）は建物の形が一致しない。場面転換（`with fade` / `dissolve`）を挟むので許容した。完全に揃えるなら、同じ構図ガイドからの img2img や専用 LoRA が必要。
- **小道具**: 望遠鏡・星図・水タンクなど、シナリオ上の小道具は背景に確実には描けない。必要なら背景とは別の透過 PNG として用意し、ゲーム側で重ねる（未着手）。
- **旧素材の記録**: 旧背景（ベクター調）は git 履歴に残り、生成コード `tools/svg/backgrounds.py` も残してある。旧素材で上書きしないよう、`tools.gen_images`（引数なし）は背景を作り直さず、`tools.op_assets` は OP 背景を作り直さない。今後は `tools/bg_gen.py` を正とする。
- **CRT 風処理**: 未適用。
- **立ち絵との合成**: 640×480 でミサキ（表情プリセット）と合成して視認性を確認した。他キャラ（冬華・楓）は旧画風のまま（別 Issue）。
