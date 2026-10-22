#!/usr/bin/env python3
"""Build the Pattern Decoder v10: one self-contained, offline HTML file.

Run from the repo root:  python3 design/build-decoder-v10.py [--out PATH]
Default output: content/prose/_raw/playbook-v10.html, the deployable page
(sites.json localSource). playbook.html stays as the v9-format data page that
extract-playbook-data.py reads; it is not deployed.

Inputs
  content/playbook-data.json            the 310 finished entries + sequences
  content/codex-final/tactic-merges.json merged-away names (aliases)
  content/codex-final/reader-meta.json  per-entry reader group, settings, plain
                                         subtitle and everyday search words; any
                                         entry it does not cover falls back to the
                                         category map below
  design/decoder-v10/                   app.css, app.js, assets/ (from extract-assets.py)
No CDN, no external request except the sanctioned analytics beacon.
"""
import argparse, json, os, re
from collections import Counter

ROOT = os.path.join(os.path.dirname(__file__), "..")
V10 = os.path.join(os.path.dirname(__file__), "decoder-v10")
A = os.path.join(V10, "assets")
VERSION = "v12 — 2026-10-22"
UPDATES = [
    "<strong>One screen, nothing to wade through (v12).</strong> On a computer the guide now fits a single screen: pick a group or a tactic and the screen splits, with where you are on the left and the entry on the right in tiles you can scan. A thin bar on the left follows the part you are reading.",
    "<strong>Easier to scan.</strong> The first sentence of every explanation is set in bold, so the answer comes first, and the lead words of each sign and question stand out. Reading text is now set in Inter, with more space between lines.",
    "<strong>Two skies.</strong> Midnight is ink black with smoked-glass panels; Daylight is gallery white. On the open sky the stars drift, lean toward your pointer and show their names as you pass; click a star to read it or a constellation to fly into it.",
    "<strong>Ten lights, four skies.</strong> Each constellation now has its own colour, and the sky and the page take it on as you move into it. Pick the sky you read under: Midnight, Aurora, Dusk, Eclipse or Daylight.",
    "<strong>Faster ways around.</strong> Press Ctrl K (or ⌘K) anywhere to jump to any tactic, group or page. A rail of ten marks at the edge of the screen shows where you are, and on an entry J and K step through its constellation.",
    "<strong>Motion that means something.</strong> Pages now hand off to each other: the name you tap becomes the title you read, headlines rise into place, a constellation draws its lines as you arrive, and the stars near your pointer brighten. Calm mode still stops all of it.",
    "<strong>A typeface of its own.</strong> The guide now has Astra, a typeface drawn for it: every letter is a constellation, and the dots of the i and the full stops are stars. Everything else was stripped back to space, type and thin lines.",
    "<strong>The sky.</strong> Every tactic is now a star in one night sky, grouped into ten constellations. The sky moves with you: wide on the home page, into a constellation when you open a group, onto the single star when you read an entry. Stars you have read glow gold, saved ones are ringed, and search results and your answers to the guide light up where they sit. A Calm button stops all motion.",
    "<strong>A simpler guide.</strong> Search by what happened, answer two short questions, or browse ten plain groups. Every entry now reads in five parts: in short, understand it, is this it, what you can do, and go deeper.",
    "<strong>Easier on a phone.</strong> Search sits at the top, a tab bar keeps every part of the guide one tap away, and each entry has a bar to jump between its parts.",
    "<strong>Every entry rewritten (v9).</strong> Each tactic has its own definition, examples, look-alikes, questions, words you could use and a safety note. Tactics that were the same thing under two names were merged; old names and links still work.",
]

GROUP_COLORS = {"truth": "#9FB2FF", "pressure": "#B9A6FF", "control": "#86CFEA", "hook": "#F0A6CF", "wear": "#D7A8F2",
                "blame": "#D6DC8F", "people": "#8FDCB8", "systems": "#AFC2DA", "online": "#7FE0DA", "society": "#A6D99B"}
