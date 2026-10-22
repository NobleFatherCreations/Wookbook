#!/usr/bin/env python3
"""Build the Pattern Decoder v10: one self-contained, offline HTML file.

Run from the repo root:  python3 design/build-decoder-v10.py [--out PATH]
Default output: content/prose/_raw/playbook-v10.html (a draft until v10 ships,
when it replaces playbook.html).

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
VERSION = "v10 — 2026-10-22"
UPDATES = [
    "<strong>A simpler guide.</strong> Search by what happened, answer two short questions, or browse ten plain groups. Every entry now reads in five parts: in short, understand it, is this it, what you can do, and go deeper.",
    "<strong>Easier on a phone.</strong> Search sits at the top, a tab bar keeps every part of the guide one tap away, and each entry has a bar to jump between its parts.",
    "<strong>Every entry rewritten (v9).</strong> Each tactic has its own definition, examples, look-alikes, questions, words you could use and a safety note. Tactics that were the same thing under two names were merged; old names and links still work.",
]

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
    # The most common: the v9 formula (text-detectable tier, then how often it recurs
    # inside the documented sequences), kept to 24 so the list stays a starting point.
    core = sorted(codex, key=lambda c: (-((4 if c["tier"] == "Detected" else 0) + min(pop.get(c["name"], 0), 10)), c["name"]))
    common = [c["name"] for c in core[:24]]
    groups = [{"k": k, "label": l, "blurb": b} for k, l, b in GROUPS if any(e["g"] == k for e in entries)]
    payload = {
        "entries": entries, "groups": groups,
        "settings": [{"k": k, "label": l, "blurb": b} for k, l, b in SETTINGS],
        "recipes": [{"n": r["n"], "c": [aliases.get(x, x) for x in r["c"] if aliases.get(x, x) in by], "d": r["d"]} for r in recipes],
        "aliases": aliases, "narrow": narrow, "feelings": feelings, "feelingGroups": feeling_groups,
        "stop": stop, "common": common, "glossary": GLOSSARY, "tries": TRIES, "catToGroup": CAT_TO_GROUP,
        "cover": read(A, "cover.txt"), "wordmark": read(A, "wordmark.svg"),
        "version": VERSION, "updates": UPDATES,
    }
    blob = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    logo = read(A, "brand-logo.txt")
    shell = read(V10, "shell.html")
    html = (shell.replace("{{FONTS}}", read(A, "fonts.css"))
                 .replace("{{CSS}}", read(V10, "app.css"))
                 .replace("{{LOGO}}", logo)
                 .replace("{{COUNT}}", str(len(entries)))
                 .replace("{{DATA}}", blob)
                 .replace("{{HOUSE}}", read(A, "house.html"))
                 .replace("{{BEACON}}", read(A, "beacon.html"))
                 .replace("{{JS}}", read(V10, "app.js")))
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
