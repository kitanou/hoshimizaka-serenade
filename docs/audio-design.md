# 音響設計方針（#41）

## 1. 共通音響方針（音量の一元化）

- **音量は Ren'Py 標準のミキサー（music / sound / voice）と 設定画面(`screens.rpy` の preferences)だけで制御する。** 脚本・ルート内から `preferences.volumes` を直接操作しない（監査 `tools/audio_audit.py` が機械的に検査。許可例外: screens.rpy / testcases.rpy）。
- BGM・SE とも宣言は `audio.rpy` の `audio.*` のみ。脚本は必ず `audio.<name>` 経由で参照する（素のファイルパス直指定禁止）。

## 2. フェード方針

| 命令 | 規定 |
|---|---|
| `play music` | `fadein` 付きで開始。例外は OP 冒頭 `play music audio.op noloop` の1箇所のみ（ゲーム起動同時開始でフェード inception 不要。監査に例外登録済み） |
| `stop music` | `fadeout` 付き（音切れ防止） |
| `play sound` | 効果音は素再生可（SE は短尺でフェード不要） |
| 曲の切り替え | `play music A` の連続で自動クロスフェードに頼らず、明示 fadein/fadeout を書く |

- BGM ループは Ren'Py 既定（`loop=True`）に任せる。非ループは OP のみ（`noloop`）。
- ミュートは 設定画面のチェック（`preferences.mute`）でのみ行い、脚本側で音量 0 を書き換えて黙らせる実装をしない。

## 3. 音量の永続化

- preferences（音量・ミュート）は Ren'Py が persistent へ自動保存 → 再起動後も復元。
- 「初期値へ戻す」は `restore_default_settings()`（persistent 側の解除記録〔endings_seen / cg_seen / bgm_seen / op_seen 等〕は保持する）→ テスト `prefs_restore` が検証。

## 4. テスト・監査

- `tools/audio_audit.py`（静的・run_tests.sh が suite 前に実行）: fadein/fadeout 方針、音量操作の一元化、`audio.*` 宣言ファイルの実在。
- testcase `audio`（動的）: 全宣言音源のロード可否、音量設定の反映、再生→差し替え→停止とループフラグ、音量0・ミュートで SE/BGM 再生がエラーにならないこと。
- testcase `qa_assets`（動的）: 640×480 表示設定、画像アセット全実在、CG_GALLERY / BGM_ROOM エントリ参照ファイルの実在、セーブスロット書込み削除。

## 5. OP の音響追加（#80 / #83・2026-11-09）

- **主題歌ボーカル（#83）**: 主題歌「流れ星エチュード」はフォルマント合成の女性ボーカルが歌う（`tools/music/voice.py`）。
  声門パルス（加算調波・女性声道フォルマント 3 共振・母音 a/i/u/e/o/撥音）に子音付与（破裂/摩擦/鼻声/グライド）。
  1 音符 = モーラ列で、割当表は `tools/music/songs.py OP_SYL`（歌詞の全モーラを発話）。
  タイミングはメロディ事象と同一（＝ op.rpy の歌詞字幕 OP_LYRICS と完全同期）。
  伴奏の square リードは歌唱中のみ 0.55 音量に下げてコーラス風ダブリングとして共存。
  検証: 孤立ボーカル 70 音符のピッチ追跡（HPS）で中央値 7.9 cents（7.9¢）の精度。
- **OP 効果音 3 点（#80）**: CUT02=shoot（流星）/ CUT06=wind（風）/ CUT12=chime（流星群）。
  `renpy.sound.play` で sfx mixer 経由（音量は設定画面のみで操作する方針は維持）。
  当初案の CUT11 hit は不入 — 18.75s（11 小節目頭）は原曲の crash 位置と重なり低音が二重になるため。
- **曲尺の実体一致（#80）**: 非ループ曲（op）は作曲尺 30.0s で実体終了＋終端 0.4s 実体フェード
  （`tools/render_audio.py` の trim。旧はシンセの余韻 +1.5s 残り 31.5s だった。絵コンテ §9 対応）。
  これに伴い op.rpy の `stop music fadeout` は 30.0s 到達後（実体曲末端と一致する no-op 相当）。
- **タイトル BGM（#80）**: `config.main_menu_music = Transform(audio.title, fadein=1.0)`。OP 終了直後の無音からの急出現を解消。
- **監査**: `play music` の fadein 例外は OP 冒頭 noloop 1 件のまま（#83/#80 で変更なし）。
  ボーカルは BGM 生成側（tools/music）の実装で、脚本の音量直呼びは増加させていない（監査適合）。