GROUPS = [
    ("truth", "Twisting what is real", "Lies, denial and confusion that leave you unsure of your own memory or judgment."),
    ("pressure", "Guilt, pressure and fear", "Pushing you to say yes through guilt, obligation, urgency or threat."),
    ("control", "Control over your life", "Rules, monitoring and limits on your time, money, body or choices."),
    ("hook", "Love that hooks you", "Affection, attention and promises used to pull you in and keep you there."),
    ("wear", "Put-downs that wear you down", "Insults, contempt and slow erosion of how you see yourself."),
    ("blame", "Dodging blame", "Ways a person avoids responsibility, or turns it back on you."),
    ("people", "Turning people against you", "Isolating you, using other people, and controlling who hears what."),
    ("systems", "Work, school and systems", "When an organization, its rules or its paperwork become the weapon."),
    ("online", "Online and technology", "Fake accounts, deepfakes, tracking, scams and pressure through screens."),
    ("society", "Groups, cults and propaganda", "Influence over whole groups: high-control groups, propaganda and influence operations."),
]
CAT_TO_GROUP = {
    "Reality Distortion": "truth", "Deception": "truth", "Confusion / rhetoric": "truth",
    "Guilt & Obligation Leverage": "pressure", "Pressure & Coercion": "pressure",
    "Control & Domination": "control", "Control structural": "control",
    "Attachment & Affection Control": "hook", "Idealization structural": "hook", "Hooking structural": "hook",
    "Attack & Erosion": "wear", "Devaluation structural": "wear", "Identity & Conditioning": "wear",
    "Accountability Evasion": "blame",
    "Isolation / social": "people", "Social Warfare & Triangulation": "people",
    "Institutional & Process": "systems", "Organizational & Institutional": "systems",
    "Digital & AI": "online", "Digital": "online", "Discard / institutional": "control",
    "Cult & Thought Reform": "society", "Political & Propaganda": "society",
    "Espionage & Influence Operations": "society",
}
SETTINGS = [
    ("relationship", "Dating and partners", "Tactics that show up between partners, exes and people dating."),
    ("family", "Family", "Parents, children, siblings and the wider family."),
    ("friends", "Friends and social circles", "Friendships, groups of friends and communities."),
    ("work", "Work and school", "Jobs, teams, classrooms, institutions and services."),
    ("online", "Online", "Social media, messaging, apps and strangers on the internet."),
    ("groups", "Groups and belief communities", "Religious, wellness, political and other close-knit groups."),
    ("society", "Media and society", "News, politics, advertising and influence at scale."),
]
FEEL_TO_SETTING = {"relationship": "relationship", "family": "family", "work": "work", "social": "friends", "online": "online"}
# Terms readers meet in the "what you can do" and safety text, explained once, on tap.
GLOSSARY = {
    "advocate": "A trained person, often free, who helps you understand your options and make a safety plan. Domestic violence and sexual assault services, unions and patient services have them.",
    "legal aid": "Free or low-cost legal help for people who cannot pay a lawyer. Many areas have a legal aid office or a law school clinic.",
    "crisis line": "A phone, text or chat service you can contact any time to talk to a trained person, often free and confidential.",
    "protective order": "A court order that tells someone to stay away from you or stop contacting you. The name varies by place, for example restraining order.",
    "coercive control": "A pattern of behavior that takes away a person's freedom bit by bit: watching, isolating, controlling money or rules, and making them afraid.",
    "ombudsperson": "An independent officer inside an organization who looks into complaints and is not on either side.",
}
TRIES = ["You're overreacting", "the silent treatment", "they keep changing the rules", "love bombing"]
FIELDS = ["short_definition", "plain_language_summary", "expanded_definition", "why_this_matters", "what_it_is",
          "what_it_sounds_like", "what_it_is_not", "this_may_be_it_when", "this_may_not_be_it_when",
          "innocent_or_ordinary_possibilities", "common_false_positives", "discernment_questions",
          "less_concerning_if", "more_concerning_if", "pattern_over_time_signs", "repair_check",
          "boundary_respect_check", "psychological_mechanism", "possible_impact_on_receiver", "response_options",
          "boundary_script", "safety_note", "misuse_warning", "how_to_distinguish_from_related"]


def read(*p):
    return open(os.path.join(*p), encoding="utf-8").read()


