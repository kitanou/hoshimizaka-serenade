# 星見坂のセレナーデ (Hoshimizaka Serenade)

90年代PC-98/サターン期の美少女ノベルゲーム風ゲーム。Ren'Py 8.x（Python）で作る体験版（ver.0.97）。

- 設計書: [docs/demo-design.md](docs/demo-design.md)
- `prototype/index.html` … ブラウザで動く最初のプロトタイプ（ver.0.96。OP・脚本・配色の仕様元）
- `hoshimizaka/` … Ren'Py プロジェクト（本体）
- `tools/` … 画像・音の生成ツール（Python）

## 遊ぶ

[Ren'Py SDK 8.5.x](https://www.renpy.org/latest.html) を入れて、`hoshimizaka` フォルダをランチャーで開く（またはコマンドで実行）。

```bash
~/renpy-sdk/renpy.sh hoshimizaka
```

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
tools/run_tests.sh            # 起動・OP・3ルート・UI・セーブ/ロード（テストケースごとに別プロセス）
~/renpy-sdk/renpy.sh hoshimizaka lint
```

## ライセンス・素材

- 日本語フォントは Ren'Py SDK 同梱の Source Han Sans Lite（SIL OFL）。
- 立ち絵・背景・音楽はすべて本リポジトリのツールによる手続き生成（仮素材）。
