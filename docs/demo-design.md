# 星見坂のセレナーデ デモ版 詳細設計書（Ren'Py 版）

- 対象: デモ版 ver.0.97（配布用体験版。劇中で ver.0.96 と表記されていたプロトタイプの次の版として番号を続ける）
- エンジン: Ren'Py 8.x（Python 3）
- 元にするもの: `index.html`（以下「プロトタイプ」。ver.0.96 体験版として作った単一 HTML）
- 作成日: 2026-11-08

---

## 1. 前提・スコープ

### 1.1 方針

- プロトタイプは**仕様の元**として扱う。脚本、演出の段取り、配色、キャラデザイン、楽曲データを Ren'Py に移す。プロトタイプのコードそのものは移植しない。
- Ren'Py に最初からある機能はできるだけそのまま使う。セーブ／ロード、バックログ（History）、既読スキップ、オート、ロールバック、音量設定がこれにあたる。自作するのは「90年代 PC-98／サターン風の見た目」と「OP演出」の2点に絞る。
- 素材は**手続き生成をソースとする**。プロトタイプの SVG 描画ロジックと FM 音源風の楽曲を Python ツールで PNG／OGG に書き出し、Ren'Py から読む（§7）。

### 1.2 プロトタイプとデモ版の差分

| 項目 | プロトタイプ (ver.0.96) | デモ版 (ver.0.97) |
|---|---|---|
| 収録範囲 | 4/8 始業式の1日 | プロローグ＋第1章（4/8〜4/10 の3日間） |
| 選択肢 | 1回（ジャンプのみ） | 4回（好感度が変わる） |
| エンディング | 1種（体験版終了カード） | 3種（ミサキ予告END／冬華予告END／ノーマル予告END） |
| プレイ時間 | 約3分 | 約25〜35分（1周）、全END回収で約60分 |
| 本文 | 約70行 | 約700〜900行 |
| 背景 | 7種 | 12種（§7.2） |
| 立ち絵の表情 | 6種×2人 | 9種×2人＋サブキャラ1人（§7.1） |
| BGM | 3曲 | 7曲（§7.3） |
| SE | 2種 | 10種前後 |
| CG（一枚絵） | なし | 3枚（各END用） |
| セーブ | なし | あり（Ren'Py 標準。スロット数はUIで決める） |
| 設定画面 | ミュートのみ | BGM／SE 音量、文字速度、オート速度、既読スキップ、全画面 |
| おまけ | なし | OP鑑賞、エンディングリスト |

### 1.3 スコープ外（製品版で扱うもの）

- 個別ルート本編、ボイス、CGギャラリー全般、多言語対応

---

## 2. 開発環境・ファイル構成

### 2.1 環境

- Ren'Py SDK 8.x の最新安定版（着手時にバージョンを固定し、`README` に書く）
- 素材生成ツール: Python 3.11 以上（Ren'Py 同梱の Python とは別の venv にする）
  - `cairosvg`（SVG → PNG）、`numpy`＋`soundfile`（楽曲レンダリング）、OGG 化は `ffmpeg`
- バージョン管理: このリポジトリ。生成物（PNG/OGG）もコミットする。ビルドに Python ツールを必須にしないため。
- **`.rpyc` もコミットする**。セーブ互換を保つのに必要（§5.1）。`.gitignore` には `game/cache/`、`*.rpyb`、`log.txt`、`traceback.txt`、`errors.txt` だけを入れる。

### 2.2 解像度

- **内部解像度 640×480（4:3）に決定**。プロトタイプと同じ寸法なので、座標・サイズ・秒数をそのまま移せる。
  - `config.screen_width = 640` / `config.screen_height = 480`。ウィンドウ・全画面とも拡大表示は Ren'Py に任せる（`config.gl_resize = True`）。
  - 日本語は小さく表示されるため、フォントはドット系・丸ゴシック系で太めを選び、本文は 19〜20px を下限にする（§4.1）。
- 背景・立ち絵は 640×480 基準で書き出す。SVG の viewBox がそのまま使える。

### 2.3 ディレクトリ構成

