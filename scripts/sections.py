#!/usr/bin/env python3
"""Reads profile.json and writes assets/section-<id>-dark.svg / -light.svg (acid-lime editorial cards)."""
import json, os, sys, textwrap
from xml.sax.saxutils import escape as E
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stats import DARK, LIGHT

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SRC = os.path.join(ROOT, "profile.json")
OUT = sys.argv[1] if len(sys.argv) > 1 else "assets"
DARK = {**DARK, "body": "#E8EBDD", "pill": "#171B14"}
LIGHT = {**LIGHT, "body": "#20241A", "pill": "#F0F2E9"}
W, RX, RW, CW = 1180, 350, 790, 9.0

def T(x, y, s, fs, fill, w="normal", ls=0, a="start"):
    return f'<text x="{x}" y="{y}" class="m" font-size="{fs}" font-weight="{w}" letter-spacing="{ls}" fill="{fill}" text-anchor="{a}">{s}</text>'

def wrap(s, width): return textwrap.wrap(s, width) or [""]

def right(sec, t, y0):
    o, y = [], y0
    kind = sec["type"]
    if kind == "text":
        for p in sec["paragraphs"]:
            for ln in wrap(p, int(RW / CW) - 4):
                o.append(T(RX, y + 16, E(ln), 15, t["body"])); y += 27
            y += 12
        y -= 12
    elif kind == "list":
        for it in sec["items"]:
            o.append(f'<rect x="{RX}" y="{y+5}" width="7" height="7" fill="{t["lime"]}"/>')
            if "lead" in it:
                o.append(T(RX + 24, y + 16, E(it["lead"]), 15, t["text"], "bold")); y += 24
                for ln in wrap(it["text"], int((RW - 24) / CW) - 4):
                    o.append(T(RX + 24, y + 14, E(ln), 14, t["muted"])); y += 23
                y += 14
            else:
                for ln in wrap(it["text"], int((RW - 24) / CW) - 4):
                    o.append(T(RX + 24, y + 16, E(ln), 15, t["body"])); y += 26
                y += 8
        y -= 8
    elif kind == "groups":
        for g in sec["groups"]:
            px, py, first = RX + 130, y, True
            o.append(T(RX, y + 17, E(g["name"].upper()), 10, t["limeT"], ls=2))
            for item in g["items"]:
                w = len(item) * 6.7 + 34
                if px + w > RX + RW: px, py = RX + 130, py + 34
                o.append(f'<rect x="{px:.1f}" y="{py}" width="{w:.1f}" height="26" rx="13" fill="{t["pill"]}" fill-opacity=".8" stroke="{t["lb"]}"/>'
                         f'<circle cx="{px+15:.1f}" cy="{py+13}" r="3" fill="{t["lime"]}"/>{T(f"{px+26:.1f}", py+17, E(item), 11, t["body"])}')
                px += w + 10
            y = py + 26 + 16
        y -= 16
    return o, y - y0

def render(sec, t):
    top = 84
    ro, rh = right(sec, t, top)
    lo, y = [], top
    if sec.get("kicker"):
        lo.append(T(40, y + 8, E(sec["kicker"]), 10, t["limeT"], ls=3)); y += 18
    for ln in wrap(sec["heading"], 14):
        lo.append(T(40, y + 30, E(ln), 28, t["text"], "bold")); y += 36
    H = int(top + max(rh, y - top) + 40)
    txt = sec["heading"] + ". " + " ".join(sec.get("paragraphs", []) + [(i.get("lead", "") + " " + i["text"]) for i in sec.get("items", [])]
                                        + [g["name"] + ": " + ", ".join(g["items"]) for g in sec.get("groups", [])])
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{E(txt, {chr(34): "&quot;"})}">',
         f'<title>{E(sec["heading"])}</title><style>.m{{font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace}}</style>',
         f'<defs><radialGradient id="g" cx="30%" cy="0%" r="110%"><stop offset="0" stop-color="{t["bg1"]}"/><stop offset="1" stop-color="{t["bg0"]}"/></radialGradient></defs>',
         f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="22" fill="url(#g)" stroke="{t["lb"]}"/>',
         f'<path d="M1 40V23a22 22 0 0 1 22-22H{W-23}a22 22 0 0 1 22 22V40Z" fill="#090B08"/>']
    for cx, c in [(26, "#C6FF00"), (44, "#596B1D"), (62, "#4A5043")]: o.append(f'<circle cx="{cx}" cy="21" r="5" fill="{c}"/>')
    o.append(T(W / 2, 25, E(sec.get("file", sec["id"].upper())), 11, t["chromeT"], ls=3, a="middle"))
    o.append(T(W - 24, 25, "profile.json", 10, t["chromeT"], ls=2, a="end"))
    o.append(f'<line x1="{RX-28}" y1="{top}" x2="{RX-28}" y2="{H-40}" stroke="{t["border"]}"/>')
    return "\n".join(o + lo + ro + ["</svg>"])

if __name__ == "__main__":
    data = json.load(open(SRC, encoding="utf-8"))
    os.makedirs(OUT, exist_ok=True)
    for sec in data["sections"]:
        for name, t in (("dark", DARK), ("light", LIGHT)):
            open(f"{OUT}/section-{sec['id']}-{name}.svg", "w", encoding="utf-8").write(render(sec, t))
    print("wrote", [s["id"] for s in data["sections"]])
