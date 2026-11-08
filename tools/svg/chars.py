"""立ち絵のレイヤー別 SVG 生成。

index.html の charSVG() を Python に移植し、Ren'Py の layeredimage 用に
「後ろ髪+体+顔 / 目 / 口 / 頬 / 前髪+アクセサリ / 眉」へ分割して出力する。
全レイヤー共通で viewBox は 0 0 400 600。
"""

LINE = "#3a2030"
SKIN = "#ffe6d5"
SKIN_D = "#f5c0ab"

CH = {
    "misaki": dict(hair="#ff9cbc", hairD="#d95a88", hairL="#ffe3ee", eye="#e2457e",
                   eyeD="#6e1440", eyeL="#ffb0d0", style="twin", cool=False, ribbon="#e8384f"),
    "touka": dict(hair="#4a5cbc", hairD="#26327a", hairL="#b2c0ff", eye="#2aa6d2",
                  eyeD="#0e3658", eyeL="#a6eeff", style="long", cool=True, ribbon="#e8384f"),
    # サブキャラ（仮）。丸眼鏡のショートボブ
    "kaede": dict(hair="#ff9a4a", hairD="#c4601a", hairL="#ffe0b8", eye="#3aa66a",
                  eyeD="#12462a", eyeL="#b0f0c8", style="bob", cool=False, ribbon="#3fa86a"),
}

EYE_SHAPE = "M-21,-10 Q-2,-34 21,-15 Q23,22 0,26 Q-22,24 -21,-10 Z"

EYE_KINDS = ["open", "happy", "surprise", "pout", "closed"]
MOUTH_KINDS = ["neutral", "smile", "happy", "surprise", "pout", "cool"]
BROW_KINDS = ["normal", "cool", "up", "angry", "sad"]


def _wrap(body, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 600" '
            f'width="400" height="600"><defs>{defs}</defs>{body}</svg>')


def _mir(s):
    return f'{s}<g transform="translate(400,0) scale(-1,1)">{s}</g>'


# ---------------------------------------------------------------- 目
def eye_svg(c, kind):
    defs = (f'<linearGradient id="ir" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{c["eyeD"]}"/><stop offset=".55" stop-color="{c["eye"]}"/>'
            f'<stop offset="1" stop-color="{c["eyeL"]}"/></linearGradient>'
            f'<clipPath id="ec"><path d="{EYE_SHAPE}"/></clipPath>')
    out = ""
    for side in (-1, 1):
        cx = 165 if side < 0 else 235
        cy = 218
        sx = -1 if side < 0 else 1
        sy = 0.86 if c["cool"] else 1
        rot = -5 if c["cool"] else 0
        tf = f"translate({cx},{cy}) scale({sx},{sy}) rotate({rot})"
        if kind == "closed":
            out += (f'<g transform="{tf}"><path d="M-20,0 Q0,9 21,-2" fill="none" stroke="{LINE}" '
                    f'stroke-width="4" stroke-linecap="round"/></g>')
            continue
        if kind == "happy":
            out += (f'<g transform="{tf}"><path d="M-19,6 Q0,-14 20,4" fill="none" stroke="{LINE}" '
                    f'stroke-width="4.5" stroke-linecap="round"/></g>')
            continue
        sur = kind == "surprise"
        irx, iry = (11, 16) if sur else (14, 20)
        prx, pry = (4, 6) if sur else (6.5, 10)
        body = (f'<path d="{EYE_SHAPE}" fill="#fff"/>'
                f'<g clip-path="url(#ec)"><ellipse cx="1" cy="4" rx="{irx}" ry="{iry}" fill="url(#ir)" '
                f'stroke="{c["eyeD"]}" stroke-width="1.5"/>'
                f'<ellipse cx="1" cy="7" rx="{prx}" ry="{pry}" fill="{c["eyeD"]}"/>'
                f'<path d="M-22,-14 Q0,-30 22,-18 L22,-4 Q0,-16 -22,-2Z" fill="{c["eyeD"]}" opacity=".25"/></g>'
                f'<circle cx="-5" cy="-5" r="5.5" fill="#fff"/><circle cx="7" cy="13" r="2.6" fill="#fff"/>'
                f'<path d="M-24,-8 Q-3,-37 23,-16" fill="none" stroke="{LINE}" stroke-width="6" stroke-linecap="round"/>'
                f'<path d="M20,-15 L30,-11" stroke="{LINE}" stroke-width="4" stroke-linecap="round"/>'
                f'<path d="M-8,26 Q4,28 15,21" fill="none" stroke="{LINE}" stroke-width="2"/>')
        if kind == "pout":
            body += (f'<path d="M-27,-44 L30,-44 L30,-7 Q0,-14 -27,-3Z" fill="{SKIN}"/>'
                     f'<path d="M-25,-4 Q0,-14 27,-7" fill="none" stroke="{LINE}" stroke-width="5" stroke-linecap="round"/>')
        out += f'<g transform="{tf}">{body}</g>'
    return _wrap(out, defs)


