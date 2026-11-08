## 予告エンディング 3 種 → 体験版終了カード

label end_misaki:
    stop music fadeout 1.0
    scene bg night with fade
    play music audio.title fadein 1.5
    "――四月の終わり。それからの日々は、あっという間に過ぎていった。"
    "夏が近づくたびに、ミサキは坂のてっぺんで空を見上げるようになった。"
    scene cg misaki_end with Dissolve(1.5)
    play sound audio.shoot
    mi "ねえ、ユウくん。もし本当に、三十年ぶりの流れ星が降ったら……今度は、わたしからお願いしてもいい？"
    yu "ああ。何でも言ってくれ。"
    mi "……ううん。やっぱり、そのときまで内緒♪"
    "ひとすじの流れ星が、星見坂の空をよこぎる。"
    "この夏の物語は、まだ始まったばかりだ。"
    $ persistent.endings_seen.add("misaki")
    jump demo_end_card_misaki

label end_touka:
    stop music fadeout 1.0
    scene bg rooftop_night with fade
    play music audio.title fadein 1.5
    "――四月の終わり。天文部は、三人目の部員を迎えた。"
    "夜の屋上には、望遠鏡と、ふたつの影。"
    scene cg touka_end with Dissolve(1.5)
    play sound audio.shoot
    to "ねえ、相沢くん。父が見たかった空は、きっとこんな空だったのだと思うの。"
    yu "なら、夏に本物を見よう。ふたりで。"
    to "……ふたり、で。ええ。約束よ。"
    "ひとすじの流れ星が、屋上の空をよこぎる。"
    "この夏の物語は、まだ始まったばかりだ。"
    $ persistent.endings_seen.add("touka")
    jump demo_end_card_touka

label end_normal:
    stop music fadeout 1.0
    scene bg slope_night with fade
    play music audio.title fadein 1.5
    "――四月の終わり。結局、答えは出せないまま、夜の坂道に三つの影が並んだ。"
    show kaede happy at pos_c with dissolve
    ka "というわけで、天文部、無事に三人が揃いました！　新聞の一面はいただきだー！"
    hide kaede with dissolve
    scene cg normal_end with Dissolve(1.5)
    play sound audio.shoot
    mi "ユウくん、冬華さん、見て！　流れ星！"
    to "……流星群には、まだ早いわ。でも、きれいね。"
    yu "夏が楽しみだな。みんなで見よう。"
    "ひとすじの流れ星が、星見坂の空をよこぎる。"
    "この夏の物語は、まだ始まったばかりだ。"
    $ persistent.endings_seen.add("normal")
    jump demo_end_card_normal

label demo_end_card_misaki:
    call screen demo_end("misaki")
    $ MainMenu(confirm=False)()

label demo_end_card_touka:
    call screen demo_end("touka")
    $ MainMenu(confirm=False)()

label demo_end_card_normal:
    call screen demo_end("normal")
    $ MainMenu(confirm=False)()
