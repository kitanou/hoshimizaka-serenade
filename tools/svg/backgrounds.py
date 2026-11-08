"""背景 SVG（640x480）。index.html の bgSlope/bgClass/bgRoof/bgNight の移植＋新規。"""

W, H = 640, 480


def _svg(body, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
            f'<defs>{defs}</defs>{body}</svg>')


def _grad(gid, stops):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    return f'<linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">{s}</linearGradient>'


def black():
    return _svg('<rect width="640" height="480" fill="#000"/>')


# ------------------------------------------------------------ 坂道
def slope(mode="morning"):
    S = mode in ("sunset", "night")
    N = mode == "night"
    if N:
        P = dict(sky=[(0, "#04061e"), (.6, "#18286a"), (1, "#3a3c8a")], sea="#1c2a66", glint="#8fa8ff",
                 town="#1a1c44", road="#2a2a46", walk="#3a3a5e", tree="#7a5a9a", treeD="#4a3a74",
                 house="#2a2a4e", roof="#14142e", cloud="#3a3c7a", win="#ffd36b")
    elif S:
        P = dict(sky=[(0, "#352a78"), (.55, "#d8607a"), (1, "#ffc27a")], sea="#c45a78", glint="#ffe0a0",
                 town="#5a3466", road="#6e566a", walk="#a07a86", tree="#ff9fb6", treeD="#c8527a",
                 house="#8c5a6c", roof="#43274a", cloud="#ffb7a6", win="#ffd36b")
    else:
        P = dict(sky=[(0, "#4aa8ff"), (1, "#e2f6ff")], sea="#3a92d4", glint="#e6f6ff",
                 town="#97afd0", road="#9696a6", walk="#d8cdbb", tree="#ffc4d6", treeD="#f08eb0",
                 house="#f4e8da", roof="#5d74ad", cloud="#fff", win="#9fd2f0")
    stars = ""
    if N:
        for i in range(70):
            x = (i * 137.5) % 640
            y = (i * 71.3) % 210
            stars += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{1.4 if i % 5 == 0 else .8}" fill="#fff" opacity=".8"/>'
    sun = ""
    if mode == "sunset":
        sun = '<circle cx="330" cy="212" r="46" fill="#ffe28e"/>'
    elif N:
        sun = '<circle cx="470" cy="90" r="26" fill="#fff6c8"/><circle cx="480" cy="84" r="24" fill="#18286a"/>'
    clouds = "" if N else (
        f'<g fill="{P["cloud"]}" opacity=".85"><ellipse cx="120" cy="84" rx="74" ry="16"/><ellipse cx="170" cy="70" rx="48" ry="18"/>'
        f'<ellipse cx="500" cy="118" rx="84" ry="14"/><ellipse cx="540" cy="104" rx="42" ry="16"/></g>')
    posts = ""
    for i in range(6):
        t = i / 6
        x = 560 - 208 * t
        y = 480 - 218 * t
        h = 34 * (1 - t) + 6
        posts += f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y + h}"/>'
    lamp_glow = ('<circle cx="195" cy="74" r="40" fill="#ffe8a0" opacity=".35"/>' if N else "")
    win_light = ""
    body = (
        f'<rect width="640" height="480" fill="url(#g)"/>{stars}{sun}{clouds}'
        f'<rect y="214" width="640" height="42" fill="{P["sea"]}"/>'
        f'<g stroke="{P["glint"]}" stroke-width="2" opacity=".8"><line x1="296" y1="226" x2="364" y2="226"/>'
        f'<line x1="276" y1="236" x2="384" y2="236"/><line x1="100" y1="232" x2="140" y2="232"/>'
        f'<line x1="500" y1="242" x2="560" y2="242"/></g>'
        f'<path d="M0,256 L0,236 L30,236 L30,226 L60,226 L60,240 L90,240 L90,220 L110,220 L110,238 L150,238 L150,230 '
        f'L190,230 L190,244 L240,244 L240,236 L280,236 L280,256 Z" fill="{P["town"]}"/>'
        f'<path d="M360,256 L360,238 L400,238 L400,228 L430,228 L430,240 L470,240 L470,222 L500,222 L500,236 L540,236 '
        f'L540,230 L580,230 L580,242 L640,242 L640,256 Z" fill="{P["town"]}"/>'
        f'<rect y="256" width="640" height="224" fill="{P["walk"]}"/>'
        f'<path d="M96,480 L544,480 L344,256 L296,256 Z" fill="{P["road"]}"/>'
        f'<line x1="320" y1="480" x2="320" y2="258" stroke="#fff" stroke-width="4" stroke-dasharray="34 22" opacity=".75"/>'
        f'<g stroke="#3a3040" stroke-width="2"><path d="M560,480 L352,262" stroke="#e8e8f0" stroke-width="5"/>{posts}</g>'
        f'<g stroke="#3a3040" stroke-width="2.5">'
        f'<path d="M0,480 L0,300 L70,262 L140,300 L140,480 Z" fill="{P["house"]}"/>'
        f'<path d="M-10,304 L70,256 L150,304 L140,310 L70,270 L0,310 Z" fill="{P["roof"]}"/>'
        f'<rect x="22" y="330" width="34" height="30" fill="{P["win"]}"/><rect x="84" y="330" width="34" height="30" fill="{P["win"]}"/>'
        f'<path d="M640,480 L640,310 L560,276 L500,306 L500,480 Z" fill="{P["house"]}"/>'
        f'<path d="M650,314 L560,270 L490,310 L500,316 L560,284 L640,320 Z" fill="{P["roof"]}"/>'
        f'<rect x="520" y="336" width="30" height="28" fill="{P["win"]}"/><rect x="584" y="336" width="34" height="28" fill="{P["win"]}"/></g>'
        f'{lamp_glow}'
        f'<rect x="190" y="40" width="11" height="440" fill="#4a3a44"/><rect x="168" y="70" width="56" height="6" fill="#4a3a44"/>'
        f'<rect x="306" y="196" width="3" height="60" fill="#4a3a44"/>'
        f'<g fill="none" stroke="#2a2430" stroke-width="1.4"><path d="M172,74 Q250,150 307,200"/>'
        f'<path d="M220,74 Q270,140 308,198"/><path d="M0,120 Q90,110 172,74"/></g>'
        f'<rect x="592" y="90" width="18" height="230" fill="#6a4a4a" stroke="#3a3040" stroke-width="2"/>'
        f'<g fill="{P["tree"]}"><circle cx="560" cy="60" r="72"/><circle cx="640" cy="44" r="82"/><circle cx="496" cy="18" r="52"/>'
        f'<circle cx="40" cy="20" r="70"/><circle cx="128" cy="-4" r="60"/></g>'
        f'<g fill="{P["treeD"]}" opacity=".55"><circle cx="530" cy="96" r="20"/><circle cx="600" cy="110" r="26"/>'
        f'<circle cx="470" cy="44" r="14"/><circle cx="60" cy="70" r="22"/><circle cx="20" cy="50" r="14"/></g>')
    return _svg(body, _grad("g", P["sky"]))


