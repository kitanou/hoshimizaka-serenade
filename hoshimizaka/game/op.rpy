## オープニング（約30秒・全13カット）。絵コンテ: docs/op-storyboard.md
## 曲 audio/bgm/op.ogg（128BPM・16小節）の再生位置を基準に、各カットの開始秒で場面を切り替える。
## 背景は人物なしの背景プレート（images/op/bg_op_*.png。ComfyUI 生成 → 640x480 で減色・ディザ → 2 倍 Nearest の 1280x960。tools/bg_gen.py）。
## キャラクターは別の透過PNG（images/op/chars/）で、背景の前面に合成する。


default op_t0 = 0.0
default op_last = 0.0
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

    def op_time():
        """OP の現在時刻[秒]。音源の再生位置を基準にし、取得できないときだけ経過時間で代用する。
        絵コンテ §8: 独立タイマーで同期させない。巻き戻らないよう単調増加にする。"""
        p = renpy.music.get_pos("music")
        t = p if p is not None else (_time.time() - store.op_t0)
        t = max(t, store.op_last)
        store.op_last = t
        return t

    def op_wait(t):
        """OP 時刻が t 秒になるまで待つ。クリック/Enter で中断されたら True。"""
        while True:
            d = t - op_time()
            if d <= 0:
                return False
            if renpy.pause(min(d, 0.2)):
                return True

    def op_flash():
        store.op_flash_n += 1
        renpy.show_screen("op_flash", _tag="opflash%d" % store.op_flash_n)

    def op_lyric(i):
        """歌詞 i 行目を表示する。段は偶数/奇数で交互。前に同じ段にいた行は消す。"""
        text, start, dur = OP_LYRICS[i]
        delay = max(0.0, start - op_time())
        if i >= 2:
            renpy.hide_screen("oplyr%d" % (i - 2))
        renpy.show_screen("op_lyric", i % 2, text, delay, dur, _tag="oplyr%d" % i)

    def op_clear():
        for i in range(len(OP_LYRICS)):
            renpy.hide_screen("oplyr%d" % i)
        for n in range(1, store.op_flash_n + 1):
            renpy.hide_screen("opflash%d" % n)
        renpy.hide_screen("op_blackout")
        renpy.hide_screen("op_glowflash")
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

transform blackout_fade:
    alpha 0.0
    linear 0.8 alpha 1.0

transform glow_flash:
    alpha 0.0
    linear 0.15 alpha 0.4
    linear 0.5 alpha 0.0

transform dot2x:
    zoom 2.0
    nearest True

## CUT 03: 光が集まってロゴ
transform op_glow_in:
    anchor (0.5, 0.5) pos (320, 160) zoom 3.0 alpha 0.0
    parallel:
        linear 0.45 alpha 0.9
        linear 0.6 alpha 0.35
    parallel:
        ease 0.6 zoom 0.9

transform op_slam_bounce:
    anchor (0.5, 0.5) pos (320, 160) zoom 3.2 alpha 0.0
    parallel:
        linear 0.2 alpha 1.0
    parallel:
        ease 0.5 zoom 0.92
        ease 0.18 zoom 1.04
        ease 0.12 zoom 1.0

## CUT 04: ミサキ登場（右からスライドイン）
transform op_stripes_scroll:
    xpos -96 ypos 0
    linear 1.0 xpos 0
    repeat

transform op_misaki_intro:
    anchor (0.0, 0.0) pos (250, 40) zoom 1.1333 xoffset 320
    ease 0.55 xoffset 0

## CUT 05: 目元アップ（600x900 のアップ素材。ゆっくり寄る）
transform op_eye_zoom_m:
    anchor (0.513, 0.561) pos (320, 250) zoom 1.75
    ease 1.8 zoom 1.55

## CUT 06: 冬華（横顔→振り向き）
transform op_touka_turn:
    anchor (0.5, 0.0) pos (150, 40) zoom 1.2 xzoom 0.74 xoffset -14
    pause 0.3
    ease 1.3 xzoom 1.0 xoffset 0

transform op_obs_drift:
    anchor (0.5, 0.5) pos (320, 240) zoom 1.04 xoffset 0
    linear 3.75 xoffset -12

transform op_wind(delay, w):
    xpos 700 alpha 0.9
    pause delay
    linear 1.1 xpos -w
    repeat

## CUT 07/08: 表情アップ（600x900 のアップ素材）
transform op_face_m:
    anchor (0.5, 0.5) pos (320, 250) zoom 1.05
    ease 0.9 zoom 0.95

transform op_face_t:
    anchor (0.5, 0.3) pos (320, 250) zoom 1.35
    ease 0.9 zoom 1.2

