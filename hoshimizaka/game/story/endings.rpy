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
    ## #25 で拡大: 8/12 大流星群の夜、全員で見るスライス・オブ・ライフ結末（決定案A §7#6 の NORMAL）
    stop music fadeout 1.0
    scene bg slope_night with fade
    play music audio.evening fadein 1.5
    "――八月十二日。三十年ぶりの、大流星群の夜。"
    "坂のてっぺんには、町じゅうの人の影。商店街の提灯、懐中電灯、それから満天の星。"

    show kaede happy at pos_c with dissolve
    ka "新聞部特設席、ここに設営！　号外の見出しはもう決めてるんだ。『町あげて、星を見た夜』！"
    yu "……今回は認めるよ。いい見出しだ"
    ka "っ当然！　というわけで天文部・観測班、本日も快調ですー！"
    hide kaede with dissolve

    show misaki smile at pos_l with dissolve
    show touka normal at pos_r with dissolve
    to "……晴れた。記録を、余すところなく書けるわ"
    mi "ユウくん、ぼくの分まで数えてね！　四十こえたら、お願いごと、ひとつきくって約束"
    yu "四十でいいのかな。……何をお願いするつもり"
    mi "――さあね"

    if fathernote:
        "冬華は、望遠鏡のそばで一度だけ、懐から古いノートの断片を取り出して、夜空にかざした。"
        to "……父さん。『星がふたたび降る夜に、あなたへ』。……三十年、遅れたけど、届いたと思うわ"
        "その声は、いつもの半分の日差しで、いつもの倍、やさしかった。"

    if hill_memory:
        "坂のてっぺんに吹く風は、七年前の夜と、まったく同じにおいがした。"
        "――まだ、思い出せない。ここで誰と何を約束したのか。"
        "いいんだ。この二人と、これから何度も夜を越せば、いつか追いつける。"

    "――その夜、星見坂の空を、四つをこえる流星が横切った。"
    scene cg normal_end with Dissolve(1.5)
    play sound audio.shoot
    mi "見て見て！　すっごく明るいのが、ひとつ――"
    to "……記録できた。観測は、成功よ"
    ka "天文部・次期十年計画の取材はこれからだー！　新聞部も新しい部員、募集してるんだよー！"
    yu "――来年も、みんなで見るよな"

    "俺は、どちらの隣にも立たなかった。二つの約束を、今はまだ、両方にしまっておく。"
    "それでも、この空のもとへは、また来年も、たぶん二人とも来る。それだけで、十分だった。"
    "この街の星の物語は、まだ序章のはじまりにすぎない。"
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