# ---------------------------------------------------------------- 眉
def brow_svg(c, kind):
    d = {
        "normal": "M-16,-37 Q2,-45 20,-38",
        "cool": "M-16,-35 Q4,-42 20,-42",
        "up": "M-16,-45 Q2,-54 20,-46",
        "angry": "M-16,-34 Q2,-38 20,-44",
        "sad": "M-16,-44 Q2,-40 20,-33",
    }[kind]
    out = ""
    for side in (-1, 1):
        cx = 165 if side < 0 else 235
        sx = -1 if side < 0 else 1
        out += (f'<path transform="translate({cx},218) scale({sx},1)" d="{d}" fill="none" '
                f'stroke="{LINE}" stroke-width="3" stroke-linecap="round"/>')
    return _wrap(out)


# ---------------------------------------------------------------- 口
def mouth_svg(kind):
    L = LINE
    d = {
        "smile": f'<path d="M188,262 Q200,273 212,262" fill="none" stroke="{L}" stroke-width="2.6" stroke-linecap="round"/>',
        "happy": (f'<path d="M185,259 Q200,284 215,259 Z" fill="#c64a5c" stroke="{L}" stroke-width="2.5" stroke-linejoin="round"/>'
                  f'<path d="M193,274 Q200,268 207,274 Q200,279 193,274Z" fill="#ff8f9a"/>'),
        "surprise": f'<ellipse cx="200" cy="267" rx="6" ry="8" fill="#a53a4c" stroke="{L}" stroke-width="2.4"/>',
        "pout": f'<path d="M192,268 Q200,262 208,268" fill="none" stroke="{L}" stroke-width="2.6" stroke-linecap="round"/>',
        "cool": f'<path d="M193,266 L207,265" stroke="{L}" stroke-width="2.4" stroke-linecap="round"/>',
        "neutral": f'<path d="M192,265 Q200,269 208,265" fill="none" stroke="{L}" stroke-width="2.5" stroke-linecap="round"/>',
    }[kind]
    return _wrap(d)


def blush_svg():
    s = ""
    for x in (154, 246):
        s += f'<ellipse cx="{x}" cy="252" rx="19" ry="8" fill="#ff7f99" opacity=".45"/>'
        for i in (-1, 0, 1):
            s += (f'<path d="M{x + i * 8 - 3},256 l6,-8" stroke="#e0506e" stroke-width="1.6" stroke-linecap="round"/>')
    return _wrap(s)


# ---------------------------------------------------------------- 土台
def _hair_back_and_acc(c):
    H, HD = c["hair"], c["hairD"]
    st = c["style"]
    if st == "twin":
        back = _mir(f'<path d="M138,100 C66,96 34,200 46,320 C54,400 38,460 56,530 L74,500 L88,522 '
                    f'C100,430 92,360 96,290 C100,210 120,150 150,124 Z" fill="{H}"/>'
                    f'<path d="M70,190 C60,260 66,330 70,420" fill="none" stroke="{HD}" stroke-width="2"/>')
        acc = (_mir(f'<path d="M138,100 L104,76 L102,124 Z" fill="#ffe066"/><path d="M138,100 L170,78 L168,124 Z" '
                    f'fill="#ffe066"/><circle cx="138" cy="101" r="8" fill="#ffcc33"/>')
               + f'<path d="M198,58 C204,24 238,20 238,38 C224,32 212,40 207,58 Z" fill="{H}"/>')
    elif st == "long":
        back = (f'<path d="M126,120 C92,240 84,420 78,600 L322,600 C316,420 308,240 274,120 C250,70 150,70 126,120 Z" fill="{H}"/>'
                f'<path d="M110,300 C104,400 100,500 98,600 M290,300 C296,400 300,500 302,600" fill="none" stroke="{HD}" stroke-width="2"/>')
        acc = (f'<path d="M124,146 Q200,48 276,146" fill="none" stroke="{LINE}" stroke-width="13" stroke-linecap="round"/>'
               f'<path d="M124,146 Q200,48 276,146" fill="none" stroke="#fff" stroke-width="7" stroke-linecap="round"/>')
    else:  # bob
        back = (f'<path d="M128,110 C84,150 88,262 102,304 L142,296 L258,296 L298,304 C312,262 316,150 272,110 '
                f'C250,70 150,70 128,110 Z" fill="{H}"/>')
        acc = (f'<circle cx="165" cy="218" r="32" fill="#ffffff" fill-opacity=".14" stroke="#5a4636" stroke-width="3.5"/>'
               f'<circle cx="235" cy="218" r="32" fill="#ffffff" fill-opacity=".14" stroke="#5a4636" stroke-width="3.5"/>'
               f'<path d="M197,214 Q200,208 203,214" fill="none" stroke="#5a4636" stroke-width="3.5"/>'
               f'<path d="M130,176 L112,160 M270,176 L288,160" stroke="#5a4636" stroke-width="3" stroke-linecap="round"/>'
               f'<path d="M262,98 L286,96 M262,108 L286,112" stroke="#ffe066" stroke-width="6" stroke-linecap="round"/>')
    return back, acc


