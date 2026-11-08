## オープニング（約30秒）。index.html の OP を ATL とタイマーで再構成。
## 曲 audio/bgm/op.ogg（128BPM・16小節）に合わせて、各カットの開始秒で場面を切り替える。
## 時刻は音楽の再生開始を 0 秒とした経過時間（op_t0）で管理する。

default op_t0 = 0.0
default op_flash_n = 0

init python:
    import time as _time

    ## 歌詞（text, 歌い始め[秒], 歌唱の長さ[秒]）。歌い始め = (2+2i) 小節 × 1.875 秒
    OP_BAR = 60.0 / 128 * 4
    OP_LYRICS = [
        ("坂道のむこう　流れ星ひとつ", 2 * OP_BAR, 3.516),
        ("キミの名前を　夜空に呼んだ", 4 * OP_BAR, 3.516),
        ("ときめくハートは　秘密のメロディ", 6 * OP_BAR, 3.75),
        ("制服のまま　明日へ駆けだそう", 8 * OP_BAR, 3.75),
        ("Shooting Star!　願いをのせて", 10 * OP_BAR, 3.75),
        ("この想い　ずっと　輝いて", 12 * OP_BAR, 3.75),
    ]

    def op_wait(t):
        """OP開始から t 秒になるまで待つ。クリック/Enterで中断されたら True。"""
        d = t - (_time.time() - store.op_t0)
        if d <= 0:
            return False
        return bool(renpy.pause(d))

    def op_flash():
        store.op_flash_n += 1
        renpy.show_screen("op_flash", _tag="opflash%d" % store.op_flash_n)

    def op_lyric(i):
        """歌詞 i 行目を表示する。段は偶数/奇数で交互。前に同じ段にいた行は消す。"""
        text, start, dur = OP_LYRICS[i]
        appear = _time.time() - store.op_t0
        delay = max(0.0, start - appear)
        if i >= 2:
            renpy.hide_screen("oplyr%d" % (i - 2))
        renpy.show_screen("op_lyric", i % 2, text, delay, dur, _tag="oplyr%d" % i)

    def op_clear():
        for i in range(len(OP_LYRICS)):
            renpy.hide_screen("oplyr%d" % i)
        for n in range(1, store.op_flash_n + 1):
            renpy.hide_screen("opflash%d" % n)
        renpy.hide_screen("op_whiteout")
        renpy.hide_screen("op_ui")

## ---------------------------------------------------------------- 変換

transform at_xy(x, y):
    pos (x, y)

transform at_top_center(x, y):
    anchor (0.5, 0.0)
    pos (x, y)

transform lyric_wipe(delay, dur):
    crop_relative True
    crop (0.0, 0.0, 0.001, 1.0)
    pause delay
    linear dur crop (0.0, 0.0, 1.0, 1.0)

transform flash_fade:
    alpha 0.95
    linear 0.45 alpha 0.0

transform whiteout_fade:
    alpha 0.0
    linear 0.8 alpha 1.0

transform op_stripes_scroll:
    xpos -96 ypos 0
    linear 1.0 xpos 0
    repeat

transform op_misaki_intro:
    anchor (0.0, 0.0) pos (250, 40) zoom 1.1333 xoffset 320
    ease 0.55 xoffset 0

transform op_face_zoom:
    anchor (0.5, 0.3) pos (320, 250) zoom 2.7
    ease 0.9 zoom 2.4

transform op_eye_zoom:
    anchor (0.5, 0.351) pos (320, 280) zoom 6.6
    ease 1.8 zoom 5.9

transform op_roof_pan:
    anchor (0.5, 0.5) pos (320, 270) zoom 1.18
    linear 3.75 ypos 210

transform op_touka_rise:
    anchor (0.0, 0.0) pos (60, 90) zoom 1.2
    ease 3.5 ypos 30

transform op_slope_pan:
    anchor (0.5, 0.5) pos (350, 240) zoom 1.2
    linear 0.94 xpos 290

transform op_zoomout:
    anchor (0.5, 0.5) pos (320, 240) zoom 1.35
    ease 3.75 zoom 1.0

transform op_wind(delay, w):
    xpos 700 alpha 0.9
    pause delay
    linear 1.1 xpos -w
    repeat

transform op_sil_in(x):
    anchor (0.0, 0.0) pos (x, 90) zoom 0.86 xoffset 320 matrixcolor BrightnessMatrix(-1.0)
    ease 0.4 xoffset 0

transform op_bounce(x, delay):
    pos (x, 50) zoom 1.0 yoffset 300
    pause delay
    ease 0.6 yoffset 0

transform op_pump:
    zoom 1.03
    linear 0.4687 zoom 1.0
    repeat

transform op_spin:
    anchor (0.5, 0.5) pos (160, 80) rotate 0
    linear 9.0 rotate 360
    repeat

transform op_twinkle(delay=0.0):
    anchor (0.5, 0.5) zoom 0.3 alpha 0.3 rotate 0
    pause delay
    block:
        parallel:
            linear 0.6 zoom 1.0 alpha 1.0 rotate 22
            linear 0.6 zoom 0.3 alpha 0.3 rotate 45
        repeat

