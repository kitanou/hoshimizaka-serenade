## プロローグ  4/8（月）朝  ── 帰郷、坂道、再会

label prologue:
    scene bg black
    with fade
    play music audio.day fadein 1.0

    "――七年ぶりに帰ってきた、この街。"

    scene bg slope
    show petals
    with dissolve

    "星見坂（ほしみざか）。海へとくだる長い坂道と、春になると満開になる桜並木。"
    "子どものころ毎日のぼったこの坂を、今日からまた、制服で歩く。"

    yu "……変わってないな、ここは。"

    q "どいてどいてどいてーーっ！！"

    play sound audio.hit
    show layer master at shake
    show misaki surprise at pos_c with dissolve

    mq "いったぁ～……。ご、ごめんなさいっ！　遅刻しそうで、前見てなくて……"
    yu "いや、こっちこそ。……ん？　その黄色いリボン……"

    mq normal "え……？　あれ、もしかして……"
    mq happy "ユウくん!?　ユウくんだよね!?　わたし、ミサキだよ！　朝比奈ミサキ！"

    "朝比奈ミサキ。家がとなりどうしで、毎日いっしょに遊んでいた幼なじみ。"
    "七年前、引っ越しの日に泣きながら手をふっていた女の子が――"

    mi blush "えへへ……おかえりなさい、ユウくん。ずーっと、待ってたんだから。"
    yu "ただいま、ミサキ。……って、遅刻するんじゃなかったのか？"
    mi surprise "あああっ！　そうだった！　ほら、ユウくんも走って！　始業式はじまっちゃう！"

    play sound audio.footsteps
    hide misaki with dissolve
    jump day1