```
novel-game-90s/
├─ index.html                 # プロトタイプ（今後 prototype/ へ移動）
├─ docs/demo-design.md        # 本書
├─ tools/                     # 素材生成（Ren'Py には同梱しない）
│   ├─ svg/                   # charSVG/bg* の Python 移植
│   │   ├─ chars.py           # 立ち絵パーツ（レイヤー別）
│   │   └─ backgrounds.py
│   ├─ gen_images.py          # → game/images/ へ PNG 出力
│   ├─ music/
│   │   ├─ synth.py           # tone/kick/snare/noiseHit の numpy 移植
│   │   └─ songs.py           # SONGS 定義（プロトタイプから移植＋新曲）
│   ├─ render_audio.py        # → game/audio/ へ OGG 出力
│   └─ requirements.txt
└─ hoshimizaka/               # Ren'Py プロジェクト
    └─ game/
        ├─ options.rpy        # config.*（タイトル、解像度、ビルド設定）
        ├─ gui.rpy            # gui.*（色・フォント・寸法）
        ├─ screens.rpy        # 画面定義（§4）
        ├─ characters.rpy     # Character 定義
        ├─ images.rpy         # layeredimage・背景・CG の宣言
        ├─ transforms.rpy     # ATL（揺れ、まばたき、OPのカメラワーク）
        ├─ audio.rpy          # BGM/SE 定義、音量チャンネル
        ├─ variables.rpy      # default／persistent の宣言
        ├─ splash.rpy         # 起動画面（BIOS 風）
        ├─ op.rpy             # オープニング
        ├─ script.rpy         # label start → 章の呼び出し
        ├─ story/
        │   ├─ prologue.rpy
        │   ├─ day1.rpy       # 4/8
        │   ├─ day2.rpy       # 4/9
        │   ├─ day3.rpy       # 4/10
        │   └─ endings.rpy
        ├─ fonts/  images/  audio/  gui/
        └─ tl/                # （将来の翻訳用。デモでは空）
```

---

## 3. 画面遷移

```
[splashscreen: BIOS起動] ─クリック/Enter→ [OP]
      ※2回目以降の起動では OP をスキップしてタイトルへ（persistent.op_seen）
[OP] ─終了/スキップ→ [タイトル(main_menu)]
[タイトル]
   ├ はじめから   → label start
   ├ つづきから   → ロード画面（セーブが無ければボタン無効）
   ├ オープニング → OP（終わったらタイトルへ戻る）
   ├ おまけ       → エンディングリスト（1つでも見たら有効）
   ├ 設定         → preferences
   └ 終了
[本編] ─右クリック/ESC→ [ゲームメニュー(game_menu)]
           ├ セーブ / ロード / 設定 / バックログ / タイトルへ / 終了
[本編] ─マウスホイール上/PageUp→ [バックログ(history)]
[END] → [体験版終了カード] → [タイトル]
```

| Ren'Py の仕組み | 対応する画面 |
|---|---|
| `label splashscreen` | BIOS 起動画面。`persistent.op_seen` で分岐する |
| `label op`（`call` で呼ぶ） | OP。`main_menu` からは `Replay("op")` で再生する（鑑賞モード。本編のセッションを始めない） |
| `screen main_menu` | タイトル（独自レイアウトに書き換える） |
| `screen game_menu` 系 | save/load/preferences/history。90年代風のウィンドウ枠を共通の `frame` スタイルにまとめる |
| `screen say` / `screen choice` | テキストウィンドウ、選択肢 |
| `screen quick_menu` | 画面下部の小ボタン（ログ／スキップ／オート／セーブ／ロード／設定）。プロトタイプの「タイトルへ」「♪」ボタンの後継 |

---

## 4. 画面（screens.rpy）詳細

### 4.1 共通スタイル（プロトタイプの CSS 変数を移す）

```python
# gui.rpy 抜粋
define gui.accent_color      = "#ff5fa2"   # --pink
define gui.idle_color        = "#ffffff"
define gui.hover_color       = "#ffe27a"   # --gold
define gui.text_color        = "#ffffff"
define gui.interface_text_color = "#cfe0ff" # --line
define gui.text_font  = "fonts/BIZUDPGothic-Regular.ttf"
define gui.name_text_font = "fonts/MPLUSRounded1c-Bold.ttf"
define gui.interface_text_font = "fonts/DotGothic16-Regular.ttf"
define gui.text_size = 19                   # プロトタイプと同じ 19px。実機で見て調整
```

- フォントは同梱できるライセンスのもの（いずれも SIL OFL）にする。Ren'Py 標準の DejaVu には日本語グリフが無いので、**日本語フォントの同梱が必須**。
  - 本文: BIZ UDPGothic／名前・ロゴ: M PLUS Rounded 1c／UI・BIOS: DotGothic16
- ウィンドウ枠（`#win` の二重線と角丸）は 9-slice の PNG（`gui/frame.png`）にし、`Frame("gui/frame.png", 24, 24)` で使う。

### 4.2 say スクリーン

