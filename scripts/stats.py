#!/usr/bin/env python3
"""Generate themed (acid lime) activity cards: assets/stats-dark.svg and assets/stats-light.svg.
Uses GITHUB_TOKEN (GraphQL, includes contributions) when present, else public REST (no contributions)."""
import os, sys, json, urllib.request
from collections import Counter
from xml.sax.saxutils import escape as E

USER = os.environ.get("GH_USER", "j-xingh")
TOK = os.environ.get("GITHUB_TOKEN")
OUT = sys.argv[1] if len(sys.argv) > 1 else "assets"

def req(url, data=None):
    h = {"User-Agent": "profile-stats", "Accept": "application/vnd.github+json"}
    if TOK: h["Authorization"] = f"Bearer {TOK}"
    r = urllib.request.Request(url, data=data, headers=h)
    return json.load(urllib.request.urlopen(r, timeout=30))

def fetch():
    m, langs = [], Counter()
    if TOK:
        q = """query($u:String!){user(login:$u){followers{totalCount}
          repositories(ownerAffiliations:OWNER,isFork:false,privacy:PUBLIC,first:100){totalCount nodes{stargazerCount primaryLanguage{name}}}
          contributionsCollection{totalCommitContributions totalPullRequestContributions
          contributionCalendar{totalContributions}}}}"""
        u = req("https://api.github.com/graphql", json.dumps({"query": q, "variables": {"u": USER}}).encode())["data"]["user"]
        nodes = u["repositories"]["nodes"]; c = u["contributionsCollection"]
        for n in nodes:
            if n["primaryLanguage"]: langs[n["primaryLanguage"]["name"]] += 1
        m = [("CONTRIBUTIONS / 1Y", c["contributionCalendar"]["totalContributions"]), ("COMMITS", c["totalCommitContributions"]),
             ("PULL REQUESTS", c["totalPullRequestContributions"]), ("STARS EARNED", sum(n["stargazerCount"] for n in nodes)),
             ("PUBLIC REPOS", u["repositories"]["totalCount"]), ("FOLLOWERS", u["followers"]["totalCount"])]
    else:
        p = req(f"https://api.github.com/users/{USER}")
        repos = [r for r in req(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner") if not r["fork"]]
        for r in repos:
            if r["language"]: langs[r["language"]] += 1
        m = [("STARS EARNED", sum(r["stargazers_count"] for r in repos)), ("PUBLIC REPOS", p["public_repos"]), ("FOLLOWERS", p["followers"])]
    tot = sum(langs.values()) or 1
    return m, [(k, v / tot * 100) for k, v in langs.most_common(5)]

DARK = dict(bg0="#050505", bg1="#0D100B", panel="#11140F", text="#F4F5EF", muted="#9CA392", lime="#C6FF00", limeT="#C6FF00",
            border="#272B24", lb="#39451A", chromeT="#9CA392", shades=["#C6FF00", "#A3D100", "#7E9E00", "#596B1D", "#39451A"], track="#171B14")
LIGHT = dict(bg0="#FAFAF6", bg1="#E9EDE1", panel="#FFFFFF", text="#11130D", muted="#626858", lime="#A8D900", limeT="#566D00",
             border="#D8DDCE", lb="#C8D0B8", chromeT="#C8CEBC", shades=["#566D00", "#6F8B00", "#91BD00", "#A8D900", "#C9E866"], track="#E3E8D6")

def card(t, metrics, langs):
    W, H = 1180, 250 if langs else 190
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="GitHub activity for {E(USER)}: '
         + ", ".join(f"{l.lower()} {v}" for l, v in metrics) + '">',
         f'<title>GitHub activity — {E(USER)}</title>',
         '<style>.m{font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace}</style>',
         f'<defs><radialGradient id="g" cx="30%" cy="10%" r="100%"><stop offset="0" stop-color="{t["bg1"]}"/><stop offset="1" stop-color="{t["bg0"]}"/></radialGradient></defs>',
         f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="22" fill="url(#g)" stroke="{t["lb"]}"/>',
         f'<path d="M1 40V23a22 22 0 0 1 22-22H{W-23}a22 22 0 0 1 22 22V40Z" fill="#090B08"/>']
    for cx, c in [(26, "#C6FF00"), (44, "#596B1D"), (62, "#4A5043")]: o.append(f'<circle cx="{cx}" cy="21" r="5" fill="{c}"/>')
    o.append(f'<text x="{W/2}" y="25" class="m" font-size="11" letter-spacing="3" fill="{t["chromeT"]}" text-anchor="middle">ACTIVITY.LOG</text>')
    o.append(f'<circle cx="{W-66}" cy="21" r="3" fill="#C6FF00"><animate attributeName="opacity" values="1;.3;1" dur="2.4s" repeatCount="indefinite"/></circle>'
             f'<text x="{W-24}" y="25" class="m" font-size="10" letter-spacing="2" fill="{t["chromeT"]}" text-anchor="end">LIVE</text>')
    n = len(metrics); cw = (W - 80) / n
    for i, (lab, val) in enumerate(metrics):
        cx = 40 + cw * i + cw / 2
        o.append(f'<text x="{cx:.1f}" y="100" class="m" font-size="40" font-weight="bold" fill="{t["text"]}" text-anchor="middle">{val:,}</text>')
        o.append(f'<text x="{cx:.1f}" y="126" class="m" font-size="10" letter-spacing="2" fill="{t["limeT"]}" text-anchor="middle">{E(lab)}</text>')
        if i: o.append(f'<line x1="{40+cw*i:.1f}" y1="70" x2="{40+cw*i:.1f}" y2="130" stroke="{t["border"]}"/>')
    if langs:
        o.append(f'<text x="40" y="172" class="m" font-size="10" letter-spacing="3" fill="{t["muted"]}">TOP LANGUAGES</text>')
        o.append(f'<rect x="40" y="182" width="{W-80}" height="8" rx="4" fill="{t["track"]}"/>')
        x = 40.0; tot = sum(p for _, p in langs)
        for i, (nm, p) in enumerate(langs):
            w = (W - 80) * p / tot
            o.append(f'<rect x="{x:.1f}" y="182" width="{max(w-2,1):.1f}" height="8" rx="2" fill="{t["shades"][i]}"/>'); x += w
        x = 40
        for i, (nm, p) in enumerate(langs):
            o.append(f'<circle cx="{x+4}" cy="214" r="4" fill="{t["shades"][i]}"/><text x="{x+14}" y="218" class="m" font-size="12" fill="{t["text"]}">{E(nm)} <tspan fill="{t["muted"]}">{p:.0f}%</tspan></text>')
            x += 14 + (len(nm) + 5) * 7.8 + 22
    o.append("</svg>")
    return "\n".join(o)

if __name__ == "__main__":
    metrics, langs = fetch()
    os.makedirs(OUT, exist_ok=True)
    for name, t in (("dark", DARK), ("light", LIGHT)):
        open(f"{OUT}/stats-{name}.svg", "w", encoding="utf-8").write(card(t, metrics, langs))
    print("wrote", OUT, metrics, langs)
