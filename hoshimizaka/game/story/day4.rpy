## 第4日  4/11（木）〜4/13（土）  ── 和解、丘の記憶の影、週末の選択⑤（決定案A §8-6）
## 素材: bg hallway/classroom/slope_sunset/slope/slope_night/home, BGM day/evening/touka/misaki, SE chime/page
## ※丘の昼背景が未制作のため、下見は slope（朝）＋台詞描写で代替（差し替え候補は manifest 参照）

label day4:
    call date_card("4月11日（木）")
    scene bg hallway with dissolve
    play music audio.day fadein 1.0
    $ renpy.force_autosave()

    "朝、教室に入ると、ミサキと冬華の空気が、はっきりと変わっていた。"
    "敵意じゃない。昨夜のできごとが、見えない敷居になったままだ。"

    show misaki smile at pos_l with dissolve
    mi "ユウくん、今日も図書室で一緒に勉強する？　……って、だめ、だったかな"
    yu "いや、いいよ。いつものように。"
    show misaki happy
    mi "……うん。いつものように。"

    show touka normal at pos_r with dissolve
    to "相沢くん。二限目のあと、少しだけ。屋上の施錠の件、確認しておきたいの"
    yu "了解。"
    "――二人とも、やけに丁寧だ。それが、いちばんこわい。"

    hide misaki
    hide touka
    scene bg classroom with dissolve
    play sound audio.chime
    "昼休み。三人分の弁当の場所を、結局決められなかった。"

    show kaede happy at pos_c with dissolve
    ka "新聞部より速報！　『転校三日目にして修羅場、四日目に小康状態』のコーナー！"
    yu "やめてくれ。"
    ka "冗談だよー。……ねえ、天文部の観測申請、受理されたって。六月の部費審査まで、放課後の屋上、公式に使っていいってさ"
    ka "で、六月の審査に通れば、流星群の夜まで屋上キープ。廃部審査そのものは通過確定、ってところ"
    yu "それ、冬華がひとりで申請したのか？"
    show kaede normal
    ka "さあて。……三人目、まだ足りないけどね。部員三人未満は廃部、ルールは生きてるから"
    ka smile "さては新聞部、今日も取材取材！"
    hide kaede with dissolve

    "放課後。坂道の途中。"
    scene bg slope_sunset with dissolve
    play music audio.evening fadein 1.0

    "街灯が、誰かを待っていたみたいに、ひとつずつ灯りはじめる。"
    yu "……この景色。どこかで、誰かと見た気がする"
    "七年前のあの日。引っ越しのトラックが動き出す前に、俺は誰に何を言った？"
    "思い出そうとすると、輪郭から溶けていく。"

    if misaki_aff > touka_aff:
        show misaki smile at pos_c with dissolve
        mi "……ユウくん？　どうしたの、ボッーとして"
        yu "いや。……ミサキ、昔よく遊んだ丘って、まだあるよな"
        show misaki surprise
        mi "丘？　あるよ、もちろん！　望遠鏡のある小高いとこ。……って、ユウくん、忘れてたの!?"
        show misaki normal
        mi "……ま、いいけど。いま、ユウくんがいるから"
        yu "(……答えられなかった)"
        hide misaki with dissolve
    elif touka_aff > misaki_aff:
        show touka normal at pos_c with dissolve
        to "相沢くん。ぼんやりしないで。坂道は危ないわ"
        yu "悪い。……綾瀬さん。流星群の夜って、どこで見るもんなの？　坂のてっぺん？　それとも屋上"
        show touka cool
        to "……望遠鏡があるのは、当然、屋上よ"
        show touka smile
        to "……とはいえ。あの丘は、町の灯りからいちばん遠いわ。条件が整えば、いちばん多く見える場所でもある"
        hide touka with dissolve
    else:
        "坂の途中でただ立ち止まり、街灯が灯るのを眺めていた。"
        "かすかな記憶が、喉の奥まで持ち上がって、そして静かに沈んでいく。"

    "――あさっては土曜。転校して、はじめての週末だ。"

    menu:
        "丘をミサキと下見する":
            $ misaki_aff += 1
            $ weekend_plan = "misaki"
            jump day4_scout_misaki
        "天体望遠鏡を冬華と整備する":
            $ touka_aff += 1
            $ weekend_plan = "touka"
            jump day4_teach_touka
        "家にこもって過去を思い出す":
            $ weekend_plan = "none"
            jump day4_homealone

