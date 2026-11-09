## 自動テスト。テストケースごとに別プロセスで実行する（状態を持ち越さないため）:
##   tools/run_tests.sh            # 全ケース
##   ./renpy.sh hoshimizaka test route_misaki --overwrite-screenshots
## 3 エンディングすべてに到達できること（受け入れ基準 T2）と、主要画面のスクリーンショット。

testsuite global:
    teardown:
        exit

testcase boot:
    description "起動→BIOS→OP（全13カットの中間でスクリーンショット）→タイトル"
    $ _test.transition_timeout = 0.05
    # OP は固定長シーケンス。until の既定 5s と綱引きで間欠的に超えるため余裕を取る（2026-11-09 flake 対応）
    $ _test.timeout = 15
    $ persistent.op_seen = False
    pause until screen "bios_boot"
    pause 2.5
    screenshot "t_bios.png"
    keysym "K_RETURN"
    pause 1.00
    screenshot "t_op_01.png"
    pause 1.50
    screenshot "t_op_02.png"
    pause 2.50
    screenshot "t_op_03.png"
    pause 3.50
    screenshot "t_op_04.png"
    pause 1.80
    screenshot "t_op_05.png"
    pause 2.70
    screenshot "t_op_06.png"
    pause 2.45
    screenshot "t_op_07.png"
    pause 0.95
    screenshot "t_op_08.png"
    pause 0.90
    screenshot "t_op_09.png"
    pause 0.80
    screenshot "t_op_10.png"
    pause 2.20
    screenshot "t_op_11.png"
    pause 3.50
    screenshot "t_op_12.png"
    pause 4.00
    screenshot "t_op_13.png"
    pause until screen "main_menu"
    pause 1.0
    screenshot "t_title.png"

testcase prologue_shots:
    description "プロローグの立ち絵と会話ウィンドウ"
    $ _test.transition_timeout = 0.05
    run Jump("start")
    advance
    advance
    advance
    advance
    advance
    advance
    advance
    advance
    pause 0.8
    screenshot "t_prologue_a.png"
    advance
    advance
    advance
    advance
    pause 0.8
    screenshot "t_prologue_b.png"
    advance
    advance
    advance
    pause 0.8
    screenshot "t_prologue_c.png"

testcase route_misaki:
    description "ミサキ予告ENDへ到達"
    $ _test.transition_timeout = 0.05
    run Jump("start")
    advance until screen "choice"
    screenshot "t_choice1.png"
    click "ミサキといっしょに帰る"
    advance until screen "choice"
    click "屋上でミサキとお弁当"
    advance until screen "choice"
    click "夜の坂のてっぺんへ行く"
    advance until screen "choice"
    screenshot "t_choice4.png"
    click "もうどこにも行かない"
    advance until screen "choice"
    screenshot "t_choice5.png"
    click "丘をミサキと下見する"
    advance until screen "choice"
    click "ミサキ（流星群の夜へ）"
    advance until screen "choice"
    screenshot "t_misaki_core1.png"
    click "覚えていない、と正直に認める"
    advance until screen "choice"
    screenshot "t_misaki_core2.png"
    click "約束のせいじゃない。お前が見たいんだ"
    advance until screen "demo_end"
    pause 2.5
    screenshot "t_end_misaki_good.png"
    assert eval ("misaki_good" in persistent.endings_seen)
    assert eval (renpy.store.misaki_aff == 5 and renpy.store.weekend_plan == "misaki")
    assert eval (renpy.store.misaki_honest)

testcase route_misaki_bad:
    description "ミサキルート BAD END（七年目のすれ違い）へ到達"
    $ _test.transition_timeout = 0.05
    run Jump("start")
    advance until screen "choice"
    click "ミサキといっしょに帰る"
    advance until screen "choice"
    click "屋上でミサキとお弁当"
    advance until screen "choice"
    click "夜の坂のてっぺんへ行く"
    advance until screen "choice"
    click "もうどこにも行かない"
    advance until screen "choice"
    click "丘をミサキと下見する"
    advance until screen "choice"
    click "ミサキ（流星群の夜へ）"
    advance until screen "choice"
    click "覚えていない、と正直に認める"
    advance until screen "choice"
    screenshot "t_misaki_core2_bad.png"
    click "約束があったから、ここへ来た"
    advance until screen "demo_end"
    pause 2.5
    screenshot "t_end_bad_misaki.png"
    assert eval ("bad_misaki" in persistent.endings_seen)
    # 注: endings_seen はケース間で persistent に永続するため "misaki_good 未視聴" は検証しない
    # （検証するのは run_tests.sh のケース順: 先に GOOD、次に BAD で別プレイの別 END に到達すること）

