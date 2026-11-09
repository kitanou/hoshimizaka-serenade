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