transform op_slide_r:
    xoffset -30 alpha 0.0
    pause 0.4
    ease 0.6 xoffset 0 alpha 1.0

transform op_drop_in:
    yoffset -120 alpha 0.0
    pause 0.2
    ease 0.5 yoffset 0 alpha 1.0

transform op_slam:
    anchor (0.5, 0.5) zoom 3.2 alpha 0.0
    parallel:
        linear 0.2 alpha 1.0
    parallel:
        ease 0.55 zoom 1.0

transform op_pop(delay):
    zoom 0.0
    pause delay
    ease 0.3 zoom 1.2
    linear 0.1 zoom 1.0

transform op_credits:
    alpha 0.0
    pause 0.5
    linear 0.9 alpha 1.0

transform op_silhouette:
    matrixcolor BrightnessMatrix(-1.0)

## ---------------------------------------------------------------- 画像

image op_stars:
    "images/fx/stars1.png"
    ypos 0
    linear 40 ypos -480
    repeat

image op_stars_far:
    "images/fx/stars2.png"
    ypos 0
    linear 70 ypos -480
    repeat

image op_sky:
    "bg night"

image op_presents:
    contains:
        Text("星屑工房 presents", size=20, color="#cfd8ff", kerning=8)
        xalign 0.5 ypos 205
    contains:
        Text("STARDUST WORKS 1996", size=11, color="#8890c0", kerning=4)
        xalign 0.5 ypos 245
    alpha 0.0
    linear 0.55 alpha 1.0
    pause 0.8
    linear 0.5 alpha 0.0

image op_meteor_big:
    "images/fx/shoot.png"
    xzoom -1.4 yzoom 1.4 rotate -28 anchor (0.5, 0.5) pos (700, -40) alpha 0.0
    linear 0.3 alpha 1.0
    linear 1.5 pos (150, 330) alpha 0.0

image op_logo:
    contains:
        Text("星見坂{size=42}の{/size}セレナーデ", size=62, bold=True, color="#ffd1e6",
             outlines=[(5, "#2a0f5c", 0, 0), (5, "#ff2f86", 5, 5)])
        anchor (0.5, 0.5) pos (320, 160) zoom 3.2 alpha 0.0
        parallel:
            linear 0.2 alpha 1.0
        parallel:
            ease 0.55 zoom 1.0
    contains:
        Text("HOSHIMIZAKA SERENADE", size=20, italic=True, color="#7fe3ff", kerning=7,
             outlines=[(2, "#1a1050", 2, 2)])
        anchor (0.5, 0.0) pos (320, 212) alpha 0.0
        pause 0.35
        linear 0.4 alpha 1.0
    contains:
        Text("体験版", size=13, color="#ffffff", kerning=4, outlines=[(6, "#ff5fa2", 0, 0)])
        anchor (0.5, 0.0) pos (320, 250) zoom 0.0
        pause 0.6
        ease 0.3 zoom 1.2
        linear 0.1 zoom 1.0

image op_name_misaki:
    Text("朝比奈ミサキ", size=40, vertical=True, bold=True, color="#ffffff", outlines=[(3, "#c2185b", 0, 0)])

image op_name_touka:
    Text("綾瀬冬華", size=44, vertical=True, bold=True, color="#ffffff", outlines=[(3, "#1a3a8c", 0, 0)])

image op_circle_img:
    "images/op/circle.png"

image op_credit_line:
    Text("♪ OPENING THEME 「流れ星エチュード」", size=13, color="#ffe9a8", outlines=[(2, "#ff5fa2", 0, 0)])

image op_spark:
    "images/fx/spark.png"

image op_credits_end:
    Text("原画・シナリオ・音楽　星屑工房\n主題歌「流れ星エチュード」", size=12, color="#dfe6ff", kerning=3, text_align=0.5, line_spacing=6)

image op_wind_line:
    Solid("#ffffffd8", xysize=(300, 2))

## ---------------------------------------------------------------- 画面

screen op_flash():
    zorder 160
    add Solid("#ffffff") at flash_fade

screen op_whiteout():
    zorder 170
    add Solid("#ffffff") at whiteout_fade

screen op_lyric(row, txt, delay, dur):
    zorder 150
    fixed:
        fit_first True
        if row == 0:
            xanchor 0.0
            xpos 34
        else:
            xanchor 1.0
            xpos 606
        yanchor 1.0
        ypos (418 if row == 0 else 460)
        text txt size 24 bold True color "#ffffff" outlines [(2, "#1b1f6b", 0, 0)]
        text txt size 24 bold True color "#ff5fa2" outlines [(2, "#ffffff", 0, 0)] at lyric_wipe(delay, dur)

screen op_ui():
    zorder 180
    text "CLICK / ENTER : SKIP ▶▶" size 11 color "#ffffffaa" xalign 1.0 xoffset -10 yoffset 8
    key "game_menu" action NullAction()

## ---------------------------------------------------------------- 本体

