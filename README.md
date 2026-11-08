# 星見坂のセレナーデ (Hoshimizaka Serenade)

90年代PC-98/サターン期の美少女ノベルゲーム風ゲーム。Ren'Py 8.x（Python）で作る体験版（ver.0.97）。

- 設計書: [docs/demo-design.md](docs/demo-design.md)（体験版 ver.0.97 の詳細設計）
- 製品版仕様ドラフト: [docs/story-bible.md](docs/story-bible.md)（設定集） / [docs/route-flow.md](docs/route-flow.md)（分岐・ルート・TRUE END 条件案）
- OP 絵コンテ: [docs/op-storyboard.md](docs/op-storyboard.md)
- `prototype/index.html` … ブラウザで動く最初のプロトタイプ（ver.0.96。OP・脚本・配色の仕様元）
- `hoshimizaka/` … Ren'Py プロジェクト（本体）
- `tools/` … 画像・音の生成ツール（Python）

## 遊ぶ

### 1. 準備（初回のみ）

1. このリポジトリを取得する。
   ```bash
   git clone https://github.com/kitanou/hoshimizaka-serenade.git
   cd hoshimizaka-serenade
   ```
2. [Ren'Py SDK 8.5.x](https://www.renpy.org/latest.html) をダウンロードして展開する（インストーラーは不要。例: `~/renpy-sdk`）。
   Python や素材生成ツールは、遊ぶだけなら不要。

### 2. 起動する

**ランチャーから**（Windows / macOS / Linux 共通）

1. SDK の `renpy.exe`（Windows）／ `renpy.app`（macOS）／ `renpy.sh`（Linux）でランチャーを開く。
2. 「Preferences」→「Projects Directory」でこのリポジトリのフォルダを指定する（または「Add Project」）。
3. 一覧の `hoshimizaka` を選び、「Launch Project」を押す。

**コマンドから**

```bash
# macOS / Linux
~/renpy-sdk/renpy.sh hoshimizaka
```

```bat
:: Windows（SDK のフォルダで）
renpy.exe C:\path\to\hoshimizaka-serenade\hoshimizaka
```

### 3. 遊び方

- 最初に BIOS 風の画面が出る。クリックか Enter で進むと、初回だけオープニング（約30秒。クリックか Enter でスキップ）が流れる。
- タイトルで「はじめから」を選ぶ。
- クリック / Enter / Space で文送り。右クリック / Esc でメニュー（セーブ・ロード・設定・タイトルへ）。
- マウスホイール上 / PageUp で一つ前に戻る（ロールバック）、`H` でログ、Ctrl 押しっぱなしでスキップ、`A` でオート。
- 設定画面で文字速度、BGM / SE の音量、走査線の ON/OFF を変えられる。

内部解像度は 640×480。収録は 4/8〜4/10 の3日間、選択肢4回、エンディング3種（予告）。

## 素材を作り直す

画像・音は `tools/` から生成して `hoshimizaka/game/` に書き出す（生成物はコミット済み。ふだんは不要）。

```bash
python3.12 -m venv ~/hoshimizaka-venv && ~/hoshimizaka-venv/bin/pip install -r tools/requirements.txt
brew install cairo   # cairosvg に必要（macOS）
DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib ~/hoshimizaka-venv/bin/python -m tools.gen_images
~/hoshimizaka-venv/bin/python -m tools.render_audio
~/hoshimizaka-venv/bin/python -m tools.gen_rpy     # images.rpy を再生成
```

## テスト

```bash
tools/run_tests.sh            # 起動・OP・3ルート・UI・設定復元・セーブ/ロード（テストケースごとに別プロセス）
~/renpy-sdk/renpy.sh hoshimizaka lint
```

## ビルド（配布）

macOS / Windows / Linux 向けの配布 zip を作る。Ren'Py SDK の pasteboard（各 OS 用ランタイム）を初めてダウンロードするため、ネットワークが必要。配布バージョンは `options.rpy` の `config.version` から付く。

**macOS / Linux**（mac の実機で実行した場合。Windows では `renpy.py launcher distribute` を使う）

```bash
cd ~/renpy-sdk
./renpy.sh launcher distribute /path/to/hoshimizaka-serenade/hoshimizaka \
    --destination /path/to/hoshimizaka-serenade/hoshimizaka/dists
```

**Windows**（SDK フォルダで）

```bat
lib\py3-windows-x86_64\python.exe renpy.py launcher distribute C:\path\to\hoshimizaka-serenade\hoshimizaka --destination C:\path\to\hoshimizaka-serenade\hoshimizaka\dists
```

生成物（2026-11-08, Ren'Py 8.5.3 で実測）と検証状況:

| ファイル | 内容 | 検証 |
|---|---|---|
| `HoshimizakaSerenade-0.97-mac.zip` | macOS 版（.app） | ✅ 解凍→起動→自動テスト `route_misaki` PASSED（実機・mac） |
| `HoshimizakaSerenade-0.97-win.zip` | Windows 版 | ⏳ パッケージ内容確認のみ（実機確認は Windows 環境で） |
| `HoshimizakaSerenade-0.97-linux.tar.bz2` | Linux 版 | ⏳ パッケージ内容確認のみ |
| `HoshimizakaSerenade-0.97-pc.zip` | 3 OS 同梱（配布向け） | 中身は win/mac/linux と同一 |
| `HoshimizakaSerenade-0.97-market.zip` | Android 向け | 本作品の配布対象外 |

- 生成された `dists/` はコミットしない（`.gitignore` 済み）。リリース時に各 OS 版 zip を GitHub Release 等に添付する
- 配布物には `.rpy` と `.rpyc` の両方が含まれる（旧セーブ互換のため label 改名禁止。docs/demo-design.md §5.1）

## ライセンス・素材

- 日本語フォントは Ren'Py SDK 同梱の Source Han Sans Lite（SIL OFL）。
- ミサキの立ち絵は `docs/images/character-misaki.webp`（参考画像）から表情6種のバストアップを切り出したもの（`python -m tools.import_misaki`）。
- 冬華・楓の立ち絵と本編背景は ComfyUI 生成（手順は [docs/image-generation.md](docs/image-generation.md) / [docs/background-art-spec.md](docs/background-art-spec.md)）。イベント CG と音楽は本リポジトリのツールによる手続き生成（仮素材）。