- 位置: 画面下部。左右の余白 14px、下 12px、高さ 128px（プロトタイプの `#win` と同じ）
- 名前欄: ウィンドウ左上にはみ出すラベル（`#name`）。キャラごとの色は `Character(..., namebox_background=...)` で切り替える（§6）。
- クリック待ちカーソル: `ctc` に `▼` の点滅（ATL）を指定する。
- 文字速度: Ren'Py 標準の `preferences.text_cps`。初期値はプロトタイプの 32ms/字にほぼ等しい 30cps。

### 4.3 choice スクリーン

- 中央に縦並び、幅 360px。半透明の暗幕を敷く。頭に「◆」を付け、hover でピンクのグラデーションにする（`.cbtn` を移す）。
- 既に選んだ選択肢: `gui.choice_button_text_insensitive_color` の代わりに、`chosen` で色を変える（2周目以降の手がかり）。

### 4.4 main_menu（タイトル）

- 背景: `bg slope_sunset`。中央上にロゴ（画像化した `logo.png`。プロトタイプのグラデ文字を書き出したもの）、その下にボタンを縦並び。
- BGM: `title`（ループ）
- 下部: `©1996 星屑工房 STARDUST WORKS ／ DEMO ver.0.97`

### 4.5 体験版終了カード

- `screen demo_end(ending_id)`。プロトタイプの `#endcard` を移す。
- 「体験版はここまでです」「～ to be continued ～」「1996年 冬 発売予定!?」と、見たエンディング名を表示する。クリックで `MainMenu(confirm=False)`。

### 4.6 エンディングリスト（おまけ）

- `persistent.endings_seen`（set）を見て、3枠を表示する。未回収の枠は「？？？」とヒントの一行。

### 4.7 ポストエフェクト（CRT 走査線・ディザ）

- `config.overlay_screens` に `crt_overlay` を登録し、全画面の半透明 PNG（走査線＋周辺減光、`gui/crt.png`）を最前面に置く。
- 設定画面に「走査線 ON/OFF」を用意する（`persistent.crt`）。可読性を気にする人向け。
- （任意・後回し）model-based rendering のシェーダ（`renpy.register_shader`）で、軽い樽型歪みや RGB ずれを入れる。デモの必須要件にはしない。

---

## 5. 状態・変数設計（variables.rpy）

### 5.1 ゲーム変数（セーブに含まれる）

```python
default misaki_aff   = 0        # ミサキ好感度
default touka_aff = 0        # 冬華好感度
default joined_astro = False # 天文部に入部したか（day1 の選択で決まる）
default promised_misaki = False # 流星群の約束をしたか
default met_kaede = False    # サブキャラ・楓と会ったか（day2）
```

- Ren'Py は `default` の変数を自動でセーブ・ロールバックの対象にする。**スクリプトの行番号に依存しないので、脚本を編集しても旧セーブが壊れにくい**（プロトタイプの `ip` インデックス方式の問題は起きない）。
- ただし Ren'Py は「今どの文を実行中か」もセーブに含める。文の同一性は **`.rpyc` ファイル**で管理されるので、`.rpyc` を消すと脚本を編集した後に旧セーブが壊れる。**`game/**/*.rpyc` はリポジトリにコミットし、`.gitignore` に入れない**（§2.1）。
- label を改名・削除しても旧セーブが復帰できなくなる。デモ配布後は**既存 label の改名をしない**こととし、必要なら `config.label_overrides` で吸収する。

### 5.2 persistent（周回をまたぐ）

```python
default persistent.op_seen = False
default persistent.endings_seen = set()   # {"misaki", "touka", "normal"}
default persistent.crt = True
```

- 既読管理は Ren'Py 標準のものを使う（`default preferences.skip_unseen = False`）。

### 5.3 ルート判定

```python
label decide_ending:
    if misaki_aff >= 3 and misaki_aff > touka_aff:
        jump end_misaki
    elif touka_aff >= 3 and touka_aff > misaki_aff:
        jump end_touka
    else:
        jump end_normal       # 同点・どちらも閾値未満
```

- 閾値と配点は §8 の選択肢表と一緒に調整する。**全エンディングに到達できること**をテスト項目にする（§11）。

---

## 6. キャラクター定義（characters.rpy）

| ID | 表示名 | 名前欄の色（プロトタイプの `#name.*`） | 立ち絵 |
|---|---|---|---|
| `y` | ユウキ | 緑 `#a8e6a0→#3f9a5a` | なし（主人公は立ち絵なし。プロトタイプと同じ） |
| `m` | ミサキ | ピンク `#ffa6cc→#e0508a` | あり |
| `t` | 冬華 | 水色 `#8fd6ff→#3a6ad0` | あり |
| `k` | 楓（新規・サブ） | 橙 | あり（表情4種） |
| `n` | （地の文） | なし | — |
| `q` | ？？？ | 灰 `#9aa6c8→#5a6488` | — |

