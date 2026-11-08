## 第1日  4/8（月）  ── 教室、星降りの伝説、放課後の選択①

label day1:
    scene bg classroom
    show petals
    with fade
    play sound audio.chime
    $ renpy.force_autosave()

    "――二年B組。転校生の自己紹介は、なんとか無事に終わった。"

    show misaki smile at pos_l with dissolve
    mi "まさかユウくんと同じクラスなんて！　これって運命かも、なーんて♪"
    q "朝比奈さん。ホームルーム中よ、静かにして。"

    show touka cool at pos_r with dissolve
    show misaki pout
    mi "うっ……ごめんなさい、委員長……"
    to "あなたが転校生の相沢くんね。クラス委員長の綾瀬冬華です。"
    to "わからないことがあれば聞いて。……ただし、浮ついた話はお断りよ。"
    yu "（クールな子だな……。でも、どこかで会ったような……？）"
    show touka normal
    to "……何？　人の顔をじっと見て。"
    yu "あ、いや、なんでもない。よろしく、綾瀬さん。"

    show misaki smile
    mi "ねえねえユウくん、知ってる？　この学校の「星降りの伝説」！"
    mi "この夏、三十年ぶりの流星群がくるの。その夜、坂のてっぺんで想いを伝えると――"
    show misaki blush
    mi "ふたりは、永遠に結ばれるんだって……♪"
    show touka cool
    to "……くだらない。ただの言い伝えよ。"
    "そう言いながら、委員長は窓の外の空を、少しだけ長く見つめていた。"

    hide misaki
    hide touka
    scene bg classroom_evening with fade
    play music audio.evening fadein 1.0

    "――そして、放課後。"
    "窓の外は、もう夕焼けに染まりはじめている。"

    menu:
        "ミサキといっしょに帰る":
            $ misaki_aff += 1
            $ promised_misaki = True
            jump day1_misaki
        "屋上へ行ってみる":
            $ touka_aff += 1
            $ joined_astro = True
            jump day1_touka

label day1_misaki:
    scene bg slope_sunset with dissolve
    show petals
    show misaki smile at pos_c with dissolve
    mi "こうしてふたりで坂をくだるの、七年ぶりだね。"
    yu "ミサキ、昔はここで転んでよく泣いてたよな。"
    show misaki pout
    mi "も、もう泣かないもん！　……ユウくんがいなくなったときは、いっぱい泣いたけど。"
    show misaki blush
    mi "ねえ、ユウくん。夏の流星群……いっしょに見に行ってくれる？"
    yu "ああ。約束する。"
    show misaki happy
    mi "ほんと!?　やったぁ！　約束だよ、ぜったいだからね！"
    jump day2

label day1_touka:
    scene bg rooftop with dissolve
    play sound audio.wind
    "屋上の扉を開けると、夕陽の中にひとりの少女がいた。"
    show touka surprise at pos_c with dissolve
    to "相沢くん……？　どうしてここに。"
    yu "なんとなく、空が見たくて。それ……望遠鏡？"
    show touka normal
    to "天文部の備品よ。部員はわたしひとりだけど。"
    to "このままだと廃部なの。夏の流星群をここで観測するまでは……終わらせたくない。"
    yu "じゃあ、俺が入るよ。天文部。"
    show touka blush
    to "え……？　……べ、別に頼んでないわ。"
    show touka smile
    to "……でも。ありがとう。入部届、明日持ってきて。"
    "はじめて見た彼女の笑顔は、一番星みたいに小さくて、きれいだった。"
    jump day2
