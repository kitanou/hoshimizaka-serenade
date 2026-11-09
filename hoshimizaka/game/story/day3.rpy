## 第3日  4/10（水）  ── ミサキと冬華のすれ違い、夜の選択③④

label day3:
    call date_card("4月10日（水）")
    scene bg classroom with dissolve
    play music audio.tension fadein 1.0
    $ renpy.force_autosave()

    "三日目の朝。教室の空気は、どこかぴりぴりしていた。"
    show misaki pout at pos_l with dissolve
    show touka cool at pos_r with dissolve
    to "朝比奈さん。相沢くんを毎日のように連れ回すのは、やめてもらえない？"
    mi "連れ回してなんかないもん！　幼なじみなんだから、いっしょにいたっていいでしょ！"
    to "彼は天文部の部員よ。部活の時間を削られるのは困るの。"
    mi "部員って……昨日、勝手に入れたんでしょ！？"
    to "勝手じゃないわ。本人の意思よ。"
    "――いや、少しだけ強引だった気もするが、言える空気じゃない。"
    show misaki angry
    mi "ユウくんは、どっちの味方なの!?"
    show touka angry
    to "答えて、相沢くん。"
    "二人の声が、教室に響く。"

    show kaede surprise at pos_c with dissolve
    ka "はいはいはーい！　ストップストップ！　朝から修羅場は新聞のネタになっちゃうぞー！"
    show misaki sad
    show touka normal
    mi "……ごめん。ちょっと、頭冷やしてくる。"
    to "……わたしも、言いすぎたわ。"
    hide misaki with dissolve
    hide touka with dissolve
    ka sad "相沢くん。放課後、どっちかに会いに行ってあげて。二人とも、本当は同じ気持ちなんだと思うから。"
    hide kaede with dissolve

    scene bg classroom_evening with fade
    "放課後。夕焼けの教室で、今日一日のことを考える。"
    "探しに行くなら、今夜しかない気がした。"

    menu:
        "夜の坂のてっぺんへ行く（ミサキ）":
            $ misaki_aff += 1
            jump day3_misaki
        "夜の屋上へ行く（冬華）":
            $ touka_aff += 1
            jump day3_touka

label day3_misaki:
    scene bg slope_night with fade
    play music audio.misaki fadein 1.5
    "夜の星見坂。街灯がぽつりぽつりと、海まで続いている。"
    "坂のてっぺんに、見覚えのあるショートボブのシルエットがあった。"
    show misaki sad at pos_c with dissolve
    mi "……来てくれたんだ。"
    yu "探したよ。今朝のこと、ごめん。ちゃんと答えられなくて。"
    mi "ううん。わたしが子どもだっただけ。……ねえ、ユウくん。"
    mi "あの日、引っ越しの朝、ユウくんは言ったよね。『ぜったい、また会いに来る』って。"
    mi "だから待ってた。毎年、ここで星にお願いして。……でも本当は、ずっと怖かったの。"
    mi "また、いなくなっちゃうんじゃないかって。"
    menu:
        "もうどこにも行かない。約束する":
            $ misaki_aff += 1
            show misaki happy
            mi "……うん。うんっ！　約束、だよ！"
            "彼女は涙をぬぐって、夜空よりもまぶしく笑った。"
        "それは……今はわからない":
            show misaki sad
            mi "……そっか。そうだよね。ごめん、変なこと聞いて。"
            "彼女は笑ってみせたけれど、その声は少しだけ遠かった。"
    jump day4

label day3_touka:
    scene bg rooftop_night with fade
    play music audio.touka fadein 1.5
    play sound audio.door
    "夜の屋上。冷たい風の中、望遠鏡の前に彼女はいた。"
    show touka normal at pos_c with dissolve
    to "……来たのね。わたし、あなたを呼んではいないけれど。"
    yu "天文部員が、部活に来ちゃいけないか？"
    show touka smile
    to "……いいえ。歓迎するわ。"
    show touka cool
    to "朝は、ごめんなさい。朝比奈さんに、八つ当たりをしたの。"
    to "三十年ぶりの流星群。父が、いちばん楽しみにしていたの。この屋上で観測するのが夢だった。"
    to "父はもういない。だから、わたしが代わりに見なきゃいけないの。……ひとりでも。"
    menu:
        "ひとりじゃない。俺もいる":
            $ touka_aff += 1
            show touka blush
            to "……っ。ばか。そういうこと、真顔で言わないで。"
            show touka smile
            to "……でも、ありがとう。少しだけ、気が楽になったわ。"
        "無理しなくていいよ":
            show touka cool
            to "……無理なんて、してないわ。"
            "強がる横顔は、いつもより少しだけ小さく見えた。"
    jump day4

label decide_ending:
    ## 互換温存ラベル（demo-design §5.1）。#25 の day4/day5 実装で本編から参照されない。
    ## 旧ラベル改名禁止のため削除しない。製品版ルート判定は day5 末尾の menu（選択⑥）。
    if misaki_aff >= 3 and misaki_aff > touka_aff:
        jump end_misaki
    elif touka_aff >= 3 and touka_aff > misaki_aff:
        jump end_touka
    else:
        jump end_normal