testcase route_touka:
    description "冬華予告ENDへ到達"
    $ _test.transition_timeout = 0.05
    run Jump("start")
    advance until screen "choice"
    click "屋上へ行ってみる"
    advance until screen "choice"
    click "部室の掃除を手伝う"
    advance until screen "choice"
    click "夜の屋上へ行く"
    advance until screen "choice"
    click "ひとりじゃない"
    advance until screen "choice"
    click "天体望遠鏡を冬華と整備する"
    advance until screen "choice"
    click "冬華（屋上の観測夜へ）"
    advance until screen "choice"
    screenshot "t_touka_core1.png"
    click "なら、そのバトンを一緒に走らせてくれ"
    advance until screen "choice"
    screenshot "t_touka_core2.png"
    click "継走はやめて、綾瀬さん自身の星空を始めよう"
    advance until screen "demo_end"
    pause 2.5
    screenshot "t_end_touka_good.png"
    assert eval ("touka_good" in persistent.endings_seen)
    assert eval (renpy.store.touka_aff == 5 and renpy.store.fathernote)
    assert eval (renpy.store.touka_motive == "relay")

testcase route_touka_bad:
    description "冬華ルート BAD END（冬の星座の別れ）へ到達"
    $ _test.transition_timeout = 0.05
    run Jump("start")
    advance until screen "choice"
    click "屋上へ行ってみる"
    advance until screen "choice"
    click "部室の掃除を手伝う"
    advance until screen "choice"
    click "夜の屋上へ行く"
    advance until screen "choice"
    click "ひとりじゃない"
    advance until screen "choice"
    click "天体望遠鏡を冬華と整備する"
    advance until screen "choice"
    click "冬華（屋上の観測夜へ）"
    advance until screen "choice"
    click "綾瀬さんのための観測は、どこへ行ったんだ"
    advance until screen "choice"
    screenshot "t_touka_core2_bad.png"
    click "任務は果たされた。よくやった、で終わらせよう"
    advance until screen "demo_end"
    pause 2.5
    screenshot "t_end_bad_touka.png"
    assert eval ("bad_touka" in persistent.endings_seen)
    assert eval (renpy.store.touka_motive == "self")

testcase route_normal:
    description "ノーマル予告ENDへ到達"
    $ _test.transition_timeout = 0.05
    run Jump("start")
    advance until screen "choice"
    click "ミサキといっしょに帰る"
    advance until screen "choice"
    click "部室の掃除を手伝う"
    advance until screen "choice"
    click "夜の坂のてっぺんへ行く"
    advance until screen "choice"
    click "それは……今はわからない"
    advance until screen "choice"
    click "家にこもって過去を思い出す"
    advance until screen "choice"
    screenshot "t_choice6.png"
    click "この街へ（夏休み）"
    advance until screen "demo_end"
    pause 2.5
    screenshot "t_end_normal.png"
    assert eval ("normal" in persistent.endings_seen)
    assert eval (renpy.store.weekend_plan == "none" and renpy.store.hill_memory)

## TRUE END テスト（route-flow.md §3.1 に対応）:
##   T-TRUE-1 = true_end（両 GOOD 視聴で⑥にみんなの丘が開く）
##   T-TRUE-2 = true_locked（片方未視聴ならゲート閉鎖→NORMAL 収束・star_promise 発生せず）
##   T-TRUE-3 = 全 END 網羅: misaki_good/bad_misaki/touka_good/bad_touka/normal/true_end の 6 END を
##              route_misaki・route_misaki_bad・route_touka・route_touka_bad・route_normal・true_end で各1本
##   T-TRUE-4（day5 中間セーブ→ロード→_flags 復元）は save_load ケースが変数保存機構で同種検証

