## 自動生成: python -m tools.gen_rpy  （手で編集しない）

## ---- 背景 (1280x960 の画像を 0.5 倍で 640x480 に) ----
image bg black = Transform("images/bg/black.png", zoom=0.5)
image bg slope = Transform("images/bg/slope.png", zoom=0.5)
image bg slope_sunset = Transform("images/bg/slope_sunset.png", zoom=0.5)
image bg slope_night = Transform("images/bg/slope_night.png", zoom=0.5)
image bg classroom = Transform("images/bg/classroom.png", zoom=0.5)
image bg classroom_evening = Transform("images/bg/classroom_evening.png", zoom=0.5)
image bg rooftop = Transform("images/bg/rooftop.png", zoom=0.5)
image bg rooftop_night = Transform("images/bg/rooftop_night.png", zoom=0.5)
image bg night = Transform("images/bg/night.png", zoom=0.5)
image bg hallway = Transform("images/bg/hallway.png", zoom=0.5)
image bg clubroom = Transform("images/bg/clubroom.png", zoom=0.5)
image bg home = Transform("images/bg/home.png", zoom=0.5)

## ---- CG ----
image cg misaki_end = Transform("images/cg/misaki_end.png", zoom=0.5)
image cg touka_end = Transform("images/cg/touka_end.png", zoom=0.5)
image cg normal_end = Transform("images/cg/normal_end.png", zoom=0.5)

## ---- 立ち絵 ----

image misaki_eyes_open:
    "images/chars/misaki/eyes_open.png"
    choice:
        3.2
    choice:
        4.4
    choice:
        5.2
    "images/chars/misaki/eyes_closed.png"
    0.12
    repeat

layeredimage misaki:
    at char_zoom

    always "images/chars/misaki/base_back.png"

    group eyes:
        attribute e_open default:
            "misaki_eyes_open"
        attribute e_happy:
            "images/chars/misaki/eyes_happy.png"
        attribute e_surprise:
            "images/chars/misaki/eyes_surprise.png"
        attribute e_pout:
            "images/chars/misaki/eyes_pout.png"
        attribute e_closed:
            "images/chars/misaki/eyes_closed.png"

    group mouth:
        attribute m_neutral default:
            "images/chars/misaki/mouth_neutral.png"
        attribute m_smile:
            "images/chars/misaki/mouth_smile.png"
        attribute m_happy:
            "images/chars/misaki/mouth_happy.png"
        attribute m_surprise:
            "images/chars/misaki/mouth_surprise.png"
        attribute m_pout:
            "images/chars/misaki/mouth_pout.png"
        attribute m_cool:
            "images/chars/misaki/mouth_cool.png"

    group cheek:
        attribute no_blush default null
        attribute blush:
            "images/chars/misaki/blush.png"

    always "images/chars/misaki/base_front.png"

    group brows:
        attribute b_normal default:
            "images/chars/misaki/brows_normal.png"
        attribute b_cool:
            "images/chars/misaki/brows_cool.png"
        attribute b_up:
            "images/chars/misaki/brows_up.png"
        attribute b_angry:
            "images/chars/misaki/brows_angry.png"
        attribute b_sad:
            "images/chars/misaki/brows_sad.png"

image touka_eyes_open:
    "images/chars/touka/eyes_open.png"
    choice:
        3.2
    choice:
        4.4
    choice:
        5.2
    "images/chars/touka/eyes_closed.png"
    0.12
    repeat

layeredimage touka:
    at char_zoom

    always "images/chars/touka/base_back.png"

    group eyes:
        attribute e_open default:
            "touka_eyes_open"
        attribute e_happy:
            "images/chars/touka/eyes_happy.png"
        attribute e_surprise:
            "images/chars/touka/eyes_surprise.png"
        attribute e_pout:
            "images/chars/touka/eyes_pout.png"
        attribute e_closed:
            "images/chars/touka/eyes_closed.png"

    group mouth:
        attribute m_neutral default:
            "images/chars/touka/mouth_neutral.png"
        attribute m_smile:
            "images/chars/touka/mouth_smile.png"
        attribute m_happy:
            "images/chars/touka/mouth_happy.png"
        attribute m_surprise:
            "images/chars/touka/mouth_surprise.png"
        attribute m_pout:
            "images/chars/touka/mouth_pout.png"
        attribute m_cool:
            "images/chars/touka/mouth_cool.png"

    group cheek:
        attribute no_blush default null
        attribute blush:
            "images/chars/touka/blush.png"

    always "images/chars/touka/base_front.png"

    group brows:
        attribute b_normal default:
            "images/chars/touka/brows_normal.png"
        attribute b_cool:
            "images/chars/touka/brows_cool.png"
        attribute b_up:
            "images/chars/touka/brows_up.png"
        attribute b_angry:
            "images/chars/touka/brows_angry.png"
        attribute b_sad:
            "images/chars/touka/brows_sad.png"

image kaede_eyes_open:
    "images/chars/kaede/eyes_open.png"
    choice:
        3.2
    choice:
        4.4
    choice:
        5.2
    "images/chars/kaede/eyes_closed.png"
    0.12
    repeat

layeredimage kaede:
    at char_zoom

    always "images/chars/kaede/base_back.png"

    group eyes:
        attribute e_open default:
            "kaede_eyes_open"
        attribute e_happy:
            "images/chars/kaede/eyes_happy.png"
        attribute e_surprise:
            "images/chars/kaede/eyes_surprise.png"
        attribute e_pout:
            "images/chars/kaede/eyes_pout.png"
        attribute e_closed:
            "images/chars/kaede/eyes_closed.png"

    group mouth:
        attribute m_neutral default:
            "images/chars/kaede/mouth_neutral.png"
        attribute m_smile:
            "images/chars/kaede/mouth_smile.png"
        attribute m_happy:
            "images/chars/kaede/mouth_happy.png"
        attribute m_surprise:
            "images/chars/kaede/mouth_surprise.png"
        attribute m_pout:
            "images/chars/kaede/mouth_pout.png"
        attribute m_cool:
            "images/chars/kaede/mouth_cool.png"

    group cheek:
        attribute no_blush default null
        attribute blush:
            "images/chars/kaede/blush.png"

    always "images/chars/kaede/base_front.png"

    group brows:
        attribute b_normal default:
            "images/chars/kaede/brows_normal.png"
        attribute b_cool:
            "images/chars/kaede/brows_cool.png"
        attribute b_up:
            "images/chars/kaede/brows_up.png"
        attribute b_angry:
            "images/chars/kaede/brows_angry.png"
        attribute b_sad:
            "images/chars/kaede/brows_sad.png"