# ------------------------------------------------------------ 教室
def classroom(evening=False):
    sky = [(0, "#5a3a8a"), (.6, "#ff8a6a"), (1, "#ffd28a")] if evening else [(0, "#5ab4ff"), (1, "#dff4ff")]

    def desk(x, y, s):
        return (f'<g transform="translate({x},{y}) scale({s})" stroke="#4a3a30" stroke-width="2">'
                f'<path d="M0,0 L120,0 L132,26 L-12,26 Z" fill="#dcb07a"/><rect x="-12" y="26" width="144" height="8" fill="#b8884e"/>'
                f'<path d="M4,34 L4,110 M116,34 L116,110" stroke="#77778a" stroke-width="6"/>'
                f'<rect x="10" y="34" width="100" height="34" fill="#9a9aae"/></g>')
    defs = _grad("g", sky) + '<clipPath id="w"><rect x="24" y="54" width="212" height="242"/></clipPath>'
    ev = '<rect width="640" height="480" fill="#ff6a20" opacity=".2"/>' if evening else ""
    body = (
        '<rect width="640" height="480" fill="#efe1c4"/><rect y="0" width="640" height="28" fill="#e2d2b2"/>'
        '<rect x="24" y="54" width="212" height="242" fill="url(#g)"/>'
        f'<g clip-path="url(#w)"><g fill="{"#e88aa0" if evening else "#ffc4d6"}"><circle cx="60" cy="300" r="60"/>'
        '<circle cx="150" cy="290" r="50"/><circle cx="230" cy="310" r="56"/></g>'
        f'<g fill="{"#fff0c0" if evening else "#fff"}" opacity=".7"><ellipse cx="90" cy="100" rx="50" ry="12"/>'
        '<ellipse cx="190" cy="140" rx="40" ry="10"/></g></g>'
        '<g fill="none" stroke="#8a7a66" stroke-width="8"><rect x="24" y="54" width="212" height="242"/>'
        '<line x1="130" y1="54" x2="130" y2="296"/><line x1="24" y1="176" x2="236" y2="176" stroke-width="5"/></g>'
        '<rect x="0" y="40" width="22" height="280" fill="#eef1f8" stroke="#bfc6d6" stroke-width="2"/>'
        '<rect x="284" y="78" width="336" height="166" fill="#2e5b45" stroke="#7a5a3a" stroke-width="10"/>'
        '<g fill="#f4f4e6"><rect x="310" y="104" width="120" height="6"/><rect x="310" y="130" width="200" height="5"/>'
        '<rect x="310" y="152" width="160" height="5"/><rect x="310" y="196" width="150" height="5"/></g>'
        '<rect x="290" y="244" width="324" height="7" fill="#9a7a52"/>'
        '<circle cx="452" cy="40" r="16" fill="#fff" stroke="#555" stroke-width="3"/><path d="M452,40 L452,30 M452,40 L460,44" stroke="#333" stroke-width="2"/>'
        '<rect y="356" width="640" height="124" fill="#b8875a"/>'
        '<g stroke="#9a6c42" stroke-width="2"><line x1="0" y1="380" x2="640" y2="380"/><line x1="0" y1="410" x2="640" y2="410"/>'
        '<line x1="0" y1="446" x2="640" y2="446"/></g>'
        + desk(300, 300, .7) + desk(420, 300, .7) + desk(540, 300, .7) + desk(20, 380, 1.1) + desk(470, 392, 1.1) + ev)
    return _svg(body, defs)