## ---- ⑤a  4/13（日） 丘の下見・ミサキ ----
label day4_scout_misaki:
    call date_card("4月13日（土）")
    scene bg slope with dissolve
    play music audio.misaki fadein 1.0

    "土曜の朝、ミサキの家の前で待ち合わせた。"
    show misaki happy at pos_c with dissolve
    mi "地図に水筒に懐中電灯！　完全なる下見チーム、です！　……てっぺんまで歩くだけなんだけど"
    yu "真面目すぎだろ"
    mi "だって、こういうのは準備が命だから！"
    hide misaki with dissolve

    "桜の散った坂道を、上へ上へと歩いた。"
    "花びらのない坂道は、子どものころとは別人みたいな顔をしていた。"

    scene bg slope with dissolve
    show misaki smile at pos_c with dissolve
    mi "ほら、丘いちばんの見晴らし。夏はここで町ぜんたいが星を見るの。……で、ベストスポッートはここ"
    "彼女は、平たい石の上にちょこんと座ってみせた。"
    mi "風よけにもなるし、海もまるごと見えて、そして――"
    show misaki blush
    mi "――あ、な、なんでもない！　えへへ"

    "石のわきに腰を下ろすと、風が、七年前とまったく同じにおいがした。"
    $ hill_memory = True
    yu "……ミサキ。俺、ここで昔、お前と――"
    mi "……うん"
    show misaki normal
    mi "……うん。そうだよ"
    mi "思い出せなくても、いいって前に言ったよね。でも本当は、思い出してほしいなって、ずっと思ってた"

    "ノートに方角と時刻を書きこむふたり。夕方の坂道を、べつの言葉を探すままに下りた。"
    jump day5

## ---- ⑤b  4/13（日） 望遠鏡整備・冬華 ----
label day4_teach_touka:
    call date_card("4月13日（土）")
    scene bg clubroom with dissolve
    play music audio.touka fadein 1.0

    "土曜の部室。冬華は床にクロスを広げ、望遠鏡を分解していた。"
    show touka normal at pos_c with dissolve
    to "観測の前に、道具を学びなさい。……ファインダーは両手で持て。埃は敵よ"
    yu "……すごい年代ものだ。これ、いつの？"
    to "接眼部に刻印がある。……1966年製。うちの望遠鏡は、その年から空を見てる"

    "二人でレンズを磨いていると、冬華は棚の古い箱を開けた。"
    "――表紙の褪せた、観測ノート。"
    play sound audio.page
    to "……父のノート。1966年8月12日の、大流星群の記録"
    $ fathernote = True
    yu "30年前にも、大流星群が？"
    show touka normal
    to "この町は、その夜ぜんたいが丘に集まったらしい。翌年の町紙に、読者の投書まで載ったって"
    to "――『星がふたたび降る夜に、あなたへ』。書いた人と、届かなかった人の、三十年"
    show touka blush
    to "……失礼。感傷ではないわ。単に、記録として重要だと"

    "ノートのあるページで、冬華の手が止まった。欄外に、子どもじみた字迹で二度塗りされた行。"
    to "……『丘にて、彼女と。三十年後、必ず』。……父が、いちばん長く見開いていたページ"
    yu "（……冬華の父も、またこの丘で誰かと――）"
    show touka cool
    to "訊かれたくないなら訊かないで。その人のことは、まだ、誰も知らないの"
    to "……わたしが観測を成功させれば、その続きがわかる気がするの。あの夜を、記録として終わらせたくない"

    "二人で磨き上げたレンズは、机の上にできた小さな星団を、確かに映していた。"
    jump day5

## ---- ⑤c  4/13（日） 家・一人 ----
label day4_homealone:
    call date_card("4月13日（土）")
    scene bg home with dissolve
    play music audio.day fadein 1.0

    "土曜、家。押入れの奥から、七年前の引越し箱を引っぱり出した。"
    "――褪せた小学のノート。裏表紙に、星図のステッカー。"
    "罫線を無視した大きな字で、もう一行。"
    yu "『7年後のなつ、丘でまた みるやくそく』"
    $ hill_memory = True
    "筆跡は、たぶん、俺のものだった。約束した相手が、誰だったのか――"

    "夕方、町に出てしまった。身体が先に、坂を下っていた。"
    scene bg slope_night with dissolve
    play music audio.evening fadein 1.0
    "夜の星見坂。海は、星を敷きつめた黒い鏡。"
    "上へ上へと歩きながら、七年前の自分の背中に追いつこうとした。"

    "坂の途中で、懐中電灯の光が揺れた。"
    show misaki sad at pos_c with dissolve
    mi "……ユウくん？　こんな時間に、なにを"
    yu "ミサキ。……お前も、昔ここで――"
    show misaki normal
    mi "……ううん。なんでもない"
    mi "今日はなんにも言わない日。決めてきたの"

    "並んで歩き出すまで、二人ともなにも言わなかった。それが、不思議と心地よかった。"
    hide misaki with dissolve
    jump day5