def js_object_literal(src, name):
    """FEELING_GROUPS / FEELINGS are JS literals with bare keys; make them JSON."""
    m = re.search(r"const " + name + r"\s*=\s*\[", src)
    i = m.end() - 1; depth = 0
    for j in range(i, len(src)):
        depth += src[j] == "["; depth -= src[j] == "]"
        if depth == 0:
            break
    body = src[i:j + 1]
    body = re.sub(r"/\*.*?\*/", "", body, flags=re.S)
    body = re.sub(r"([{,]\s*)([A-Za-z_]\w*)\s*:", r'\1"\2":', body)
    body = re.sub(r",(\s*[\]}])", r"\1", body)
    return json.loads(body)


def toks(t):
    return {w for w in re.findall(r"[a-z']+", t.lower()) if len(w) > 3}


def near(a, b):
    """Word-set overlap; 0.5+ means the two items say the same thing."""
    x, y = toks(a), toks(b)
    return len(x & y) / max(1, min(len(x), len(y)))


def dedupe(items, against):
    keep = [i for i in items if all(near(i, o) < 0.5 for o in against)]
    return keep or items[:1]


def layout_sky(entries, recipes, portrait=False):
    """Deterministic star positions: each group is a constellation on a ring; inside a group
    stars start on a phyllotaxis spiral (popular ones nearest the centre) and are relaxed
    with springs along related links and repulsion, so neighbours sit near each other.
    Pure Python and seeded, so the same data always draws the same sky."""
    import math, random
    W, H = (1700, 2700) if portrait else (2600, 1700)
    order = ["hook", "wear", "truth", "blame", "pressure", "control", "people", "systems", "online", "society"]
    cx0, cy0 = W / 2, H / 2
    centres = {}
    for i, g in enumerate(order):
        a = -math.pi / 2 + i * 2 * math.pi / len(order) + 0.18
        rr = 0.36 + 0.05 * math.sin(i * 2.3)
        centres[g] = (cx0 + math.cos(a) * W * rr * (1.05 if portrait else 1), cy0 + math.sin(a) * H * rr * (1.0 if portrait else 1.02))
    idx = {e["n"]: i for i, e in enumerate(entries)}
    pos = [None] * len(entries)
    rng = random.Random(310)
    for g in order:
        members = sorted([e for e in entries if e["g"] == g], key=lambda e: (-e["pop"], e["n"]))
        gx, gy = centres[g]
        for k, e in enumerate(members):
            r = 38 * math.sqrt(k + 1.5); a = k * 2.399963 + rng.random() * .4
            pos[idx[e["n"]]] = [gx + r * math.cos(a), gy + r * math.sin(a) * .82]
    edges = set()
    for e in entries:
        i = idx[e["n"]]; same = [idx[r] for r in e["rel"] if r in idx and entries[idx[r]]["g"] == e["g"]]
        for j in same[:3]:
            edges.add((min(i, j), max(i, j)))
    for it in range(220):
        force = [[0.0, 0.0] for _ in pos]
        for i in range(len(pos)):
            for j in range(i + 1, len(pos)):
                dx = pos[i][0] - pos[j][0]; dy = pos[i][1] - pos[j][1]
                d2 = dx * dx + dy * dy + .01
                if d2 < 110 * 110:
                    d = math.sqrt(d2); f = (110 - d) / 110 * 2.2
                    force[i][0] += dx / d * f; force[i][1] += dy / d * f
                    force[j][0] -= dx / d * f; force[j][1] -= dy / d * f
        for i, j in edges:
            dx = pos[j][0] - pos[i][0]; dy = pos[j][1] - pos[i][1]
            d = math.sqrt(dx * dx + dy * dy) + .01
            f = (d - 96) * .012
            force[i][0] += dx / d * f; force[i][1] += dy / d * f
            force[j][0] -= dx / d * f; force[j][1] -= dy / d * f
        for i, e in enumerate(entries):
            gx, gy = centres[e["g"]]
            force[i][0] += (gx - pos[i][0]) * .004; force[i][1] += (gy - pos[i][1]) * .004
        for i in range(len(pos)):
            pos[i][0] += max(-6, min(6, force[i][0])); pos[i][1] += max(-6, min(6, force[i][1]))
    xs = [p[0] for p in pos]; ys = [p[1] for p in pos]
    mx, my = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    scale_x = (W * .9) / (max(xs) - min(xs)); scale_y = (H * .9) / (max(ys) - min(ys)); sc = min(scale_x, scale_y, 1.25)
    for p in pos:
        p[0] = round(W / 2 + (p[0] - mx) * sc, 1); p[1] = round(H / 2 + (p[1] - my) * sc, 1)
    gcent = {}
    for g in order:
        pts = [pos[idx[e["n"]]] for e in entries if e["g"] == g]
        gx = sum(p[0] for p in pts) / len(pts); gy = sum(p[1] for p in pts) / len(pts)
        rad = max(math.hypot(p[0] - gx, p[1] - gy) for p in pts)
        gcent[g] = {"x": round(gx, 1), "y": round(gy, 1), "r": round(rad, 1)}
    # cross-group related links are kept separately: drawn only for a focused star
    near = [[idx[r] for r in e["rel"] if r in idx] for e in entries]
    return {"w": W, "h": H, "pos": pos, "edges": sorted([list(x) for x in edges]), "groups": gcent, "near": near,
            "seq": [[idx[n] for n in r["c"] if n in idx] for r in recipes]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "content", "prose", "_raw", "playbook-v10.html"))
    a = ap.parse_args()
    data = json.load(open(os.path.join(ROOT, "content", "playbook-data.json"), encoding="utf-8"))
    codex, recipes = data["codex_completed"], data["recipes"]
    merges = json.load(open(os.path.join(ROOT, "content", "codex-final", "tactic-merges.json")))["groups"]
    aliases = {m: g["canonical"] for g in merges for m in g["merged"]}
    meta_p = os.path.join(ROOT, "content", "codex-final", "reader-meta.json")
    meta = json.load(open(meta_p, encoding="utf-8"))["entries"] if os.path.exists(meta_p) else {}
    feel_src = read(A, "feelings.js")
    feeling_groups = js_object_literal(feel_src, "FEELING_GROUPS")
    feelings = js_object_literal(feel_src, "FEELINGS")
    narrow = json.loads(read(A, "narrow-by-feeling.json"))
    narrow = {k: [aliases.get(n, n) for n in v] for k, v in narrow.items()}
    stop = re.search(r'new Set\(\("([^"]+)"', read(A, "search-stop.js")).group(1).split()

    meta_doc = json.load(open(meta_p, encoding="utf-8")) if os.path.exists(meta_p) else {}
    feelings += meta_doc.get("new_feelings", [])
    if meta_doc.get("feelings_index"):
        narrow = {k: [aliases.get(n, n) for n in v] for k, v in meta_doc["feelings_index"].items()}
    names = {c["name"] for c in codex}
    pop = Counter(n for r in recipes for n in r["c"])
    feel_group = {f["key"]: f["group"] for f in feelings}
    settings_of = {}
    for k, lst in narrow.items():
        s = FEEL_TO_SETTING.get(feel_group.get(k))
        for n in lst:
            if s:
                settings_of.setdefault(n, set()).add(s)

    def slug(s):
        return re.sub(r"(^-+|-+$)", "", re.sub(r"[^a-z0-9]+", "-", s.lower())) or "x"

    entries, seen = [], {}
    for c in codex:
        n = c["name"]; m = meta.get(n, {})
        g = m.get("group") or CAT_TO_GROUP[c["category"]]
        w = m.get("settings")
        if not w:
            w = sorted(settings_of.get(n, set()))
            if g == "systems": w = sorted(set(w) | {"work"})
            if g == "online": w = sorted(set(w) | {"online"})
            if g == "society": w = sorted(set(w) | {"society"})
        s = slug(n); k = 1
        while s in seen:
            k += 1; s = slug(n) + "-" + str(k)
        seen[s] = n
        entries.append({
            "n": n, "s": s, "g": g, "w": w, "cat": c["category"],
            "sub": m.get("subtitle", ""), "kw": m.get("search_words", []),
            "sens": bool(c["safety_sensitive"]), "abs": c.get("absorbs") or [],
            "rel": [r for r in (m.get("related") or c.get("related_tactics", [])) if r in names and r != n],
            "pop": pop.get(n, 0),
            "kind": ("verify" if (c["branch"] == "societal" or c["boundary_script"].lower().startswith("verification"))
                     else "self" if c["branch"] == "aftermath" else "say"),
            "f": {**{f: c[f] for f in FIELDS},
                  "less_concerning_if": dedupe(c["less_concerning_if"], c["this_may_not_be_it_when"])},
        })
    by = {e["n"]: e for e in entries}
    _rec = [{"c": [aliases.get(x, x) for x in r["c"]]} for r in recipes]
    payload_sky = {"land": layout_sky(entries, _rec), "port": layout_sky(entries, _rec, True)}
    # The most common: the v9 formula (text-detectable tier, then how often it recurs
    # inside the documented sequences), kept to 24 so the list stays a starting point.
    core = sorted(codex, key=lambda c: (-((4 if c["tier"] == "Detected" else 0) + min(pop.get(c["name"], 0), 10)), c["name"]))
    common = [c["name"] for c in core[:24]]
    SHORT = {"truth": "Twisting truth", "pressure": "Guilt and pressure", "control": "Control", "hook": "Love that hooks", "wear": "Put-downs", "blame": "Dodging blame", "people": "Turning people", "systems": "Work and systems", "online": "Online", "society": "Groups and cults"}
    groups = [{"k": k, "label": l, "blurb": b, "short": SHORT[k], "c": GROUP_COLORS[k]} for k, l, b in GROUPS if any(e["g"] == k for e in entries)]
    payload = {
        "entries": entries, "groups": groups,
        "settings": [{"k": k, "label": l, "blurb": b} for k, l, b in SETTINGS],
        "recipes": [{"n": r["n"], "c": [aliases.get(x, x) for x in r["c"] if aliases.get(x, x) in by], "d": r["d"]} for r in recipes],
        "aliases": aliases, "narrow": narrow, "feelings": feelings, "feelingGroups": feeling_groups,
        "sky": payload_sky, "stop": stop, "common": common, "glossary": GLOSSARY, "tries": TRIES, "catToGroup": CAT_TO_GROUP,
        "cover": read(A, "cover.txt"), "wordmark": read(A, "wordmark.svg"),
        "version": VERSION, "updates": UPDATES,
    }
    blob = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    logo = read(A, "brand-logo.txt")
    shell = read(V10, "shell.html")
    import base64
    faces = re.findall(r"@font-face\s*\{[^}]*\}", read(A, "fonts.css"))
    # Inter (SIL OFL 1.1, rsms.me/inter), variable 100-900, subset to Latin by fontTools
    sans = "@font-face{font-family:'Inter';font-style:normal;font-weight:100 900;font-display:swap;src:url(data:font/woff2;base64,%s) format('woff2')}" % base64.b64encode(open(os.path.join(A, "inter-var.woff2"), "rb").read()).decode()
    astra = "\n".join("@font-face{font-family:'Astra';font-style:normal;font-weight:%d;font-display:swap;src:url(data:font/woff2;base64,%s) format('woff2')}"
                      % (wt, base64.b64encode(open(os.path.join(A, "astra-%s.woff2" % nm), "rb").read()).decode())
                      for nm, wt in (("light", 300), ("medium", 500)))
    html = (shell.replace("{{FONTS}}", sans + "\n" + astra)
                 .replace("{{CSS}}", read(V10, "app.css"))
                 .replace("{{LOGO}}", logo)
                 .replace("{{COUNT}}", str(len(entries)))
                 .replace("{{DATA}}", blob)
                 .replace("{{HOUSE}}", read(A, "house.html"))
                 .replace("{{BEACON}}", read(A, "beacon.html"))
                 .replace("{{JS}}", read(V10, "app.js").replace("//@@SKY@@", read(V10, "sky.js"))))
    assert "{{" not in html, "unfilled placeholder in shell"
    with open(a.out, "w", encoding="utf-8") as fh:
        fh.write(html)
    gs = Counter(e["g"] for e in entries)
    print(f"wrote {os.path.relpath(a.out, ROOT)}  {len(html.encode())//1024} KB  entries {len(entries)}  "
          f"meta {sum(1 for e in entries if e['n'] in meta)}/{len(entries)}")
    print("  groups:", ", ".join(f"{k} {gs[k]}" for k, _, _ in GROUPS))
    print("  no settings:", sum(1 for e in entries if not e["w"]))


if __name__ == "__main__":
    main()