# ------------------------------------------------------------ 屋上
def rooftop(night=False):
    if night:
        sky = [(0, "#04061e"), (.7, "#18286a"), (1, "#3a3c8a")]
        town = "#0c0e2a"
        floor = "#2a2a44"
        mesh = "#14142e"
        stars = ""
        for i in range(90):
            x = (i * 137.5) % 640
            y = (i * 71.3) % 200
            stars += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{1.5 if i % 6 == 0 else .8}" fill="#fff" opacity=".85"/>'
        sun = '<circle cx="520" cy="96" r="28" fill="#fff6c8"/><circle cx="531" cy="90" r="26" fill="#18286a"/>'
        streaks = ""
        lights = "".join(f'<rect x="{(i * 47) % 600 + 14}" y="{286 + (i * 13) % 18}" width="3" height="3" fill="#ffd36b"/>' for i in range(22))
    else:
        sky = [(0, "#2a2868"), (.45, "#c25a86"), (.75, "#ff8a5a"), (1, "#ffd27a")]
        town = "#4a2c54"
        floor = "#8a7f92"
        mesh = "#3a2c40"
        stars = ""
        sun = '<circle cx="440" cy="300" r="54" fill="#ffe59a"/>'
        streaks = ('<g fill="#ffb08e" opacity=".55"><rect x="40" y="150" width="260" height="6" rx="3"/>'
                   '<rect x="380" y="200" width="220" height="5" rx="3"/><rect x="120" y="240" width="160" height="4" rx="2"/></g>')
        lights = ""
    defs = _grad("g", sky) + (
        f'<pattern id="m" width="18" height="18" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
        f'<rect width="18" height="18" fill="none" stroke="{mesh}" stroke-width="1.6"/></pattern>')
    tele = ""
    if night:
        tele = ('<g stroke="#1a1a30" stroke-width="2.5"><path d="M300,420 L270,480 M300,420 L330,480 M300,420 L300,480" stroke-width="4" fill="none"/>'
                '<rect x="262" y="368" width="96" height="22" rx="8" transform="rotate(-38 300 420)" fill="#d8d8ec"/>'
                '<circle cx="300" cy="420" r="9" fill="#9a9ab8"/></g>')
    body = (
        f'<rect width="640" height="480" fill="url(#g)"/>{stars}{sun}{streaks}'
        f'<path d="M0,330 L0,300 L40,300 L40,284 L80,284 L80,306 L130,306 L130,276 L160,276 L160,300 L220,300 L220,290 '
        f'L280,290 L280,310 L360,310 L360,288 L400,288 L400,304 L470,304 L470,280 L510,280 L510,300 L580,300 L580,292 '
        f'L640,292 L640,330 Z" fill="{town}"/>{lights}'
        f'<rect y="330" width="640" height="150" fill="{floor}"/>'
        f'<g stroke="#6a6074" stroke-width="2"><line x1="0" y1="370" x2="640" y2="370"/><line x1="0" y1="420" x2="640" y2="420"/>'
        f'<line x1="160" y1="330" x2="100" y2="480"/><line x1="480" y1="330" x2="540" y2="480"/></g>'
        f'<rect x="0" y="196" width="640" height="140" fill="url(#m)"/>'
        f'<g stroke="{mesh}" stroke-width="5"><line x1="0" y1="196" x2="640" y2="196"/><line x1="0" y1="336" x2="640" y2="336"/>'
        + "".join(f'<line x1="{i * 80}" y1="196" x2="{i * 80}" y2="336"/>' for i in range(9)) + '</g>'
        f'<g stroke="{mesh}" stroke-width="2.5"><rect x="520" y="150" width="96" height="70" rx="10" fill="#c8c0d0"/>'
        f'<ellipse cx="568" cy="150" rx="48" ry="10" fill="#dcd4e4"/><path d="M532,220 L528,300 M604,220 L608,300" stroke-width="6"/></g>'
        + tele)
    return _svg(body, defs)