```python
define y = Character("ユウキ", namebox_background=Frame("gui/namebox_yuki.png", 8, 8))
define m = Character("ミサキ",  image="misaki",   namebox_background=Frame("gui/namebox_misaki.png", 8, 8))
define t = Character("冬華",  image="touka", namebox_background=Frame("gui/namebox_touka.png", 8, 8))
define n = Character(None, what_italic=False)
# 正体が明かされる前の台詞用。表情タグは引き継ぐが、名前欄は灰色にする（ピンクだと正体がばれる）
define m_q = Character("？？？", image="misaki", kind=m, namebox_background=Frame("gui/namebox_unknown.png", 8, 8))
```

- `image=` を指定しておくと、`m happy "台詞"` の形で表情を切り替えながら喋らせられる（プロトタイプの `show` と `say` の組を1行にまとめられる）。

---

## 7. アセット設計

### 7.1 立ち絵（layeredimage）

プロトタイプの `charSVG` は、後ろ髪、体、顔、目、口、眉、頬染め、前髪、アクセサリの順に**パーツを重ねて**描いている。この構造を `layeredimage` にそのまま移す。

```python
layeredimage misaki:
    always "misaki_base_back"         # 後ろ髪＋体＋顔
    group eyes auto:
        attribute e_open default
        attribute e_happy
        attribute e_surprise
        attribute e_pout
    group mouth auto:
        attribute m_neutral default
        attribute m_smile
        attribute m_happy
        attribute m_surprise
        attribute m_pout
    group cheek:
        attribute no_blush default null
        attribute blush
    always "misaki_base_front"        # 前髪＋横の房＋リボン＋髪のハイライト
    group brows auto:              # 眉は前髪の上（プロトタイプと同じ）
        attribute b_normal default
        attribute b_up
        attribute b_angry
```

- **重ね順はプロトタイプの `charSVG` と同じにする**: 後ろ髪・体・顔 → 目・口・頬 → 前髪・横髪・アクセサリ・ハイライト → 眉。横髪（x≈146 まで）は目（x≈144 から）に重なっているので、base を1枚にまとめると目が横髪の上に描かれてしまう。base は必ず `back` と `front` の2枚に分ける。
- **表情は「プリセット属性」で書く**。脚本では `m happy` のように書き、目・口・眉・頬の組み合わせは `images.rpy` のエイリアスに集める。

  | 表情 | 目 | 口 | 眉 | 頬 | プロトタイプ |
  |---|---|---|---|---|---|
  | normal | open | neutral | normal | — | ✓ |
  | smile | open | smile | normal | — | ✓ |
  | happy | happy | happy | normal | blush | ✓ |
  | surprise | surprise | surprise | up | — | ✓ |
  | pout | pout | pout | angry | blush | ✓ |
  | blush | open | smile | normal | blush | ✓ |
  | cool（冬華） | open(細) | cool | normal | — | ✓ |
  | **sad**（新規） | open | neutral | 八の字 | — | |
  | **angry**（新規） | open | pout | angry | — | |
  | **closed**（新規） | 閉じ | smile | normal | — | |

  実装メモ: プリセットは `image misaki happy = LayeredImageProxy(...)` ではなく、`layeredimage` の `attribute` に `if_any` を組み合わせるか、`define config.adjust_attributes["misaki"]` で `happy` を `e_happy m_happy blush` に展開する。後者の方が脚本の表記が短い。
  **プリセットは必ず4グループ（目・口・眉・頬）すべてを指定する**（例: `smile` → `e_open m_smile b_normal no_blush`）。どれかを省くと、直前の表情の属性（`blush` など）が残ってしまう。

- **まばたき**: `e_open` を ATL の画像にして、プロトタイプの `blinkO/blinkC`（4.4秒周期）を再現する。周期に `renpy.random` で揺らぎを入れる。
  ```
  image misaki_eyes_open_anim:
      "misaki_e_open"
      choice: 3.2
      choice: 4.4
      choice: 5.0
      "misaki_e_closed"
      0.12
      repeat
  ```
