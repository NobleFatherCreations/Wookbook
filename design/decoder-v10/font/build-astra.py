#!/usr/bin/env python3
"""Astra: an original monoline display typeface for the Pattern Decoder.

Run from the repo root:  python3 design/decoder-v10/font/build-astra.py
Needs fontTools + brotli (pip install fonttools brotli). Writes woff2 files to
design/decoder-v10/assets/ (astra-light.woff2, astra-medium.woff2) and a
specimen to design/decoder-v10/font/specimen.html.

Every glyph is a skeleton: straight lines and elliptical arcs on a 1000-unit em
(baseline 0, x-height 500, cap height 700, ascender 740, descender -210). The
builder strokes each skeleton with round caps at a chosen weight and emits one
overlapping contour per chain. The dots of i, j and all punctuation are small
four-point stars: the letters are drawn like constellations, joined points of
light, which is the idea behind the whole product.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.environ.get("ASTRA_PYLIB", ""))
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.agl import UV2AGL


def gname(ch):
    return UV2AGL.get(ord(ch)) or "uni%04X" % ord(ch)


EM = 1000


def arc(cx, cy, rx, ry, a0, a1, step=5):
    n = max(2, int(abs(a1 - a0) / step) + 1)
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / (n - 1))),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / (n - 1)))) for i in range(n)]


def join(*parts):
    out = []
    for p in parts:
        for pt in p:
            if not out or abs(out[-1][0] - pt[0]) + abs(out[-1][1] - pt[1]) > 0.5:
                out.append(pt)
    return out


L = lambda *pts: list(pts)
STAR = "star"

# ---- the alphabet: each glyph is (strokes, stars). strokes are polylines; stars are centres.
G = {}


def circle(cx, cy, rx, ry):
    return arc(cx, cy, rx, ry, 90, 450)


# lowercase
G["o"] = ([circle(250, 250, 250, 250)], [])
G["c"] = ([arc(270, 250, 250, 250, 45, 315)], [])
G["e"] = ([join(L((0, 250), (500, 250)), arc(250, 250, 250, 250, 0, 325))], [])
G["a"] = ([circle(250, 250, 250, 250), L((500, 500), (500, 0))], [])
G["d"] = ([circle(250, 250, 250, 250), L((500, 740), (500, 0))], [])
G["b"] = ([circle(250, 250, 250, 250), L((0, 740), (0, 0))], [])
G["p"] = ([circle(250, 250, 250, 250), L((0, 500), (0, -210))], [])
G["q"] = ([circle(250, 250, 250, 250), L((500, 500), (500, -210))], [])
G["g"] = ([circle(250, 250, 250, 250), join(L((500, 500), (500, -40)), arc(250, -40, 250, 170, 0, -150))], [])
G["n"] = ([join(L((0, 0), (0, 500)), L((0, 250)), arc(250, 250, 250, 250, 180, 0), L((500, 0)))], [])
G["m"] = ([join(L((0, 0), (0, 500)), L((0, 335)), arc(165, 335, 165, 165, 180, 0), L((330, 0))),
           join(L((330, 335)), arc(495, 335, 165, 165, 180, 0), L((660, 0)))], [])
G["h"] = ([join(L((0, 0), (0, 740)), L((0, 250)), arc(250, 250, 250, 250, 180, 0), L((500, 0)))], [])
G["r"] = ([L((0, 0), (0, 500)), join(L((0, 270)), arc(230, 270, 230, 230, 180, 70))], [])
G["u"] = ([join(L((0, 500), (0, 250)), arc(250, 250, 250, 250, 180, 360)), L((500, 500), (500, 0))], [])
G["v"] = ([L((0, 500), (250, 0), (500, 500))], [])
G["w"] = ([L((0, 500), (170, 0), (340, 500), (510, 0), (680, 500))], [])
G["x"] = ([L((0, 500), (500, 0)), L((500, 500), (0, 0))], [])
G["y"] = ([L((0, 500), (250, 0)), L((500, 500), (145, -210))], [])
G["z"] = ([L((0, 500), (500, 500), (0, 0), (500, 0))], [])
G["i"] = ([L((0, 0), (0, 500))], [(0, 705)])
G["j"] = ([join(L((0, 500), (0, -40)), arc(-170, -40, 170, 170, 0, -120))], [(0, 705)])
G["k"] = ([L((0, 0), (0, 740)), L((440, 500), (0, 180)), L((220, 340), (460, 0))], [])
G["l"] = ([L((0, 0), (0, 740))], [])
G["t"] = ([join(L((140, 640), (140, 200)), arc(340, 200, 200, 200, 180, 270)), L((0, 500), (330, 500))], [])
G["f"] = ([join(L((150, 0), (150, 560)), arc(330, 560, 180, 180, 180, 60)), L((0, 500), (330, 500))], [])
G["s"] = ([join(arc(250, 375, 215, 125, 25, 270), arc(250, 125, 215, 125, 90, -160))], [])
G["é"] = (G["e"][0] + [L((190, 590), (310, 730))], [])

# capitals
G["A"] = ([L((0, 0), (250, 700), (500, 0)), L((95, 235), (405, 235))], [])
G["B"] = ([L((0, 0), (0, 700)),
           join(L((0, 700), (200, 700)), arc(200, 525, 190, 175, 90, -90), L((0, 350))),
           join(L((200, 350)), arc(220, 175, 215, 175, 90, -90), L((0, 0)))], [])
G["C"] = ([arc(330, 350, 330, 350, 45, 315)], [])
G["D"] = ([join(L((0, 700), (0, 0)), L((180, 0)), arc(180, 350, 340, 350, -90, 90), L((0, 700)))], [])
G["E"] = ([L((430, 700), (0, 700), (0, 0), (430, 0)), L((0, 350), (360, 350))], [])
G["F"] = ([L((430, 700), (0, 700), (0, 0)), L((0, 350), (360, 350))], [])
G["G"] = ([join(arc(330, 350, 330, 350, 45, 360), L((380, 350)))], [])
G["H"] = ([L((0, 0), (0, 700)), L((500, 0), (500, 700)), L((0, 350), (500, 350))], [])
G["I"] = ([L((0, 0), (0, 700))], [])
G["J"] = ([join(L((330, 700), (330, 200)), arc(150, 200, 180, 180, 0, -180))], [])
G["K"] = ([L((0, 0), (0, 700)), L((450, 700), (0, 240)), L((140, 376), (470, 0))], [])
G["L"] = ([L((0, 700), (0, 0), (400, 0))], [])
G["M"] = ([L((0, 0), (0, 700), (300, 110), (600, 700), (600, 0))], [])
G["N"] = ([L((0, 0), (0, 700), (520, 0), (520, 700))], [])
G["O"] = ([circle(340, 350, 340, 350)], [])
G["P"] = ([L((0, 0), (0, 700)), join(L((0, 700), (210, 700)), arc(210, 490, 215, 210, 90, -90), L((0, 280)))], [])
G["Q"] = ([circle(340, 350, 340, 350), L((420, 170), (640, -70))], [])
G["R"] = ([L((0, 0), (0, 700)), join(L((0, 700), (210, 700)), arc(210, 490, 215, 210, 90, -90), L((0, 280))), L((230, 280), (480, 0))], [])
G["S"] = ([join(arc(250, 525, 230, 175, 25, 270), arc(250, 175, 230, 175, 90, -160))], [])
G["T"] = ([L((0, 700), (520, 700)), L((260, 700), (260, 0))], [])
G["U"] = ([join(L((0, 700), (0, 250)), arc(250, 250, 250, 250, 180, 360), L((500, 700)))], [])
G["V"] = ([L((0, 700), (260, 0), (520, 700))], [])
G["W"] = ([L((0, 700), (170, 0), (340, 520), (510, 0), (680, 700))], [])
G["X"] = ([L((0, 700), (500, 0)), L((500, 700), (0, 0))], [])
G["Y"] = ([L((0, 700), (260, 330), (520, 700)), L((260, 330), (260, 0))], [])
G["Z"] = ([L((0, 700), (500, 700), (0, 0), (500, 0))], [])

# digits
G["0"] = ([circle(240, 350, 240, 350)], [])
G["1"] = ([L((60, 560), (260, 700), (260, 0))], [])
G["2"] = ([join(arc(240, 490, 230, 210, 160, -40), L((0, 0), (480, 0)))], [])
G["3"] = ([join(arc(225, 520, 215, 180, 150, -90), arc(230, 170, 240, 170, 90, -150))], [])
G["4"] = ([L((360, 0), (360, 700), (0, 200), (500, 200))], [])
G["5"] = ([join(L((440, 700), (70, 700), (45, 400)), arc(235, 240, 245, 240, 135, -145))], [])
six = [circle(240, 240, 240, 240), join(arc(440, 300, 440, 400, 100, 180), L((0, 240)))]
G["6"] = (six, [])
G["7"] = ([L((0, 700), (480, 700), (150, 0))], [])
G["8"] = ([circle(230, 525, 205, 175), circle(240, 190, 240, 190)], [])
G["9"] = ([[(480 - x, 700 - y) for x, y in s] for s in six], [])

# punctuation
G["."] = ([], [(0, 88, 1.45)])
G[","] = ([L((10, 60), (-45, -130))], [])
G[":"] = ([], [(0, 88, 1.3), (0, 440, 1.3)])
G[";"] = ([L((10, 60), (-45, -130))], [(10, 440, 1.3)])
G["!"] = ([L((0, 700), (0, 250))], [(0, 88, 1.35)])
G["?"] = ([join(arc(215, 490, 215, 210, 170, -90), L((215, 280), (215, 190)))], [(215, 80, 1.35)])
G["-"] = ([L((0, 260), (260, 260))], [])
G["–"] = ([L((0, 260), (480, 260))], [])
G["—"] = ([L((0, 260), (880, 260))], [])
G["’"] = ([L((50, 700), (5, 540))], [])
G["'"] = G["’"]
G["‘"] = ([L((50, 700), (5, 540))], [])
G["“"] = ([L((50, 700), (5, 540)), L((200, 700), (155, 540))], [])
G["”"] = G["“"]
G['"'] = G["“"]
G["("] = ([arc(420, 250, 330, 500, 125, 235)], [])
G[")"] = ([arc(-20, 250, 330, 500, 55, -55)], [])
G["/"] = ([L((0, -100), (330, 760))], [])

SIDE = {"A": 25, "V": 25, "W": 25, "X": 25, "Y": 25, "T": 30, "v": 30, "w": 30, "x": 30, "y": 30,
        "1": 100, "I": 110, "i": 110, "l": 110, "j": 90, ".": 110, ",": 110, ":": 110, ";": 110, "!": 110,
        "’": 80, "'": 80, "‘": 80, "“": 80, "”": 80, '"': 80, "(": 70, ")": 70, "-": 70, "–": 40, "—": 40, "f": 20, "r": 40}


def star_poly(cx, cy, R):
    pts = []
    for i in range(8):
        a = math.pi / 2 + i * math.pi / 4
        r = R if i % 2 == 0 else R * 0.3
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def split_corners(pts, ang=30):
    chains, cur = [], [pts[0]]
    for i in range(1, len(pts)):
        cur.append(pts[i])
        if 0 < i < len(pts) - 1:
            a = (pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1])
            b = (pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1])
            na, nb = math.hypot(*a), math.hypot(*b)
            if na and nb:
                cosv = max(-1, min(1, (a[0] * b[0] + a[1] * b[1]) / (na * nb)))
                if math.degrees(math.acos(cosv)) > ang:
                    chains.append(cur)
                    cur = [pts[i]]
    chains.append(cur)
    return [c for c in chains if len(c) >= 2]


def stroke_polygon(pts, w):
    h = w / 2
    n = len(pts)
    norms = []
    for i in range(n):
        if i == 0:
            d = (pts[1][0] - pts[0][0], pts[1][1] - pts[0][1])
        elif i == n - 1:
            d = (pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1])
        else:
            d1 = (pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1])
            d2 = (pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1])
            l1, l2 = math.hypot(*d1) or 1, math.hypot(*d2) or 1
            d = (d1[0] / l1 + d2[0] / l2, d1[1] / l1 + d2[1] / l2)
        l = math.hypot(*d) or 1
        norms.append((-d[1] / l, d[0] / l))
    left = [(p[0] + nx * h, p[1] + ny * h) for p, (nx, ny) in zip(pts, norms)]
    right = [(p[0] - nx * h, p[1] - ny * h) for p, (nx, ny) in zip(pts, norms)]

    def cap(c, nrm, sign):
        ang0 = math.atan2(nrm[1], nrm[0])
        return [(c[0] + h * math.cos(ang0 - sign * math.pi * k / 10), c[1] + h * math.sin(ang0 - sign * math.pi * k / 10)) for k in range(1, 10)]
    end_cap = cap(pts[-1], norms[-1], 1)
    start_cap = cap(pts[0], (-norms[0][0], -norms[0][1]), 1)
    return left + end_cap + right[::-1] + start_cap


def orient(poly):
    a = sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly)))
    return poly if a < 0 else poly[::-1]            # clockwise outer contours (TrueType)


def glyph_contours(name, w):
    strokes, stars = G[name]
    polys = []
    for s in strokes:
        if len(s) == 2 and s[0] == s[1]:
            polys.append(stroke_polygon([(s[0][0], s[0][1]), (s[0][0] + 0.1, s[0][1])], w))
            continue
        for ch in split_corners(s):
            polys.append(stroke_polygon(ch, w))
    for c in stars:
        polys.append(star_poly(c[0], c[1], (92 + w * .6) * (c[2] if len(c) > 2 else 1)))
    return [orient(p) for p in polys]


def build(weight_name, w, out):
    glyph_order = [".notdef", "space"] + [gname(c) for c in G.keys()]
    cmap, glyphs, metrics = {32: "space"}, {}, {}
    pen = TTGlyphPen(None)
    glyphs[".notdef"] = pen.glyph(); metrics[".notdef"] = (500, 0)
    pen = TTGlyphPen(None); glyphs["space"] = pen.glyph(); metrics["space"] = (int(260 + w * 2), 0)
    # centreline bounds -> sidebearings
    for name in G:
        polys = glyph_contours(name, w)
        xs = [p[0] for poly in polys for p in poly]
        xmin, xmax = min(xs), max(xs)
        sb = SIDE.get(name, 70)
        dx = sb - xmin
        pen = TTGlyphPen(None)
        for poly in polys:
            pts = [(round(x + dx), round(y)) for x, y in poly]
            pen.moveTo(pts[0])
            for p in pts[1:]:
                pen.lineTo(p)
            pen.closePath()
        g = pen.glyph()
        glyphs[gname(name)] = g
        metrics[gname(name)] = (int(xmax - xmin + 2 * sb), sb)
        cmap[ord(name)] = gname(name)
    fb = FontBuilder(EM, isTTF=True)
    fb.setupGlyphOrder(glyph_order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyphs)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=800, descent=-260)
    fb.setupNameTable({"familyName": "Astra Display", "styleName": weight_name,
                       "copyright": "Astra Display, drawn for the Pattern Decoder. Original work.",
                       "uniqueFontIdentifier": "AstraDisplay-" + weight_name, "fullName": "Astra Display " + weight_name,
                       "psName": "AstraDisplay-" + weight_name, "version": "Version 1.000"})
    fb.setupOS2(sTypoAscender=800, sTypoDescender=-260, sTypoLineGap=0, usWinAscent=900, usWinDescent=300,
                sxHeight=500, sCapHeight=700, usWeightClass=300 if w < 60 else 500, fsType=0)
    fb.setupPost()
    font = fb.font
    for gn in font["glyf"].keys():
        g = font["glyf"][gn]
        if g.numberOfContours > 0:
            g.flags[0] |= 0x40                      # OVERLAP_SIMPLE: contours overlap, fill non-zero
    font.flavor = "woff2"
    font.save(out)
    return os.path.getsize(out)


if __name__ == "__main__":
    assets = os.path.join(HERE, "..", "assets")
    os.makedirs(assets, exist_ok=True)
    for nm, w in (("Light", 44), ("Medium", 84)):
        out = os.path.join(assets, "astra-%s.woff2" % nm.lower())
        print(nm, w, build(nm, w, out) // 1024, "KB", os.path.relpath(out))