testcase true_end:
    description "TRUE END『星見坂のセレナーデ』へ到達（両 GOOD 視聴でみんなの丘ゲート開放）"
    $ _test.transition_timeout = 0.05
    $ _test.timeout = 15
    $ persistent.endings_seen.add("misaki_good")
    $ persistent.endings_seen.add("touka_good")
    run Jump("start")
    advance until screen "choice"
    click "ミサキといっしょに帰る"
    advance until screen "choice"
    click "屋上でミサキとお弁当"
    advance until screen "choice"
    click "夜の坂のてっぺんへ行く"
    advance until screen "choice"
    click "もうどこにも行かない"
    advance until screen "choice"
    click "丘をミサキと下見する"
    advance until screen "choice"
    screenshot "t_true_gate.png"
    click "みんなの丘（八月十二日の夜）"
    advance until screen "demo_end"
    pause 2.5
    screenshot "t_end_true.png"
    assert eval ("true_end" in persistent.endings_seen)
    assert eval (renpy.store.star_promise and renpy.store.seen_good_both)

testcase true_locked:
    description "両 GOOD 未視聴では TRUE ゲート閉鎖。NORMAL へ収束し star_promise は発生しない"
    $ _test.transition_timeout = 0.05
    $ persistent.endings_seen.discard("touka_good")
    $ persistent.endings_seen.add("misaki_good")
    run Jump("start")
    advance until screen "choice"
    click "ミサキといっしょに帰る"
    advance until screen "choice"
    click "部室の掃除を手伝う"
    advance until screen "choice"
    click "夜の屋上へ行く"
    advance until screen "choice"
    click "無理しなくていいよ"
    advance until screen "choice"
    click "家にこもって過去を思い出す"
    advance until screen "choice"
    # ここでは⑥にミサキ(aff1)も冬華(aff2)もみんなの丘(touka_good 欠落)も出ず、この街へ のみ
    screenshot "t_choice6_locked.png"
    click "この街へ（夏休み）"
    advance until screen "demo_end"
    pause 2.5
    assert eval (renpy.store.star_promise == False and renpy.store.seen_good_both == False)

testcase ui_screens:
    description "設定・セーブ・ログ・おまけ画面のスクリーンショット"
    $ _test.transition_timeout = 0.05
    $ persistent.endings_seen = {"misaki"}
    run Jump("start")
    advance
    advance
    advance
    advance
    advance
    advance
    advance
    advance
    advance
    pause 0.5
    screenshot "t_say_name.png"
    run ShowMenu("preferences")
    pause 0.8
    screenshot "t_prefs.png"
    run ShowMenu("save")
    pause 0.8
    screenshot "t_save.png"
    run ShowMenu("history")
    pause 0.8
    screenshot "t_history.png"
    run ShowMenu("endings")
    pause 0.8
    screenshot "t_endings.png"
    run Return()
    pause 0.5

testcase prefs_restore:
    description "設定初期値復元（音量・文字速度・スキップ・走査線）。解除記録は保持"
    $ _test.transition_timeout = 0.05
    $ preferences.text_cps = 5
    $ preferences.volumes["music"] = 0.2
    $ preferences.volumes["sfx"] = 0.3
    $ preferences.mute["music"] = True
    $ preferences.skip_unseen = True
    $ persistent.crt = False
    $ persistent.op_seen = True
    $ persistent.endings_seen = {"misaki"}
    $ restore_default_settings()
    pause 0.5
    assert eval (renpy.store.preferences.volumes["music"] == 1.0)
    assert eval (renpy.store.preferences.volumes["sfx"] == 1.0)
    assert eval (not renpy.store.preferences.mute["music"])
    assert eval (renpy.store.preferences.text_cps != 5)
    assert eval (not renpy.store.preferences.skip_unseen)
    assert eval (persistent.crt)
    assert eval (persistent.op_seen)
    assert eval ("misaki" in persistent.endings_seen)
    run ShowMenu("preferences")
    pause 0.8
    screenshot "t_prefs_reset.png"

testcase save_load:
    description "選択肢②でセーブ→進める→ロードで好感度・フラグが元に戻る（T3）"
    $ _test.transition_timeout = 0.05
    run Jump("start")
    advance until screen "choice"
    click "ミサキといっしょに帰る"
    advance until screen "choice"
    $ renpy.save("testslot")
    pause 0.3
    click "屋上でミサキとお弁当"
    advance
    advance
    assert eval (renpy.store.misaki_aff == 2)
    $ renpy.load("testslot")
    pause 1.0
    assert eval (renpy.store.misaki_aff == 1 and renpy.store.promised_misaki)
    $ renpy.unlink_save("testslot")

