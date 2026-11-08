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
    advance until screen "demo_end"
    pause 2.5
    screenshot "t_end_misaki.png"
    assert eval ("misaki" in persistent.endings_seen)

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
    advance until screen "demo_end"
    pause 2.5
    screenshot "t_end_touka.png"
    assert eval ("touka" in persistent.endings_seen)

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
    advance until screen "demo_end"
    pause 2.5
    screenshot "t_end_normal.png"
    assert eval ("normal" in persistent.endings_seen)

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
