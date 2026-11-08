init offset = -1

## 変換（ATL）。座標・秒数は index.html のプロトタイプに合わせる。

## 立ち絵は 600x900 で書き出してあるので 0.5 倍して 300x450 にする
transform char_zoom:
    zoom 0.5

## 立ち位置（プロトタイプの POS と同じ。左端基準、画面下から 12px はみ出す）
transform pos_l:
    xanchor 0.0 xpos 20 yanchor 1.0 ypos 494 yoffset 0
    block:
        ease 1.8 yoffset 2
        ease 1.8 yoffset 0
        repeat

transform pos_c:
    xanchor 0.0 xpos 170 yanchor 1.0 ypos 494 yoffset 0
    block:
        ease 1.8 yoffset 2
        ease 1.8 yoffset 0
        repeat

transform pos_r:
    xanchor 0.0 xpos 320 yanchor 1.0 ypos 494 yoffset 0
    block:
        ease 1.8 yoffset 2
        ease 1.8 yoffset 0
        repeat

## 画面の揺れ（衝突）
transform shake:
    xoffset 0 yoffset 0
    linear 0.08 xoffset -8 yoffset 4
    linear 0.08 xoffset 7 yoffset -5
    linear 0.08 xoffset -5 yoffset 3
    linear 0.08 xoffset 3 yoffset -2
    linear 0.08 xoffset 0 yoffset 0

## 花びら
image petals = SnowBlossom("images/fx/petal.png", count=16, border=40, xspeed=(-45, -20), yspeed=(70, 130), start=0, fast=False, horizontal=False)

## 流れ星
image shoot_fx:
    "images/fx/shoot.png"
    xzoom -0.5 yzoom 0.5 rotate -28 anchor (0.5, 0.5) alpha 0.0 pos (680, 10)
    pause 0.8
    alpha 1.0
    linear 0.9 pos (330, 230) alpha 0.0
    pause 2.2
    repeat

image shoot_fx2:
    "images/fx/shoot.png"
    xzoom -0.4 yzoom 0.4 rotate -28 anchor (0.5, 0.5) alpha 0.0 pos (560, -10)
    pause 2.2
    alpha 1.0
    linear 0.8 pos (240, 190) alpha 0.0
    pause 1.2
    repeat

## 一般的なフェード用
transform fade_in_out(t=1.8):
    alpha 0.0
    linear 0.35 alpha 1.0
    pause t - 0.7
    linear 0.35 alpha 0.0