def base_back_svg(c):
    back, _ = _hair_back_and_acc(c)
    R = c["ribbon"]
    body = (f'<path d="M178,262 L178,362 L222,362 L222,262 Z" fill="{SKIN}"/>'
            f'<path d="M178,282 Q200,314 222,282 L222,302 Q200,332 178,302 Z" fill="{SKIN_D}" stroke="none"/>'
            f'<path d="M60,600 C66,480 96,392 165,352 L235,352 C304,392 334,480 340,600 Z" fill="#fbfbff"/>'
            + _mir(f'<path d="M62,600 C68,480 98,394 160,356 L150,376 C112,424 98,500 98,600 Z" fill="#dde2f2" stroke="none"/>') +
            f'<path d="M162,350 L200,446 L238,350 Z" fill="{SKIN}"/>'
            f'<path d="M174,388 L200,446 L226,388 Z" fill="#fbfbff"/>'
            f'<path d="M162,350 L200,446 L238,350 L300,386 C306,414 302,438 292,452 L200,502 L108,452 C98,438 94,414 100,386 Z" fill="#26397c"/>'
            f'<path d="M114,396 L200,482 L286,396" fill="none" stroke="#fff" stroke-width="3.5"/>'
            f'<path d="M200,476 L158,460 L164,502 Z" fill="{R}"/><path d="M200,476 L242,460 L236,502 Z" fill="{R}"/>'
            f'<path d="M192,482 L176,562 L198,542 Z" fill="{R}"/><path d="M208,482 L224,562 L202,542 Z" fill="{R}"/>'
            f'<rect x="189" y="466" width="22" height="20" rx="6" fill="{R}"/>')
    face = (f'<path d="M130,150 C128,215 160,272 200,298 C240,272 272,215 270,150 C270,100 240,80 200,80 '
            f'C160,80 130,100 130,150 Z" fill="{SKIN}"/>')
    nose = f'<path d="M203,240 l-3,7" stroke="{SKIN_D}" stroke-width="2" stroke-linecap="round"/>'
    return _wrap(f'<g stroke="{LINE}" stroke-width="3" stroke-linejoin="round">{back}{body}{face}</g>{nose}')


def base_front_svg(c):
    H, HD = c["hair"], c["hairD"]
    _, acc = _hair_back_and_acc(c)
    lock = (f'<path d="M124,150 C112,220 116,290 106,352 L124,332 L134,348 C142,280 140,210 146,160 Z" fill="{H}"/>')
    front = (_mir(lock) +
             f'<path d="M122,176 L136,124 L150,170 L164,116 L180,176 L196,110 L212,174 L228,116 L244,172 L258,124 '
             f'L278,176 C292,94 250,56 200,56 C150,56 108,94 122,176 Z" fill="{H}"/>'
             f'<path d="M164,116 Q160,90 176,70 M228,116 Q236,90 224,70 M196,110 Q195,86 200,62" fill="none" '
             f'stroke="{HD}" stroke-width="2"/>')
    hl = (f'<path d="M142,116 Q200,90 258,116" fill="none" stroke="{c["hairL"]}" stroke-width="7" '
          f'stroke-linecap="round" opacity=".85"/>')
    return _wrap(f'<g stroke="{LINE}" stroke-width="3" stroke-linejoin="round">{front}{acc}</g>{hl}')


# ---------------------------------------------------------------- 一括
def layers(char_id):
    """{ファイル名(拡張子なし): svg文字列} を返す。"""
    c = CH[char_id]
    out = {"base_back": base_back_svg(c), "base_front": base_front_svg(c), "blush": blush_svg()}
    for k in EYE_KINDS:
        out[f"eyes_{k}"] = eye_svg(c, k)
    for k in MOUTH_KINDS:
        out[f"mouth_{k}"] = mouth_svg(k)
    for k in BROW_KINDS:
        out[f"brows_{k}"] = brow_svg(c, k)
    return out


def flat(char_id, eyes="open", mouth="smile", brows="normal", blush=False):
    """全レイヤーを正しい順で1枚にした SVG（CG・OP用）。"""
    import re
    c = CH[char_id]

    def inner(svg):
        m = re.match(r"<svg[^>]*>(.*)</svg>$", svg, re.S)
        return m.group(1)

    parts = [base_back_svg(c), eye_svg(c, eyes), mouth_svg(mouth)]
    if blush:
        parts.append(blush_svg())
    parts += [base_front_svg(c), brow_svg(c, brows)]
    # defs（グラデ/クリップ）は eye_svg だけが持つので、そのまま連結して OK
    return _wrap("".join(inner(p) for p in parts))
