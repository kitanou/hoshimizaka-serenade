## 第2日  4/9（火）  ── 新聞部の楓、天文部の危機、昼休みの選択②

label day2:
    call date_card("4月9日（火）")
    scene bg hallway with dissolve
    play music audio.day fadein 1.0
    $ renpy.force_autosave()
    $ met_kaede = True

    "転校二日目。朝の廊下は、昨日よりずっと賑やかに感じる。"

    q "あっ、いたいた！　そこの転校生くーん！"
    show kaede happy at pos_c with dissolve
    q "ふふん、見つけたよ。取材させてもらうからね！"
    yu "えっと……君は？"
    ka "新聞部の柊楓（ひいらぎ かえで）。ミサキの親友で、この学校のことなら何でも知ってる女！"
    ka smile "『七年ぶりに帰ってきた幼なじみ』……いやあ、いいネタだよ。見出しはもう決まってるんだ。"
    yu "ちょっと待て、見出し？"
    ka happy "『星見坂に舞い戻った王子様！　ミサキ、ついに春到来か!?』"
    yu "やめてくれ……。"
    show kaede normal
    ka "冗談冗談。……ねえ、ひとつだけ真面目な話してもいい？"
    ka "うちの天文部、このままだと夏休み前の審査で廃部になるの。部員三人未満は即廃部ってルールでさ。"
    if joined_astro:
        ka "今は冬華と……あ、昨日入ってくれたのが相沢くん？　だったら、あとひとり！"
        yu "冬華が言ってた廃部の話は本当だったのか。"
    else:
        ka "今は冬華がひとりだけ。誰かが入ってくれないと、本当にまずいんだよね。"
        yu "綾瀬さんがひとりで……。"
    ka smile "ミサキはああ見えて、星の話になるとちょっと元気がなくなるの。理由は……そのうち本人から聞いてあげて。"
    ka happy "さて、取材取材！　またねー！"
    hide kaede with dissolve

    "チャイムが鳴る。慌ただしい朝は、あっという間に昼休みになった。"

    scene bg classroom with dissolve
    play sound audio.chime
    show misaki smile at pos_l with dissolve
    show touka normal at pos_r with dissolve
    mi "ユウくーん！　お昼、いっしょに食べよ！　屋上で！　お弁当、二人分つくってきたの！"
    to "相沢くん。部室の掃除を手伝ってほしいの。昼休みのうちに片づけたいから。"
    show misaki pout
    mi "あっ、委員長ずるい！　わたしが先に誘おうとしてたのに！"
    show touka cool
    to "先着順じゃないわ。必要なのは、手を動かせる人よ。"
    "二人の視線が、まっすぐこちらに向く。"

    menu:
        "屋上でミサキとお弁当":
            $ misaki_aff += 1
            jump day2_misaki
        "部室の掃除を手伝う":
            $ touka_aff += 1
            if not joined_astro:
                $ joined_astro = True
            jump day2_touka

label day2_misaki:
    scene bg rooftop with dissolve
    play music audio.misaki fadein 1.0
    show misaki happy at pos_c with dissolve
    mi "じゃーん！　特製・星形ハンバーグ！　ちょっと焦げちゃったけど……味は保証するよ！"
    yu "うまい。……昔、ミサキの作ったおにぎり、塩とお砂糖を間違えてたよな。"
    show misaki pout
    mi "もうっ、その話はなし！　あのときは小学二年生だったの！"
    show misaki smile
    mi "ねえ、ユウくん。七年前の約束、覚えてる？"
    yu "約束？"
    show misaki sad
    mi "……ううん、いいの。覚えてなくても。今、ここにユウくんがいてくれるだけで、十分だから。"
    "彼女は笑っていた。けれど、その指先は、少しだけ震えていた。"
    jump day2_evening

label day2_touka:
    scene bg clubroom with dissolve
    play music audio.touka fadein 1.0
    show touka normal at pos_c with dissolve
    to "ここが天文部の部室。ほとんど物置だけど。"
    yu "星図に、古い望遠鏡……。これ、全部ひとりで？"
    to "ええ。……去年までは、先輩たちもいたの。みんな卒業してしまったけれど。"
    show touka cool
    to "それと、この望遠鏡は父のもの。父は、天文学者になりたかったの。……なれなかったけれど。"
    show touka smile
    to "星はね、何万年も前の光が、今やっと届いているの。だから、見上げた人の数だけ、ちがう過去が見えるのよ。"
    yu "……いい言葉だな。"
    show touka blush
    to "っ……別に、ただの受け売りよ。さ、掃除の続き。手が止まってるわ。"
    "ほうきを動かしながら、気づかれないように彼女の横顔を見ていた。"
    jump day2_evening

label day2_evening:
    scene bg slope_sunset with dissolve
    play music audio.evening fadein 1.0
    "放課後。坂道の途中で、楓に呼び止められた。"
    show kaede normal at pos_c with dissolve
    ka "相沢くん。ひとつだけ、おせっかい。"
    ka "ミサキはね、七年前から毎年、誕生日の夜に坂のてっぺんで星に願い事をしてるの。『ユウくんが帰ってきますように』って。"
    yu "……毎年？"
    ka smile "冬華は冬華で、毎晩ひとりで屋上に上がってる。誰にも言わないけど、ね。"
    ka "二人とも、不器用なんだよ。だから、ちゃんと見てあげてね。"
    hide kaede with dissolve
    "夕焼けの坂道に、ひとり立ち尽くす。"
    "二人が抱えているもの。それを、俺はまだ何も知らない。"
    jump day3
