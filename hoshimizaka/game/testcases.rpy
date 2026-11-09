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