- **呼吸**: `transform breath` で 3.6秒周期・2px の上下動（プロトタイプの `@keyframes breath`）。
- 立ち位置: Ren'Py 組み込みの `left / center / right` と名前が衝突しないよう、`pos_l / pos_c / pos_r` という `transform` を新たに定義する（`xanchor 0.0`、`xpos` 20/170/320。プロトタイプの `POS` と同じ値）。登場はプロトタイプの `sprIn` に合わせて dissolve＋下から10px。
- 書き出しサイズ: 1枚 300×450（プロトタイプと同じ。表示は 2 倍に拡大されても荒れないよう、書き出しは 600×900 で行い、Ren'Py 側で `zoom 0.5` する）。

### 7.2 背景

| ID | 内容 | 由来 |
|---|---|---|
| `bg black` | 黒 | 既存 |
| `bg slope` | 星見坂・朝 | 既存 `bgSlope('morning')` |
| `bg slope_sunset` | 星見坂・夕 | 既存 |
| `bg slope_night` | 星見坂・夜（街灯） | 新規 |
| `bg classroom` | 教室・昼 | 既存 `bgClass(false)` |
| `bg classroom_evening` | 教室・夕 | 既存 |
| `bg rooftop` | 屋上・夕 | 既存 `bgRoof()` |
| `bg rooftop_night` | 屋上・夜（望遠鏡） | 新規 |
| `bg night` | 夜空＋丘 | 既存 `bgNight()` |
| `bg hallway` | 廊下 | 新規 |
| `bg clubroom` | 天文部室（地学準備室） | 新規 |
| `bg home` | 主人公の部屋・夜 | 新規 |

- 桜の花びら（`bg slope*`／`bg classroom` に付ける）は Ren'Py の `SnowBlossom("images/fx/petal.png", count=16, xspeed=(-40,-20), yspeed=(80,140))` に置き換える。
- 流れ星（`bg night`）は ATL の画像 `fx_shoot` を背景の上に重ねる。
- CG: `cg misaki_end`／`cg touka_end`／`cg normal_end`（新規3枚）

### 7.3 BGM

| ID | 曲名 | 用途 | 由来 |
|---|---|---|---|
| `op` | 流れ星エチュード（歌入り風） | OP（ループなし30秒） | 既存 `SONGS.op` |
| `title` | 流れ星エチュード（オルゴール風） | タイトル・エピローグ | 既存 |
| `day` | 坂道ステップ | 日常（昼） | 既存 |
| `evening` | 夕凪メモリー | 放課後・夕方 | 新規 |
| `touka` | 冬華のテーマ（静かめ・三拍子） | 冬華の場面 | 新規 |
| `misaki` | ミサキのテーマ（明るいポップ） | ミサキの場面 | 新規 |
| `tension` | 胸さわぎ | 衝突・すれ違い | 新規 |

- チャンネル: Ren'Py 標準の `music`／`sound`／`voice`。SE を重ねるために `renpy.music.register_channel("sound2", "sfx", loop=False)` を足す。
- **BGM と SE の音量は Ren'Py の mixer で別々に調整できる**ので、プロトタイプの「単一 master＋ミュート」は廃止する。

### 7.4 SE

`hit`（衝突）、`select`（決定）、`cursor`（カーソル移動）、`door`、`chime`（学校のチャイム）、`footsteps`、`wind`、`shoot`（流れ星）、`page`（場面転換）、`heart`（好感度アップ演出用・任意）

### 7.5 素材生成パイプライン（tools/）

1. **画像**: プロトタイプの JS 関数（`charSVG`, `eye`, `mouth`, `brow`, `blush`, `bg*`）を Python に移す。SVG 文字列を組み立てる処理なので、ほぼ一対一で書き換えられる。
   - 立ち絵は**レイヤーごとに別の SVG を出力**する（base_back／base_front／eyes_*／mouth_*／brows_*／blush）。どれも同じ viewBox（0 0 400 600）にして、重ねたときに位置がずれないことを保証する。
   - `cairosvg.svg2png(bytestring, output_width=600, output_height=900)` で PNG にする。
   - 新規の背景・表情は Python 側に直接書き足す（プロトタイプには戻さない）。
2. **音**: `tone()` や `kick()` などを numpy で移し、`SONGS` を 44.1kHz のステレオ WAV にレンダリングして `ffmpeg -c:a libvorbis -q:a 5` で OGG にする。
   - ループ曲は1周ぶんを書き出し、ディレイの余韻が切れないように末尾の残響を先頭へ折り返す。Ren'Py のループで継ぎ目が出ないようにするため。
   - **方式は Python（numpy）移植に決定**。ブラウザでの書き出しは採用しない。
3. `make assets`（または `python tools/gen_images.py && python tools/render_audio.py`）で一括再生成できるようにする。

---

## 8. シナリオ構成（デモ版）

### 8.1 章立て