## CUT 09: 坂道・朝（わずかに前進）
transform op_slope_forward:
    anchor (0.5, 0.53) pos (320, 254) zoom 1.0
    ease 0.94 zoom 1.12

transform op_light_in:
    alpha 0.0
    linear 0.94 alpha 0.3

## CUT 10: 夕景・後ろ姿（星が現れる／光を一度だけ強める）
transform op_stars_appear:
    alpha 0.0
    linear 0.9 alpha 1.0

transform op_twilight_pulse:
    alpha 0.0
    pause 0.45
    linear 0.2 alpha 0.5
    linear 0.28 alpha 0.0

transform op_back_l:
    anchor (0.0, 0.0) pos (110, 215) zoom 0.82 nearest True

transform op_back_r:
    anchor (0.0, 0.0) pos (300, 205) zoom 0.86 nearest True

## CUT 11: サビ（バウンス＋髪のゆらぎ）
transform op_bounce(x, delay):
    anchor (0.0, 0.0) pos (x, 50) yoffset 300
    pause delay
    ease 0.6 yoffset 0
    block:
        ease 0.234 yoffset -5 rotate 0.8
        ease 0.234 yoffset 0 rotate -0.8
        repeat

transform op_pump:
    zoom 1.03
    linear 0.4687 zoom 1.0
    repeat

transform op_spin:
    anchor (0.5, 0.5) pos (160, 80) rotate 0
    linear 9.0 rotate 360
    repeat

## CUT 12: 星降りの丘（ズームアウト）、後ろ姿が同じ空を見上げる
transform op_hill_zoomout:
    anchor (0.5, 0.5) pos (320, 240) zoom 1.3
    ease 3.75 zoom 1.0

transform op_back_hill_l:
    anchor (0.0, 0.0) pos (40, 222) zoom 0.86 nearest True yoffset 0
    block:
        ease 1.9 yoffset 2
        ease 1.9 yoffset 0
        repeat

transform op_back_hill_r:
    anchor (0.0, 0.0) pos (330, 214) zoom 0.9 nearest True yoffset 0
    block:
        ease 1.9 yoffset 2
        ease 1.9 yoffset 0
        repeat

## 共通
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

transform op_credits:
    alpha 0.0
    pause 0.5
    linear 0.9 alpha 1.0

## ---------------------------------------------------------------- 画像

## 背景プレート（人物なし）。320x240 のドット絵を 2 倍・Nearest で拡大する
image op_bg_starry = Transform("images/op/bg_op_starry_sky.png", zoom=0.5)
image op_bg_title = Transform("images/op/bg_op_title_sky.png", zoom=0.5)
image op_bg_observatory = Transform("images/op/bg_op_observatory_night.png", zoom=0.5)
image op_bg_lamp = Transform("images/op/bg_op_slope_lamp.png", zoom=0.5)
image op_bg_twilight = Transform("images/op/bg_op_town_twilight.png", zoom=0.5)
image op_bg_hill = Transform("images/op/bg_op_hill_meteor_shower.png", zoom=0.5)

## キャラクター（透過PNG）。通常は 300x450、アップ用は *_hi（600x900）
image op_misaki_smile = "images/op/chars/misaki_smile.png"
image op_touka_back = "images/op/chars/touka_back.png"
image op_misaki_back = "images/op/chars/misaki_back.png"

image op_misaki_eyes:
    ## contains は画面いっぱいの Fixed になるので、素材と同じ 600x900 に固定する（anchor の基準を合わせる）
    xysize (600, 900)
    contains:
        "images/op/chars/misaki_smile_hi.png"
        pause 0.95
        "images/op/chars/misaki_blush_hi.png"
    contains:
        ## 瞳の反射（星）を一度だけ入れる
        "images/fx/spark.png"
        anchor (0.5, 0.5) pos (368, 490) zoom 0.0 alpha 0.9
        pause 0.4
        ease 0.15 zoom 1.1
        ease 0.3 zoom 0.0

image op_touka_turn:
    "images/op/chars/touka_cool.png"
    pause 1.5
    "images/op/chars/touka_smile.png"

image op_misaki_face:
    "images/op/chars/misaki_surprise_hi.png"
    pause 0.42
    "images/op/chars/misaki_smile_hi.png"

image op_touka_face:
    "images/op/chars/touka_surprise_hi.png"
    pause 0.42
    "images/op/chars/touka_smile_hi.png"

image op_touka_smile = "images/op/chars/touka_smile.png"

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

image op_glow:
    "images/op/glow.png"

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

