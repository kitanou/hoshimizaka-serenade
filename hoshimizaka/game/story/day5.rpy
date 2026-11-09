## 第5日  4/15（月）→ 8/12（月）  ── 時間圧縮ブリッジ（date_card）とルート選択⑥
## 決定案A §8-6: 4/15 の第二週朝 → 5月/6月/7月 の圧縮テロップ → 8/12 当日でルート確定
## 素材: bg classroom/clubroom/slope_sunset, BGM day/touka/evening, SE chime

label day5:
    call date_card("4月15日（月）")
    scene bg classroom with dissolve
    play music audio.day fadein 1.0
    $ renpy.force_autosave()

    "転校第二週目の、月曜の朝。"
    "冬華は屋上の扉の方へ、ミサキは下駄箱の方へ――二人の背中は、もうぶつかり合わない。"
    "――俺はといえば、どちらへも行かず、記憶の丘の方ばかり見ていた。"

    if weekend_plan == "misaki":
        yu "(……思い出のかけらは、ミサキとの約束の形をして、戻りつつあった)"
    elif weekend_plan == "touka":
        yu "(……1966年のノート。冬華の父の約束が、この町の空にまだ横たわっている)"
    else:
        yu "(……あの夜、丘で交わされた約束が、まだ答えを待っている)"

    "――五月。"

    scene bg clubroom with dissolve
    play music audio.touka fadein 1.0
    "天文部から、生徒会へ観測計画の提出。六月の部費審査へ向けて、部室の白板は方眼と矢印で埋まった。"

    if joined_astro:
        show touka normal at pos_c with dissolve
        to "仮部員を含めて三人。……審査には通る形式よ。形式的に、ではなく、本当に通すけど"
        yu "三人目って、もしかして"
        show touka smile
        to "柊さん。新聞部の取材がてら、備品の管理係を引き受けたわ。……断る選択肢が、わたしになかったのよ"
        hide touka with dissolve
    else:
        show kaede happy at pos_c with dissolve
        ka "というわけで、天文部仮部員・柊楓、着任しました！　記事にする代わりに部員番号3番もらいました！"
        show touka surprise at pos_r with dissolve
        to "柊さん。『仮』は部則にないはず……"
        ka "備品管理は立派な活動でしょ？　三人目、揃ったよ冬華"
        to "……揃った、わね。三人"
        "――冬華の声が、いちばん小さく、まっすぐだった。"
        hide kaede with dissolve
        hide touka with dissolve

    "――六月。"

    scene bg hallway with dissolve
    play music audio.day fadein 1.0
    "期末試験と部費審査が、同じ週に来た。"
    "審査の結果は、金曜の放課後に貼り出される――『天文部 続行可』。"
    show kaede happy at pos_c with dissolve
    ka "一面記事にしたる！　『天文部、流星群へ道開く』！"
    hide kaede with dissolve
    "廊下のざわめきの中で、冬華だけが、静かに息を吐いたのを、俺は見逃さなかった。"

    "――七月。"

    scene bg slope_sunset with dissolve
    play music audio.evening fadein 1.0
    "期末も終わり、夏休みが始まった。坂の空気は湿度と海の匂いを帯び、日没がおそくなる。"
    "町の商店街に、流星群の特別観測会の幟が立つ。天文台のプラネタリウムも『30年ぶりの大流星群』を上映すると謳っている。"

    if misaki_aff > touka_aff:
        show misaki smile at pos_c with dissolve
        mi "ユウくん、あと少しだね。……ちょっとだけ、胸がドキドキしてる"
        yu "流星群が近いからか？"
        show misaki blush
        mi "――さあね。七月をすぎたあたりから、約束の countdown じゃなくて、別の理由でドキドキしてる気がするの"
        hide misaki with dissolve
    elif touka_aff > misaki_aff:
        show touka normal at pos_c with dissolve
        to "相沢くん。八月十二日の予報、まだ先なのに毎日確認しているわ。我ながら、情けない"
        yu "俺もだ。……綾瀬さんの父上のノート、あの続きが、僕らはまだ読んでいない"
        show touka cool
        to "……ええ。だから、観測を成功させるの。記録を、三十年ぶりに、生かしたまま終わらせる"
        hide touka with dissolve
    else:
        "夕暮れの坂で、ふたりの影は並ばず、離れず、どちらも俺の横にいた。"
        "俺はどちらへも、決められないまま夏をむかえつつあった。"

    "――八月十一日。お盆直前の日に、坂のてっぺんで三つの影が止まった。"

    scene bg slope_sunset with dissolve
    show touka normal at pos_c with dissolve
    to "明日は天気、持ちこたえる見込み。……で、相沢くん。あなたが明日、どこに立つのか、まだ聞いていなかった"
    show misaki smile at pos_r with dissolve
    mi "ユウくん。……約束、果たしに来てくれるよね？　7年前の、ここで"
    "坂のてっぺんで、二人は同時に、でもちがう星空を見上げて、待っていた。"
    "――俺の返事は、もう決まっていた。決まっていた、はずだった。"

    menu:
        "ミサキ（流星群の夜へ）" if promised_misaki and misaki_aff >= 4:
            jump route_misaki
        "冬華（天文台の夜へ）" if joined_astro and touka_aff >= 4:
            jump route_touka
        "この街へ（夏休み）":
            jump end_normal

## ---- ルート分岐先（プレースホルダ） ----
## #26: ミサキ個別ルート（day8M-1..3 + GOOD/BAD）へ差し替え予定。差し替え時は demo_end_card_misaki を GOOD/BAD 演出に置換。
## #27: 冬華個別ルート（day8T-1..3 + GOOD/BAD）へ差し替え予定。同上。
## #28: TRUE END は両 GOOD 視聴 + star_promise の最終章（route-flow §3）として本ラベルとは別に実装。

label route_misaki:
    "八月十二日。約束の丘へ、俺は走る――"
    jump end_misaki

label route_touka:
    "八月十二日。観測の屋上へ、俺は走る――"
    jump end_touka