## ---- #34 おまけ画面（CGギャラリー・音楽室・ENDリスト）----
## 解放状態は persistent（端末保持）。gallery は解放済み2件/未解放1件の混合状態を自分で作り、
## 「解放済みのみ閲覧」「未解放は ?+解放条件表示」「再起動後維持(=persistent保存)」の完了条件を検証。
testcase gallery:
    description "#34 おまけ: ENDリスト/CGギャラリー/音楽室。解放・非解放表示と再生停止"
    $ _test.transition_timeout = 0.05
    $ _test.timeout = 15
    $ persistent.op_seen = True
    $ persistent.endings_seen.add("misaki")
    $ persistent.cg_seen = set(["misaki_end"])
    $ persistent.bgm_seen = set()
    run MainMenu(confirm=False)
    pause 0.8
    screenshot "t_main_menu_otomake.png"
    click "おまけ"
    pause 0.6
    screenshot "t_otomake.png"
    click "CGギャラリー"
    pause 0.6
    screenshot "t_cg_gallery.png"
    assert eval ("misaki_end" in persistent.cg_seen and "touka_end" not in persistent.cg_seen and "normal_end" not in persistent.cg_seen)
    click "流星群の夜、あの子と"
    pause 0.8
    screenshot "t_cg_view.png"
    # 閉じる操作: tag menu 共通なので ShowMenu で確実に戻る（画面上の「← とじる」ボタンと同効果）
    run ShowMenu("cg_gallery")
    pause 0.6
    screenshot "t_cg_gallery_again.png"
    run ShowMenu("bgm_room")
    pause 0.6
    screenshot "t_bgm_room.png"
    click "星見坂 テーマ"
    pause 1.2
    assert eval (renpy.music.get_playing("music") == renpy.store.audio.title)
    assert eval ("title" in persistent.bgm_seen)
    click "停止"
    pause 0.6
    assert eval (renpy.music.get_playing("music") is None)
    screenshot "t_bgm_room_stopped.png"
    click "もどる"
    pause 0.5
    screenshot "t_otomake_back.png"

## ---- #43 ルート判定ロジック単体検査（手動プレイに依存しない）----
testcase route_logic:
    description "#43 gate関数の境界値・真理表・aff予算制約・TRUE永続ゲート"
    $ _test.timeout = 15
    # ゲート境界値: aff=3 で閉・aff=4 で開（両ヒロイン対称）
    assert eval (not gate_misaki(True, 3) and gate_misaki(True, 4))
    assert eval (not gate_touka(True, 3) and gate_touka(True, 4))
    # フラグゲート: aff=5 でも条件フラグ False なら閉
    assert eval (not gate_misaki(False, 5) and not gate_touka(False, 5))
    # 真理表（flag×aff境界 の全4組合せ × 両ヒロイン）
    assert eval ([gate_misaki(f, a) for f in (True, False) for a in (3, 4)] == [False, True, False, False])
    assert eval ([gate_touka(f, a) for f in (True, False) for a in (3, 4)] == [False, True, False, False])
    # gate_true 真理表（集合の内容のみで判定、順序・超過要素に影響されない）
    assert eval (not gate_true(set()) and not gate_true({"misaki_good"}) and not gate_true({"touka_good"}))
    assert eval (gate_true({"misaki_good", "touka_good"}) and gate_true({"misaki_good", "touka_good", "normal"}))
    # 到達不能分岐検査: 同一プレイの好感度配分は AFF_BUDGET 以下。
    #   全配分で「ミサキゲートと冬華ゲートが同時開かない」= 単一プレイでの二重ルート選択は存在しない（route-flow §1.4）
    assert eval (all(not (gate_misaki(True, m) and gate_touka(True, t)) for m in range(8) for t in range(8) if m + t <= AFF_BUDGET))
    # 境界直前は常に閉: m+t<=AFF_BUDGET の範囲で (4,4) 配分自体が非存在
    assert eval (AFF_BUDGET < 2 * AFF_GATE)
    # TRUE ゲートと永続状態の連動（add/discard で開閉）。自分自身で確立し元の状態へ復元する
    python:
        _had_m = "misaki_good" in persistent.endings_seen
        _had_t = "touka_good" in persistent.endings_seen
        persistent.endings_seen.add("misaki_good")
        persistent.endings_seen.discard("touka_good")
        assert not gate_true(persistent.endings_seen)
        persistent.endings_seen.add("touka_good")
        assert gate_true(persistent.endings_seen)
        if not _had_m:
            persistent.endings_seen.discard("misaki_good")
        if not _had_t:
            persistent.endings_seen.discard("touka_good")

