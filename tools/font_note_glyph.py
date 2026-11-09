"""SourceHanSansLite.ttf への ♪（U+266A）グリフ注入（#81 歌詞 ♪ マーカー用）。

歌词字幕の行頭 ♪（歌唱中マーカー）は SubSet フォントにグリフが無かったため、
自作のオリジナルグリフ（8分音符）を注入する。権利方針（docs/demo-design.md §権利確認:
バンドルは SIL OFL または本リポジトリ手続き生成のみ）に合わせ、他フォントから
コピーせず vector データは本スクリプトで生成している。

usage: python -m tools.font_note_glyph
（冪等: 既に U+266A が入っていれば何もしない。フォント更新・再サブセット後の再実行用）
"""
import math
import os

from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.path.join(ROOT, "hoshimizaka", "game", "fonts", "SourceHanSansLite.ttf")

GNAME = "note8th"


def signed_area(pts):
    s = 0.0
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        s += x1 * y2 - x2 * y1
    return s / 2.0


def ensure_cw(pts):
    """TrueType の外輪郭は時計回り（y-up で負面積）。"""
    pts = [(round(x), round(y)) for x, y in pts]
    if signed_area(pts) > 0:
        pts.reverse()
    return pts


def ring(cx, cy, rx, ry, rot=0.0, n=16):
    out = []
    cr, sr = math.cos(rot), math.sin(rot)
    for i in range(n):
        a = 2 * math.pi * i / n
        x, y = rx * math.cos(a), ry * math.sin(a)
        out.append((cx + x * cr - y * sr, cy + x * sr + y * cr))
    return out


def build_glyph():
    """♪（8分音符）。UPM=1000、基準線 y=0。符頭＋軸＋はためきの 3 輪郭（同順でunion）。"""
    head = ring(268, 150, 116, 84, rot=math.radians(-14))
    stem = [(348, 150), (348, 668), (430, 668), (430, 150)]
    flag = [(430, 674), (506, 652), (578, 598), (614, 520),
            (585, 552), (520, 594), (430, 612)]
    pen = TTGlyphPen(None)
    for pts in (head, stem, flag):
        pts = ensure_cw(pts)
        pen.moveTo(pts[0])
        for q in pts[1:]:
            pen.lineTo(q)
        pen.closePath()
    return pen.glyph(), len(head) + len(stem) + len(flag)


def main():
    f = TTFont(FONT)
    if 0x266A in f.getBestCmap():
        print("U+266A 済み（変更不要）")
        return
    g, npts = build_glyph()
    glyf = f["glyf"]
    order = f.getGlyphOrder()
    order.append(GNAME)
    f.setGlyphOrder(order)
    glyf.glyphOrder = order
    glyf.glyphs[GNAME] = g
    f["hmtx"].metrics[GNAME] = (700, 0)
    mp = f["maxp"]
    mp.maxContours = max(mp.maxContours, 3)
    mp.maxPoints = max(mp.maxPoints, npts)
    for t in f["cmap"].tables:
        if isinstance(getattr(t, "cmap", None), dict):
            t.cmap[0x266A] = GNAME
    f.save(FONT)
    print(f"injected {GNAME} (U+266A) -> {os.path.relpath(FONT, ROOT)}")


if __name__ == "__main__":
    main()