## ロゴ（CUT 03: 体験版 / CUT 13: 体験版 ver.0.97）
image op_logo:
    contains:
        Text("星見坂{size=42}の{/size}セレナーデ", size=62, bold=True, color="#ffd1e6",
             outlines=[(5, "#2a0f5c", 0, 0), (5, "#ff2f86", 5, 5)])
        anchor (0.5, 0.5) pos (320, 160) zoom 3.2 alpha 0.0
        parallel:
            linear 0.2 alpha 1.0
        parallel:
            ease 0.5 zoom 0.92
            ease 0.18 zoom 1.04
            ease 0.12 zoom 1.0
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

image op_logo_end:
    contains:
        Text("星見坂{size=42}の{/size}セレナーデ", size=62, bold=True, color="#ffd1e6",
             outlines=[(5, "#2a0f5c", 0, 0), (5, "#ff2f86", 5, 5)])
        anchor (0.5, 0.5) pos (320, 160) zoom 1.25 alpha 0.0
        parallel:
            linear 0.25 alpha 1.0
        parallel:
            ease 0.5 zoom 1.0
    contains:
        Text("HOSHIMIZAKA SERENADE", size=20, italic=True, color="#7fe3ff", kerning=7,
             outlines=[(2, "#1a1050", 2, 2)])
        anchor (0.5, 0.0) pos (320, 212) alpha 0.0
        pause 0.3
        linear 0.4 alpha 1.0
    contains:
        Text("体験版 ver.0.97", size=13, color="#ffffff", kerning=3, outlines=[(6, "#ff5fa2", 0, 0)])
        anchor (0.5, 0.0) pos (320, 250) alpha 0.0
        pause 0.6
        linear 0.3 alpha 1.0

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

## 流星群（CUT 12: 最初は数本、徐々に増やす。速度と長さを変える）
image op_shoot_a:
    "images/fx/shoot.png"
    xzoom -0.5 yzoom 0.5 rotate -28 anchor (0.5, 0.5) alpha 0.0 pos (690, 20)
    alpha 1.0
    linear 0.9 pos (350, 220) alpha 0.0
    pause 1.6
    repeat

image op_shoot_b:
    "images/fx/shoot.png"
    xzoom -0.9 yzoom 0.7 rotate -22 anchor (0.5, 0.5) alpha 0.0 pos (600, -10)
    alpha 1.0
    linear 0.7 pos (240, 180) alpha 0.0
    pause 1.2
    repeat

image op_shoot_c:
    "images/fx/shoot.png"
    xzoom -0.6 yzoom 0.5 rotate -32 anchor (0.5, 0.5) alpha 0.0 pos (420, -20)
    alpha 1.0
    linear 0.8 pos (120, 150) alpha 0.0
    pause 0.9
    repeat

image op_shoot_d:
    "images/fx/shoot.png"
    xzoom -1.2 yzoom 0.8 rotate -26 anchor (0.5, 0.5) alpha 0.0 pos (720, 60)
    alpha 1.0
    linear 0.6 pos (330, 260) alpha 0.0
    pause 0.7
    repeat

image op_shoot_e:
    "images/fx/shoot.png"
    xzoom -0.7 yzoom 0.6 rotate -24 anchor (0.5, 0.5) alpha 0.0 pos (300, -30)
    alpha 1.0
    linear 0.7 pos (30, 130) alpha 0.0
    pause 0.5
    repeat

## ---------------------------------------------------------------- 画面

screen op_flash():
    zorder 160
    add Solid("#ffffff") at flash_fade

screen op_blackout():
    zorder 170
    add Solid("#000000") at blackout_fade