# ------------------------------------------------------------ 夜空
def night(hill=True):
    st = ""
    for i in range(120):
        x = (i * 137.5) % 640
        y = (i * 71.3) % 330
        r = 1.8 if i % 7 == 0 else (1.1 if i % 3 == 0 else .7)
        st += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#fff" opacity="{.4 + (i % 5) / 8:.2f}"/>'
    hill_svg = ""
    if hill:
        lights = "".join(f'<rect x="{(i * 53) % 600 + 10}" y="{420 + (i * 17) % 50}" width="3" height="3"/>' for i in range(26))
        hill_svg = ('<path d="M0,480 L0,380 C120,340 220,330 330,350 C440,370 540,360 640,330 L640,480 Z" fill="#0a0c24"/>'
                    f'<g fill="#ffd36b">{lights}</g>')
    body = f'<rect width="640" height="480" fill="url(#g)"/>{st}{hill_svg}'
    return _svg(body, _grad("g", [(0, "#04061e"), (.7, "#18286a"), (1, "#3a3c8a")]))


# ------------------------------------------------------------ 廊下
def hallway():
    wins = ""
    for i in range(4):
        x = 30 + i * 150
        wins += (f'<rect x="{x}" y="70" width="110" height="170" fill="#bfe4ff" stroke="#8a7a66" stroke-width="6"/>'
                 f'<line x1="{x + 55}" y1="70" x2="{x + 55}" y2="240" stroke="#8a7a66" stroke-width="4"/>'
                 f'<ellipse cx="{x + 30}" cy="110" rx="26" ry="8" fill="#fff" opacity=".8"/>')
    lockers = "".join(f'<rect x="{i * 40}" y="250" width="38" height="90" fill="#9fb0c8" stroke="#6a7890" stroke-width="2"/>' for i in range(16))
    body = (
        '<rect width="640" height="480" fill="#efe4cc"/><rect y="0" width="640" height="50" fill="#e0d4b8"/>'
        '<rect y="50" width="640" height="200" fill="#f4ecd8"/>' + wins + lockers +
        '<rect y="340" width="640" height="140" fill="#c49a68"/>'
        '<path d="M0,480 L120,340 M640,480 L520,340 M320,480 L320,340" stroke="#a87c4a" stroke-width="3"/>'
        '<g stroke="#a87c4a" stroke-width="2"><line x1="0" y1="380" x2="640" y2="380"/><line x1="0" y1="430" x2="640" y2="430"/></g>'
        '<rect x="260" y="20" width="120" height="22" fill="#fff" stroke="#8a7a66" stroke-width="3"/>'
        '<rect width="640" height="480" fill="#ffe9b0" opacity=".12"/>')
    return _svg(body)