| label | 日付 | 内容 | 場所 | 主なBGM | 選択肢 |
|---|---|---|---|---|---|
| `prologue` | 4/8 朝 | 帰郷。坂でミサキと衝突・再会（プロトタイプ前半） | slope | day | — |
| `day1` | 4/8 | 教室で冬華と出会う。星降りの伝説 | classroom | day | — |
| `day1_after` | 4/8 放課後 | **選択①** ミサキと帰る／屋上へ | classroom_evening→ | evening | ① |
| `day2` | 4/9 | 天文部の廃部危機が明らかになる。サブキャラ楓が登場（ミサキの親友・新聞部） | hallway, clubroom | day/touka | ② |
| `day2_lunch` | 4/9 昼 | **選択②** 屋上で弁当（ミサキ）／部室の掃除（冬華） | rooftop/clubroom | misaki/touka | ② |
| `day3` | 4/10 | ミサキと冬華が初めてまともに話す。すれ違い | classroom | tension | ③ |
| `day3_night` | 4/10 夜 | **選択③** 夜の屋上で天体観測（冬華）／坂の上でミサキと話す。**選択④**はその場面での返答 | rooftop_night / slope_night | touka/misaki | ③④ |
| `decide_ending` | — | 好感度で分岐する | — | — | — |
| `end_*` | — | 予告エンド（CG1枚＋数行）→ 体験版終了カード | night ほか | title | — |

### 8.2 選択肢と配点

| # | 選択肢 | 効果 |
|---|---|---|
| ① | ミサキといっしょに帰る | `misaki_aff += 1`, `promised_misaki = True` |
|   | 屋上へ行ってみる | `touka_aff += 1`, `joined_astro = True` |
| ② | 屋上でミサキとお弁当 | `misaki_aff += 1` |
|   | 部室の掃除を手伝う | `touka_aff += 1`（`joined_astro` が False なら、ここで入部の流れになる） |
| ③ | 夜の屋上へ | `touka_aff += 1` |
|   | 坂のてっぺんへ | `misaki_aff += 1` |
| ④ | （③の先で、相手の悩みへの返答。2択） | 正解で該当ヒロインに `+1`、不正解で `±0` |

- 片方のヒロインを一貫して選び、④でも正解すると 4 点、閾値 3 以上でそのヒロインの END になる。選択が割れるとノーマルになる。
- プロトタイプの脚本（`SCRIPT` 配列）は `prologue`〜`day1_after` にほぼそのまま移す。加筆するのは day2 以降。

### 8.3 プロトタイプの命令と Ren'Py の対応

| プロトタイプ `SCRIPT` | Ren'Py |
|---|---|
| `{bg:'slope'}` | `scene bg slope with dissolve` |
| `{bgm:'day'}` | `play music day fadein 1.0` |
| `{narr:'…'}` | `n "…"`（または地の文として `"…"`） |
| `{say:'ミサキ',text:'…'}` | `m "…"` |
| `{show:'misaki',expr:'happy',pos:'center'}` | `show misaki happy at pos_c` |
| 表情＋台詞 | `m happy "…"` |
| `{hide:'all'}` | `scene` で一括、または `hide misaki` |
| `{fx:'shake'}` | `with hpunch`（または独自の `transform shake`）＋ `play sound hit` |
| `{choice:[…]}` | `menu:` ブロック（各項目の中で `$ misaki_aff += 1`） |
| `{label:'x'}` / `{jump:'x'}` | `label x:` / `jump x` |
| `{endcard:true}` | `call screen demo_end("misaki")` → `return` |

---

## 9. 演出設計

### 9.1 起動画面（splash.rpy）

- 黒背景に DotGothic16（緑 `#9fffb0`）で BIOS 風の行を1行ずつ表示する（`{cps=60}` と `{w=0.2}`）。
- 「― CLICK TO START ―」を点滅させる。クリックで OP へ。
- Web 版は出さないため、この画面はオーディオ解禁のためではなく**演出として**置く。`persistent.op_seen` が True の2回目以降はスキップする。

### 9.2 オープニング（op.rpy）

プロトタイプの OP は 128BPM・16小節・30秒で、12カットに分かれている。これを **Ren'Py の ATL とタイマーで再構成**する。

- 実装: `label op:` で `play music op noloop` を開始し、`call screen op_screen` に入る。
- `screen op_screen` に**カット表**を持たせる。
  ```python
  define OP_CUTS = [
      # (開始秒, 終了秒, displayable/ATL 名)
      (0.0,    1.875, "op_presents"),
      (1.875,  3.75,  "op_meteor"),
      (3.75,   7.5,   "op_logo"),
      (7.5,    9.375, "op_misaki_intro"),
      ...
      (26.25, 31.0,   "op_final_logo"),
  ]
  ```