screen op_glowflash():
    zorder 160
    add Solid("#fff6c8") at glow_flash

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
    $ op_last = 0.0
    $ op_flash_n = 0
    show screen op_ui

    ## CUT 01  0.000  星屑工房 presents
    scene black
    show op_stars
    show op_presents
    with None

    ## CUT 02  1.875  流星
    if op_wait(1.875):
        jump op_done
    $ op_flash()
    scene op_bg_starry
    show op_stars_far
    show op_meteor_big
    with None

    ## 歌詞1行目を先行表示（歌い出しは 3.750）
    if op_wait(3.3):
        jump op_done
    $ op_lyric(0)

    ## CUT 03  3.750  タイトル
    if op_wait(3.75):
        jump op_done
    $ op_flash()
    scene op_bg_title
    show op_stars
    show op_glow at op_glow_in
    show op_logo
    show op_credit_line at at_xy(24, 40), op_slide_r
    show op_spark at at_xy(96, 120), op_twinkle(0.0) as sp1
    show op_spark at at_xy(510, 200), op_twinkle(0.3) as sp2
    show op_spark at at_xy(440, 100), op_twinkle(0.6) as sp3
    $ op_lyric(1)

    ## CUT 04  7.500  ミサキ登場
    if op_wait(7.5):
        jump op_done
    $ op_flash()
    scene black
    show expression Tile("images/op/stripes.png", size=(832, 480)) as stripes at op_stripes_scroll
    show op_circle_img at at_xy(200, 40)
    show op_misaki_smile at op_misaki_intro
    show op_name_misaki at at_xy(60, 40), op_drop_in
    $ op_lyric(2)

    ## CUT 05  9.375  ミサキの目元アップ
    if op_wait(9.375):
        jump op_done
    scene black
    show expression Image("images/op/speed.png") as speed at at_xy(-330, -410)
    show op_misaki_eyes at op_eye_zoom_m
    with None

    ## CUT 06  11.250  天文台・冬華登場
    if op_wait(11.25):
        jump op_done
    $ op_flash()
    scene black
    show op_bg_observatory at op_obs_drift
    show op_wind_line at at_xy(0, 90), op_wind(0.0, 300) as w1
    show op_wind_line at at_xy(0, 180), op_wind(0.4, 420) as w2
    show op_wind_line at at_xy(0, 300), op_wind(0.8, 260) as w3
    show op_touka_turn at op_touka_turn
    show op_name_touka at at_xy(530, 40), op_drop_in
    $ op_lyric(3)

    ## CUT 07  15.000  ミサキ表情アップ（驚き→笑顔）
    if op_wait(15.0):
        jump op_done
    $ op_flash()
    scene black
    show expression Image("images/op/halftone_y.png") as ht
    show op_misaki_face at op_face_m
    $ op_lyric(4)

    ## CUT 08  15.938  冬華表情アップ（驚き→微笑み）
    if op_wait(15.9375):
        jump op_done
    scene black
    show expression Image("images/op/halftone_c.png") as ht
    show op_touka_face at op_face_t

    ## CUT 09  16.875  坂道・朝の光
    if op_wait(16.875):
        jump op_done
    scene black
    show op_bg_lamp at op_slope_forward
    show expression Solid("#fff6c8") as morning at op_light_in

    ## CUT 10  17.813  夕景の坂道・2人の後ろ姿
    if op_wait(17.8125):
        jump op_done
    scene op_bg_twilight
    show op_stars_far at op_stars_appear
    show op_misaki_back at op_back_l
    show op_touka_back at op_back_r
    show expression Solid("#fff4d0") as pulse at op_twilight_pulse

    ## CUT 11  18.750  Shooting Star!
    if op_wait(18.75):
        jump op_done
    $ op_flash()
    scene black
    show expression Image("images/op/sunburst.png") as burst at op_spin
    show op_misaki_smile at op_bounce(30, 0.0)
    show op_touka_smile at op_bounce(310, 0.15)
    show op_spark at at_xy(40, 60), op_twinkle(0.0) as sp1
    show op_spark at at_xy(560, 90), op_twinkle(0.5) as sp2
    show op_spark at at_xy(300, 30), op_twinkle(0.8) as sp3
    $ op_lyric(5)

    ## CUT 12  22.500  星降りの丘・流星群
    if op_wait(22.5):
        jump op_done
    $ op_flash()
    scene black
    show op_bg_hill at op_hill_zoomout
    show op_stars_far
    show op_shoot_a
    show op_misaki_back at op_back_hill_l
    show op_touka_back at op_back_hill_r
    if op_wait(23.3):
        jump op_done
    show op_shoot_b
    if op_wait(24.1):
        jump op_done
    show op_shoot_c
    show op_shoot_e
    if op_wait(24.9):
        jump op_done
    show op_shoot_d
    ## 「輝いて」の語尾で流星群の明るさを最大に
    if op_wait(25.6):
        jump op_done
    show screen op_glowflash

    ## 26.250  歌詞字幕を消す → CUT 13
    if op_wait(26.25):
        jump op_done
    $ op_clear()

    ## CUT 13  26.250  タイトル・クレジット
    $ op_flash()
    scene op_bg_title
    show op_stars
    show op_logo_end
    show op_credits_end at at_top_center(320, 330), op_credits
    show op_spark at at_xy(110, 110), op_twinkle(0.0) as sp1
    show op_spark at at_xy(500, 220), op_twinkle(0.5) as sp2
    show op_shoot_a
    if op_wait(29.2):
        jump op_done
    show screen op_blackout
    if op_wait(29.8):
        jump op_done
    stop music fadeout 0.2
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