# ------------------------------------------------------------ 天文部室
def clubroom():
    stars = "".join(f'<circle cx="{(i * 83) % 600 + 20}" cy="{(i * 47) % 120 + 20}" r="1.6" fill="#ffe27a"/>' for i in range(14))
    body = (
        '<rect width="640" height="480" fill="#d8cdb8"/><rect y="0" width="640" height="40" fill="#c8bca4"/>'
        '<rect x="40" y="60" width="150" height="180" fill="#ffc88a" stroke="#7a5a3a" stroke-width="8"/>'
        '<line x1="115" y1="60" x2="115" y2="240" stroke="#7a5a3a" stroke-width="5"/>'
        '<rect x="250" y="50" width="340" height="210" fill="#1c2a5c" stroke="#7a5a3a" stroke-width="8"/>' + stars +
        '<circle cx="480" cy="140" r="38" fill="#f6e8a0"/><circle cx="494" cy="132" r="34" fill="#1c2a5c"/>'
        '<text x="282" y="236" font-size="16" fill="#cfe0ff" font-family="sans-serif">STAR CHART</text>'
        '<rect y="330" width="640" height="150" fill="#a98558"/>'
        '<g stroke="#8a6a40" stroke-width="2"><line x1="0" y1="370" x2="640" y2="370"/><line x1="0" y1="420" x2="640" y2="420"/></g>'
        '<rect x="70" y="270" width="500" height="26" fill="#cfa66c" stroke="#7a5a3a" stroke-width="3"/>'
        '<rect x="90" y="296" width="12" height="90" fill="#7a5a3a"/><rect x="540" y="296" width="12" height="90" fill="#7a5a3a"/>'
        '<rect x="120" y="236" width="70" height="34" fill="#8fb0d8" stroke="#4a6a98" stroke-width="2"/>'
        '<rect x="420" y="244" width="90" height="26" fill="#e8d8c0" stroke="#7a5a3a" stroke-width="2"/>'
        '<rect x="0" y="120" width="30" height="210" fill="#8a6a50" stroke="#5a3a2a" stroke-width="2"/>'
        '<rect width="640" height="480" fill="#ffd9a0" opacity=".1"/>')
    return _svg(body)


# ------------------------------------------------------------ 主人公の部屋・夜
def home():
    body = (
        '<rect width="640" height="480" fill="#2a2748"/><rect y="360" width="640" height="120" fill="#4a3a48"/>'
        '<rect x="380" y="70" width="190" height="200" fill="#10184a" stroke="#6a5a78" stroke-width="8"/>'
        '<line x1="475" y1="70" x2="475" y2="270" stroke="#6a5a78" stroke-width="5"/>'
        + "".join(f'<circle cx="{390 + (i * 37) % 170}" cy="{80 + (i * 23) % 130}" r="1.4" fill="#fff"/>' for i in range(18)) +
        '<circle cx="440" cy="120" r="14" fill="#fff6c8"/>'
        '<rect x="30" y="250" width="280" height="140" rx="10" fill="#7a8ac8" stroke="#3a3a68" stroke-width="3"/>'
        '<rect x="40" y="240" width="110" height="46" rx="14" fill="#f4eef8" stroke="#3a3a68" stroke-width="3"/>'
        '<rect x="400" y="300" width="200" height="16" fill="#8a6a50"/><rect x="410" y="316" width="10" height="70" fill="#6a4a38"/>'
        '<rect x="570" y="316" width="10" height="70" fill="#6a4a38"/>'
        '<rect x="430" y="262" width="80" height="38" rx="3" fill="#bfe8ff" stroke="#3a3a68" stroke-width="3"/>'
        '<rect width="640" height="480" fill="#000" opacity=".25"/>')
    return _svg(body)


ALL = {
    "black": black,
    "slope": lambda: slope("morning"),
    "slope_sunset": lambda: slope("sunset"),
    "slope_night": lambda: slope("night"),
    "classroom": lambda: classroom(False),
    "classroom_evening": lambda: classroom(True),
    "rooftop": lambda: rooftop(False),
    "rooftop_night": lambda: rooftop(True),
    "night": lambda: night(True),
    "hallway": hallway,
    "clubroom": clubroom,
    "home": home,
}
