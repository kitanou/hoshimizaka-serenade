## キャラクター定義。名前欄の色は gui/namebox_*.png（tools/gen_images.py で生成）。

define yu = Character("ユウキ", namebox_background=Frame("gui/namebox_yuki.png", gui.namebox_borders, tile=gui.namebox_tile))
define mi = Character("ミサキ", image="misaki", namebox_background=Frame("gui/namebox_misaki.png", gui.namebox_borders, tile=gui.namebox_tile))
define to = Character("冬華", image="touka", namebox_background=Frame("gui/namebox_touka.png", gui.namebox_borders, tile=gui.namebox_tile))
define ka = Character("楓", image="kaede", namebox_background=Frame("gui/namebox_kaede.png", gui.namebox_borders, tile=gui.namebox_tile))
## 正体が明かされる前の台詞用。表情タグは引き継ぐが、名前欄は灰色にする
define mq = Character("？？？", image="misaki", namebox_background=Frame("gui/namebox_unknown.png", gui.namebox_borders, tile=gui.namebox_tile))
define q = Character("？？？", namebox_background=Frame("gui/namebox_unknown.png", gui.namebox_borders, tile=gui.namebox_tile))

## ---- 表情プリセット ----
## 脚本では `mi happy "…"` のように 1 語で書く。ここで 目/口/眉/頬 の 4 グループすべてに展開する。
## （どれかを省くと直前の表情の属性が残るため、必ず 4 つ指定すること）
init python:
    _BASE = {
        "normal":   ("e_open",     "m_neutral",  "b_normal", "no_blush"),
        "smile":    ("e_open",     "m_smile",    "b_normal", "no_blush"),
        "happy":    ("e_happy",    "m_happy",    "b_normal", "blush"),
        "surprise": ("e_surprise", "m_surprise", "b_up",     "no_blush"),
        "pout":     ("e_pout",     "m_pout",     "b_angry",  "blush"),
        "blush":    ("e_open",     "m_smile",    "b_normal", "blush"),
        "cool":     ("e_open",     "m_cool",     "b_cool",   "no_blush"),
        "sad":      ("e_open",     "m_neutral",  "b_sad",    "no_blush"),
        "angry":    ("e_open",     "m_pout",     "b_angry",  "no_blush"),
        "closed":   ("e_closed",   "m_smile",    "b_normal", "no_blush"),
    }
    # 冬華は無表情寄りなので、通常の眉を b_cool にする（元プロトタイプと同じ）
    _TOUKA = dict(_BASE)
    for _k in ("normal", "happy"):
        _e, _m, _b, _c = _BASE[_k]
        _TOUKA[_k] = (_e, _m, "b_cool", _c)

    def _make_adjust(table):
        def adjust(name):
            tag = name[0]
            out = [tag]
            for a in name[1:]:
                out.extend(table.get(a, (a,)))
            return tuple(out)
        return adjust

    config.adjust_attributes["misaki"] = _make_adjust(_BASE)
    config.adjust_attributes["kaede"] = _make_adjust(_BASE)
    config.adjust_attributes["touka"] = _make_adjust(_TOUKA)