label op:
    $ quick_menu = False
    window hide
    scene black
    play music audio.op noloop
    $ op_t0 = _time.time() + 0.12
    $ op_flash_n = 0
    show screen op_ui

    ## 0.0  星屑工房 presents
    scene black
    show op_stars
    show op_presents
    with None

    ## 1.875  流れ星
    if op_wait(1.875):
        jump op_done
    $ op_flash()
    scene op_sky
    show op_stars
    show op_meteor_big
    with None

    ## 3.3  1行目の歌詞（歌い始めは 3.75）
    if op_wait(3.3):
        jump op_done
    $ op_lyric(0)

    ## 3.75  ロゴ
    if op_wait(3.75):
        jump op_done
    $ op_flash()
    scene op_sky
    show op_stars
    show op_logo
    show op_credit_line at at_xy(24, 40), op_slide_r
    show op_spark at at_xy(96, 120), op_twinkle(0.0) as sp1
    show op_spark at at_xy(510, 200), op_twinkle(0.3) as sp2
    show op_spark at at_xy(440, 100), op_twinkle(0.6) as sp3
    $ op_lyric(1)

    ## 7.5  ミサキ登場
    if op_wait(7.5):
        jump op_done
    $ op_flash()
    scene black
    show expression Tile("images/op/stripes.png", size=(832, 480)) as stripes at op_stripes_scroll
    show op_circle_img at at_xy(200, 40)
    show misaki smile at op_misaki_intro
    show op_name_misaki at at_xy(60, 40), op_drop_in
    $ op_lyric(2)

    ## 9.375  目のアップ
    if op_wait(9.375):
        jump op_done
    scene black
    show expression Image("images/op/speed.png") as speed at at_xy(-330, -410)
    show misaki normal at op_eye_zoom
    with None

    ## 11.25  屋上・冬華
    if op_wait(11.25):
        jump op_done
    $ op_flash()
    scene black
    show bg rooftop at op_roof_pan
    show op_wind_line at at_xy(0, 90), op_wind(0.0, 300) as w1
    show op_wind_line at at_xy(0, 180), op_wind(0.4, 420) as w2
    show op_wind_line at at_xy(0, 300), op_wind(0.8, 260) as w3
    show touka cool at op_touka_rise
    show op_name_touka at at_xy(530, 40), op_drop_in
    $ op_lyric(3)

    ## 15.0  ミサキの顔
    if op_wait(15.0):
        jump op_done
    $ op_flash()
    scene black
    show expression Image("images/op/halftone_y.png") as ht
    show misaki happy at op_face_zoom
    $ op_lyric(4)

    ## 15.94  冬華の顔
    if op_wait(15.9375):
        jump op_done
    scene black
    show expression Image("images/op/halftone_c.png") as ht
    show touka blush at op_face_zoom

    ## 16.875  坂道（朝）
    if op_wait(16.875):
        jump op_done
    scene black
    show bg slope at op_slope_pan

    ## 17.8125  夕焼けのシルエット
    if op_wait(17.8125):
        jump op_done
    scene bg slope_sunset
    show misaki normal at op_sil_in(120)
    show touka normal at op_sil_in(300)

    ## 18.75  サビ
    if op_wait(18.75):
        jump op_done
    $ op_flash()
    scene black
    show expression Image("images/op/sunburst.png") as burst at op_spin
    show misaki happy at op_bounce(30, 0.0)
    show touka smile at op_bounce(310, 0.15)
    show op_spark at at_xy(40, 60), op_twinkle(0.0) as sp1
    show op_spark at at_xy(560, 90), op_twinkle(0.5) as sp2
    show op_spark at at_xy(300, 30), op_twinkle(0.8) as sp3
    $ op_lyric(5)

    ## 22.5  丘の上の二人（流星群）
    if op_wait(22.5):
        jump op_done
    $ op_flash()
    scene bg night at op_zoomout
    show op_stars_far
    show shoot_fx
    show shoot_fx2
    show misaki normal at Transform(pos=(226, 352), anchor=(0.0, 1.0), zoom=0.42, matrixcolor=BrightnessMatrix(-1.0))
    show touka normal at Transform(pos=(322, 352), anchor=(0.0, 1.0), zoom=0.44, matrixcolor=BrightnessMatrix(-1.0))

    ## 26.15  歌詞を消す
    if op_wait(26.15):
        jump op_done
    $ op_clear()
    $ renpy.hide_screen("op_ui")

    ## 26.25  タイトルロゴ
    if op_wait(26.25):
        jump op_done
    $ op_flash()
    scene op_sky
    show op_stars
    show op_logo
    show op_credits_end at at_top_center(320, 330), op_credits
    show op_spark at at_xy(110, 110), op_twinkle(0.0) as sp1
    show op_spark at at_xy(500, 220), op_twinkle(0.5) as sp2

    ## 29.2  ホワイトアウト
    if op_wait(29.2):
        jump op_done
    show screen op_whiteout
    if op_wait(30.0):
        jump op_done
    jump op_end

label op_done:
    ## スキップされた
    stop music fadeout 0.4
    $ op_clear()
    scene black with Dissolve(0.3)
    $ quick_menu = True
    $ persistent.op_seen = True
    return

label op_end:
    $ op_clear()
    scene black
    $ quick_menu = True
    $ persistent.op_seen = True
    return
