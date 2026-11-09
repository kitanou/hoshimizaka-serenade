## 追加画面: タイトルロゴ、ボタン、CRT、起動画面、おまけ、体験版終了カード

define ENDING_LIST = [
    ("misaki", "ミサキ 予告END", "夜の坂道で、あの子と約束を。"),
    ("misaki_good", "MISAKI END『約束の答え』", "七年目の約束に、返事を書いた。"),
    ("bad_misaki", "MISAKI BAD END『七年目のすれ違い』", "流星の尾が、二人の間を横切った。"),
    ("touka", "冬華 予告END", "屋上の望遠鏡のそばで。"),
    ("touka_good", "TOUKA END『二人の観測』", "署名欄に、二人分の名前を書いた。"),
    ("bad_touka", "TOUKA BAD END『冬の星座の別れ』", "望遠鏡は町の保管庫へ。任務了。"),
    ("normal", "NORMAL END", "八月十二日、全員で見上げる星空。"),
    ("true_end", "TRUE END『星見坂のセレナーデ』", "両 GOOD END を視聴し、8/12 の夜に『みんなの丘』を選ぶ。"),
]

## ---- CRT 走査線 ----
screen crt_overlay():
    zorder 200
    if persistent.crt:
        add Transform("gui/crt.png", zoom=0.5)

init python:
    config.overlay_screens.append("crt_overlay")

## ---- ロゴ ----
screen title_logo(y=54):
    vbox:
        xalign 0.5
        ypos y
        spacing 4

        text "星見坂{size=34}の{/size}セレナーデ":
            size 50
            bold True
            color "#ffe1f0"
            xalign 0.5
            outlines [(4, "#2a0f5c", 0, 0), (4, "#ff2f86", 4, 4)]
        text "HOSHIMIZAKA SERENADE":
            size 16
            italic True
            color "#7fe3ff"
            xalign 0.5
            outlines [(2, "#1a1050", 1, 1)]
        frame:
            xalign 0.5
            background Solid("#ff5fa2")
            padding (12, 2)
            text "体験版" size 12 color "#ffffff"

## ---- タイトルのボタン ----
style mbtn_button:
    xsize 190
    ysize 28
    xalign 0.5
    background Frame("gui/button/choice_idle_background.png", 10, 6, 10, 6)
    hover_background Frame("gui/button/choice_hover_background.png", 10, 6, 10, 6)
    insensitive_background Frame("gui/button/choice_idle_background.png", 10, 6, 10, 6)

style mbtn_button_text:
    xalign 0.5
    yalign 0.5
    size 15
    color "#ffffff"
    hover_color "#ffffff"
    insensitive_color "#8088aa"
    outlines [(1, "#000000", 1, 1)]

## ---- 起動画面（BIOS 風） ----
transform bios_line(d):
    alpha 0.0
    pause d
    alpha 1.0

transform blink_text:
    alpha 1.0
    pause 0.5
    alpha 0.0
    pause 0.5
    repeat

screen bios_boot():
    modal True
    add Solid("#000000")
    vbox:
        xpos 34
        ypos 28
        spacing 2
        text "STARDUST-BIOS Ver 1.96" size 14 color "#9fffb0" font "fonts/SourceHanSansLite.ttf" at bios_line(0.1)
        text "(C) 1996 星屑工房 SYSTEM" size 14 color "#5fa070" at bios_line(0.3)
        null height 12
        text "MEMORY CHECK ....... 640KB OK" size 14 color "#9fffb0" at bios_line(0.7)
        text "FM SOUND BOARD ..... OK" size 14 color "#9fffb0" at bios_line(1.1)
        text "GRAPHIC 640x480 .... 256 COLORS" size 14 color "#9fffb0" at bios_line(1.5)
        text "LOADING \"HOSHIMI.EXE\" ..." size 14 color "#9fffb0" at bios_line(1.9)
    text "― CLICK TO START ―" xalign 0.5 ypos 340 size 22 color "#ffffff" at blink_text
    text "音が出ます（OP 約30秒・スキップ可）" xalign 0.5 ypos 392 size 12 color "#8a8fb0"
    button:
        xysize (640, 480)
        action Return()
    key "dismiss" action Return()
    use crt_overlay

## ---- おまけ: エンディングリスト ----
screen endings():
    tag menu
    use game_menu("おまけ", scroll="viewport"):
        vbox:
            spacing 10
            label "エンディング"
            for eid, title, hint in ENDING_LIST:
                if eid in persistent.endings_seen:
                    text "◆ [title]" color "#ffe27a"
                else:
                    text "◇ ？？？　（[hint]）" color "#8088aa"
            null height 8
            textbutton "オープニングを見る" action Replay("op")

## ---- 体験版終了カード ----
screen demo_end(eid):
    modal True
    add Solid("#05061ac8")
    vbox:
        xalign 0.5
        yalign 0.5
        spacing 12
        text "体験版はここまでです" size 32 bold True color "#ffffff" xalign 0.5 outlines [(2, "#ff2f86", 3, 3)]
        text "～ to be continued ～" size 18 italic True color "#7fe3ff" xalign 0.5
        frame:
            xalign 0.5
            background None
            padding (14, 4)
            text "1996年 冬 発売予定!?" size 15 color "#ffe27a"
        python:
            _t = [t for e, t, h in ENDING_LIST if e == eid]
        if _t:
            text "― [_t[0]] ―" size 14 color "#cfe0ff" xalign 0.5
        null height 12
        text "クリックでタイトルへ" size 12 color "#aaaabb" xalign 0.5 at blink_text
    button:
        xysize (640, 480)
        action Return()
    key "dismiss" action Return()

## 名前欄の文字: 背景が色付きなので白＋黒フチにする
style say_label:
    color "#ffffff"
    outlines [(1, "#000000", 1, 1)]