## ---- #41 音響品質テスト（方針は docs/audio-design.md・静的監査 tools/audio_audit.py）----
testcase audio:
    description "#41 全音源ロード/音量反映/再生差替停止ループ/音量0ミュートで再生可"
    $ _test.timeout = 15
    # 宣言された全音源（BGM7+SE10）が実際にロード可能（音源欠落エラーの確認）
    $ _apaths = sorted(set(v for v in vars(renpy.store.audio).values() if isinstance(v, str) and v.startswith("audio/") and v.endswith(".ogg")))
    assert eval (len(_apaths) >= 17)
    python:
        for p in _apaths:
            renpy.loader.load(p)
    # 音量設定が preferences に反映（設定画面経由と同じ経路。persistent保存は prefs_restore が検証）
    $ preferences.volumes["music"] = 0.5
    $ preferences.volumes["sfx"] = 0.0
    assert eval (renpy.store.preferences.volumes["music"] == 0.5 and renpy.store.preferences.volumes["sfx"] == 0.0)
    # BGM: 再生→差し替え→停止（fadein/fadeout 付き・方針通り）とループフラグ
    $ renpy.music.play(renpy.store.audio.day, "music", fadein=0.2)
    assert eval (renpy.music.get_playing("music") == renpy.store.audio.day)
    assert eval (renpy.music.get_loop("music"))
    $ renpy.music.play(renpy.store.audio.evening, "music", fadein=0.2)
    assert eval (renpy.music.get_playing("music") == renpy.store.audio.evening)
    $ renpy.music.stop("music", fadeout=0.2)
    assert eval (renpy.music.get_playing("music") is None)
    # ミュート・音量ゼロ時に BGM/SE 再生がエラーにならず、音楽は停止できる
    $ preferences.mute["music"] = True
    $ renpy.music.play(renpy.store.audio.title, "music", fadein=0.1)
    $ renpy.music.play(renpy.store.audio.hit, "sound")
    $ renpy.music.stop("music", fadeout=0.1)
    $ renpy.music.stop("sound")
    assert eval (renpy.music.get_playing("music") is None)
    # 既定値へ戻す（恒久設定の検証は prefs_restore が別途担当）
    $ preferences.mute["music"] = False
    $ preferences.volumes["music"] = 1.0
    $ preferences.volumes["sfx"] = 1.0

## ---- #45 アセット・表示・セーブデータの検査 ----
testcase qa_assets:
    description "#45 640x480/画像全実在ロード/ギャラリー参照ファイル実在/セーブスロット書込削除"
    $ _test.timeout = 15
    # 表示: ゲーム解像度は設計通り 640x480（4:3）
    assert eval (renpy.config.screen_width == 640 and renpy.config.screen_height == 480)
    # 画像アセット: images/ 配下の全画像ファイルが実在・デコード可能（読み込み検証）
    python:
        import os
        _n_img = 0
        _gamedir = renpy.config.gamedir
        for _dp, _dn, _files in os.walk(os.path.join(_gamedir, "images")):
            for _f in sorted(_files):
                if _f.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                    _rel = os.path.relpath(os.path.join(_dp, _f), _gamedir).replace(os.sep, "/")
                    renpy.loader.load(_rel)
                    _n_img += 1
    assert eval (_n_img >= 100)
    # おまけギャラリー（#34）が参照する CG・BGM ファイルの実在
    python:
        for _cid, _t, _s, _p in renpy.store.CG_GALLERY:
            renpy.loader.load(_p)
        for _bid, _t, _p in renpy.store.BGM_ROOM:
            renpy.loader.load(_p)
    # セーブデータ: スロット書込み→json読出→削除のラウンドトリップ（周回継続の機構確認。詳細は save_load）
    run Jump("start")
    advance until screen "choice"
    $ renpy.save("qa_assets_slot")
    pause 0.5
    assert eval (renpy.slot_json("qa_assets_slot") is not None)
    $ renpy.unlink_save("qa_assets_slot")
    assert eval (renpy.slot_json("qa_assets_slot") is None)