- 再生位置は `renpy.music.get_pos("music")` で取り、`timer 0.016 repeat True` で画面を更新する。現在のカットを showif で切り替え、**曲と映像を同期**させる。曲を読めない場合は経過時間で代用する（プロトタイプの `opTime()` と同じ考え方）。
- カメラワーク（slam, inRight, zoomin, pan, bounce, pump, zoomout）はそれぞれ ATL の transform にする。キーフレームの値はプロトタイプの CSS `@keyframes` をそのまま移す（解像度が同じため）。
- フラッシュ: 各カットの頭で白い Solid を `alpha 0.95 → 0.0`（0.45秒）。
- カラオケ字幕: 2段交互。各行は「白縁の白文字」と「ピンクの文字」の2枚を重ね、ピンク側を ATL の `crop` で左から右へ広げる（`linear 歌唱秒数 crop (0,0,1.0,1.0)`、相対 crop）。歌詞と時刻は `LYR` 定義から計算する。
- 星空のキャンバスは、**事前に描いた星レイヤー（PNG）を2〜3枚**ゆっくりスクロールさせ、流星は ATL の画像を乱数の位置に出して再現する。`SnowBlossom` を流星に転用する案も可。
- スキップ: `key "dismiss"`、ESC、右上の「SKIP ▶▶」ボタンで `Return()`。
- **方式は ATL での再構成に決定**。動画化は採用しない。ただし同期ずれや重さで破綻した場合に備え、P7 で早めに試作して T6 を確認する。

### 9.3 本編の演出

| 演出 | 実装 |
|---|---|
| 背景切替 | `with dissolve`（0.7秒。プロトタイプの transition と同じ） |
| 場面転換（日付が変わる） | `with fade` と日付テロップ（`screen date_card("4月9日（火）")`） |
| 衝突 | `with hpunch` ＋ `play sound hit` |
| 好感度アップ | 画面の隅に小さな♪エフェクト（任意。設定で OFF にできる） |
| 予告END | CG ＋ `with Dissolve(1.5)` → 流れ星 → 終了カード |

---

## 10. 設定・システム

- Ren'Py 標準の preferences 画面を90年代風にスキンし直す。項目は次のとおり:
  - 画面モード（ウィンドウ／全画面）、文字速度、オート待ち時間、未読もスキップ、選択肢後もスキップ継続
  - BGM 音量、SE 音量、全ミュート
  - 走査線 ON/OFF（`persistent.crt`）
- セーブスロット: 1ページ6枠 × 5ページ＋オートセーブ／クイックセーブ。サムネイルは Ren'Py 標準のもの。
- ロールバック: 有効（ホイール上）。選択肢の取り消しも許可する（デモでは寛容にする）。
- `config.has_autosave = True`、章の頭で `$ renpy.force_autosave()`。

---

## 11. テスト・受け入れ基準

| # | 項目 | 方法 |
|---|---|---|
| T1 | `renpy lint` で警告ゼロ（未定義画像、未使用ラベル、日本語の文字化け） | CLI: `renpy.sh hoshimizaka lint` |
| T2 | 3エンディングすべてに到達できる | 選択肢の組み合わせ表（2×2×2×2=16通り）で机上確認したうえで、`testcase` スクリプトで自動化 |
| T3 | 各章の頭／選択肢の直前でセーブ → タイトル → ロードで同じ状態に戻る（背景・立ち絵・BGM・変数） | 手動 |
| T4 | 1周目のセーブを残したまま脚本を軽く修正しても、旧セーブを読み込める | 手動（配布後の互換確認） |
| T5 | 既読スキップが2周目で効き、未読で止まる | 手動 |
| T6 | OP の字幕・カットと曲が ±0.1秒以内で同期する（Win/Mac） | 目視＋ログ |
| T7 | BGM／SE の音量が別々に効く。ミュートが永続化する | 手動 |
| T8 | 640×480 の等倍・拡大・全画面で、文字が読めてレイアウトが崩れない | 手動 |
| T10 | 誤字脱字、表記揺れ（「ユウくん」等の呼称の統一） | 校正 |

---

## 12. 決定事項

2026-11-08 に確定:

1. **解像度**: 640×480。プロトタイプの座標をそのまま使う。
2. **絵**: 仮絵。プロトタイプの手続き SVG を Python でレイヤー書き出しした素材を、デモ版の素材として使う。製品版で差し替えられるよう、`layeredimage` の構造とファイル名の規則を固定する。
3. **楽曲の書き出し**: Python（numpy）に移植する。
4. **OP**: Ren'Py の ATL で再構成する。
5. **配布先**: Win/Mac/Linux のビルドのみ。Web 版は含めない。プロトタイプ `index.html` は `prototype/` へ移動して残す。
6. **楓**: 追加する（名前・設定は仮）。
7. **デモ版**: 配布用の体験版。店頭デモ（自動再生）は対象外。

## 13. 実装順序

| フェーズ | 内容 | 完了条件 |
|---|---|---|
| P0 | Ren'Py プロジェクトの作成、解像度・フォント・Character の設定 | 「Hello」が日本語で表示される |
| P1 | 素材パイプライン（画像）: 既存の背景7種と立ち絵2人のレイヤー書き出し | `show misaki happy at pos_c` が表示される |
| P2 | プロトタイプの脚本を `prologue`〜`day1_after` に移植。仮の BGM で動かす | プロトタイプと同じ内容を最後まで遊べる |
| P3 | 素材パイプライン（音）: 既存3曲と SE を OGG 化 | 本編で BGM と SE が鳴る |
| P4 | UI スキン（say／choice／main_menu／game_menu／quick_menu）、CRT オーバーレイ | 90年代風の見た目になる |
| P5 | day2〜day3 の脚本執筆、好感度、エンディング3種、終了カード | T2 が通る |
| P6 | 新規素材（背景5、表情3、楓、CG3、BGM4、SE） | 仮素材ゼロ |
| P7 | splash と OP | T6 が通る |
| P8 | おまけ（OP鑑賞・ENDリスト）、設定画面の仕上げ | — |
| P9 | テスト（§11）、ビルド（Win/Mac/Linux）、配布 | 全項目 OK |

---

## 14. 実装状況（2026-11-08 時点）

`hoshimizaka/` に Ren'Py 8.5.3 のプロジェクトとして実装済み。`renpy lint` は警告なし。

### 14.1 設計どおりに入ったもの

- 640×480 のプロジェクト、日本語 UI、90年代風ウィンドウ・名前欄（キャラ別の色）・CRT 走査線（設定で ON/OFF）
- layeredimage の立ち絵 3 人（ミサキ／冬華／楓）。後ろ側・前側の 2 枚＋目・口・頬・眉。表情は 10 種のプリセットを 4 グループへ展開
- 背景 12、CG 3、BGM 7、SE 10（すべて `tools/` で手続き生成）
- 起動画面（BIOS 風）→ 初回のみ OP → タイトル（はじめから／つづきから／オープニング／おまけ／設定／終了）
- OP は ATL で再構成（12 カット＋カラオケ字幕）。スキップはクリック／Enter
- 本編: プロローグ＋第1〜3日、選択肢 4 回、好感度による予告エンディング 3 種、体験版終了カード、おまけ（エンディング一覧）
- Ren'Py 標準のセーブ／ロード／ログ／オート／スキップ／ロールバック、BGM と SE の別音量
- `.rpyc` をコミットする運用（§5.1）、プロトタイプは `prototype/index.html` へ移動

### 14.2 設計と違うもの・足りないもの

| 項目 | 設計 | 実際 |
|---|---|---|
| 本文の量 | 約 700〜900 行、1 周 25〜35 分 | **約 150 ブロック（lint の台詞数）。1 周は十数分** |
| 冬華のテーマ曲 | 三拍子 | 四拍子（シーケンサが 1 小節=16 ステップ固定のため） |
| 表情 `cool`（冬華） | — | 通常表情の眉を `b_cool` にしている |
| サブキャラ楓 | 表情 4 種 | 立ち絵は 10 種のプリセットすべて使用可。出番は day2・day3・ノーマル END |
| 配布ビルド | Win/Mac/Linux | **未実施**（SDK のランチャーで「ビルド」） |
| 手動確認 | T4〜T8, T10 | **未確認**（旧セーブ互換・既読スキップ・OP 同期・拡大表示・誤字校正） |

### 14.3 自動テスト（`tools/run_tests.sh`）

テストケースごとに別プロセスで実行する（`testcases.rpy`）。

- `boot`: BIOS → OP（9 か所でスクリーンショット）→ タイトル
- `prologue_shots`: プロローグの立ち絵・会話ウィンドウ
- `route_misaki` / `route_touka` / `route_normal`: 3 エンディングに到達し、`persistent.endings_seen` を確認（T2）
- `ui_screens`: 設定・セーブ・ログ・おまけ画面
- `save_load`: 変数を保存→書き換え→ロードで復元（T3）
