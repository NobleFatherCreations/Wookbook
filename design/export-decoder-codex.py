#!/usr/bin/env python3
"""Export everything the Pattern Decoder offers into one Markdown file an AI (or a person) can read whole.

Reads the deployed page itself (content/prose/_raw/playbook-v10.html), so the export is exactly what
readers see: every entry with every field, the groups, settings, guide questions, patterns, merged
names, glossary and the safety page. Run:  python3 design/export-decoder-codex.py
Writes docs/DECODER-CODEX.md.
"""
import json, os, re, html
from collections import defaultdict

ROOT = os.path.join(os.path.dirname(__file__), "..")
PAGE = os.path.join(ROOT, "content/prose/_raw/playbook-v10.html")
OUT = os.path.join(ROOT, "docs/DECODER-CODEX.md")

s = open(PAGE, encoding="utf-8").read()
D = json.loads(re.search(r'<script type="application/json" id="data">(.*?)</script>', s, re.S).group(1))
E = D["entries"]
BY = {e["n"]: e for e in E}
G = {g["k"]: g for g in D["groups"]}
SET = {x["k"]: x for x in D["settings"]}
ALPHA = sorted(E, key=lambda e: e["n"].lower())
FOLIO = {e["n"]: i + 1 for i, e in enumerate(ALPHA)}
PATS_OF = defaultdict(list)
for r in D["recipes"]:
    for n in r["c"]:
        PATS_OF[n].append(r["n"])
ALIASES_OF = defaultdict(list)
for a, n in D["aliases"].items():
    ALIASES_OF[n].append(a)
RESP = [("soft_clarification", "Ask about it gently"), ("firm_boundary", "Set a clear limit"), ("disengagement", "Step back"),
        ("support_seeking", "Get support"), ("workplace_or_professional", "At work, school or with services")]
SCRIPT = {"say": "Words you could use", "self": "Words to say to yourself", "verify": "A check to run before you share or act"}

def txt(x):
    return html.unescape(re.sub(r"<[^>]+>", "", str(x or ""))).strip()

def bullets(items, out):
    for it in items or []:
        out.append("- " + txt(it))

def slug(n):
    return re.sub(r"(^-+|-+$)", "", re.sub(r"[^a-z0-9]+", "-", n.lower())) or "x"

L = []
w = L.append
w("# The Pattern Decoder: complete codex")
w("")
w(f"Version **{D['version']}**. Live at https://noblefathercreations.com/playbook (also https://noblepatterns.netlify.app). "
  f"Generated from the deployed page by `design/export-decoder-codex.py`; do not hand-edit, regenerate.")
w("")
w("## What this site is")
w("")
w(f"A free, offline guide to **{len(E)} manipulation and control tactics**, explained in plain words: what each looks like, "
  "how to tell if it really fits, and what you can do. It is written for **someone who is hurting and unsure**: a person who "
  "suspects something is wrong in a relationship, family, friendship, workplace, school, online space or group, and wants "
  "words for it without being told what to think. It is a reading aid, not a diagnosis, legal opinion or therapy. Every "
  "entry says what the tactic is not and lists ordinary explanations, because one example is a signal to look closer, not a verdict.")
w("")
w("The guide runs entirely on the reader's device: no account, nothing typed is sent anywhere, optional private reading that "
  "stores nothing, and an anonymous visit counter (the Cloudflare Web Analytics beacon) as the only outside request. It is "
  "published by Noble Father Creations as one of the Instruments on noblefathercreations.com.")
w("")
w("### At a glance")
w("")
w(f"- {len(E)} entries in {len(D['groups'])} groups (\"constellations\") and {len(D['settings'])} settings (where it happens)")
w(f"- {sum(1 for e in E if e.get('sens'))} entries are marked **Safety-sensitive**: their safety note comes first and their wording advice is framed around safety")
w(f"- {len(D['recipes'])} patterns: named sequences in which several tactics tend to follow one another")
w(f"- {len(D['aliases'])} other names merged into the entry that covers them (old names and links still open the right entry)")
w(f"- A two-question guide (\"Help me figure it out\") built on {len(D['feelings'])} plain descriptions of what someone is experiencing, in {len(D['feelingGroups'])} parts of life")
w(f"- {len(D['common'])} entries flagged as the most common place to begin")
w(f"- {len(D['glossary'])} plain-word glossary terms explained inline where they first appear")
w("")
w("### How every entry is organised")
w("")
w("Each entry is read in five parts, from a 30-second summary to depth:")
w("")
w("1. **In short**: a plain-language summary, three things it can sound like, and two signs it may be something else. Safety-sensitive entries put the safety note here.")
w("2. **Understand it**: what it is, why it matters, how it shows up, more things people say.")
w("3. **Is this it?**: signs it might be this, signs it is probably something else, questions to ask yourself, what makes it more worrying, what shows up over time, what it is not, ordinary explanations, and what it is often mistaken for.")
w("4. **What you can do**: words you could use (or words to say to yourself, or a check to run first), five ways to respond, how to tell whether it is changing, and when to take it more seriously.")
w("5. **Go deeper**: how it works, how it can affect you, telling it apart from close relatives, using the label fairly, and the patterns it is part of.")
w("")
w("## Use this guide safely (as shown on the site)")
w("")
pages = {}
pj = os.environ.get("DECODER_PAGES_JSON")
if pj and os.path.exists(pj):
    pages = json.load(open(pj))
if pages.get("about"):
    about = pages["about"].split("What changed")[0]
    about = re.sub(r"^\s*Home\s*", "", about).strip()
    for para in [p.strip() for p in about.split("\n") if p.strip()]:
        if para.upper() == para and len(para) < 60:
            w("### " + para.title()); w("")
        elif para in ("Turn on private reading", "Private reading is on"):
            continue
        elif len(para) < 40 and not para.endswith("."):
            w("### " + para); w("")
        else:
            w(para); w("")
else:
    w("_(Safety page text was not captured in this export; see the site's \"Use this safely\" page.)_"); w("")

w("## The ten constellations")
w("")
for g in D["groups"]:
    n = sum(1 for e in E if e["g"] == g["k"])
    w(f"- **{g['label']}** ({n} tactics, colour {g['c']}): {g['blurb']}")
w("")
w("## Where it happens (settings)")
w("")
for x in D["settings"]:
    n = sum(1 for e in E if x["k"] in (e.get("w") or []))
    w(f"- **{x['label']}** ({n} tactics): {x.get('blurb','')}")
w("")
w("## The most common (where to begin)")
w("")
for n in D["common"]:
    if n in BY:
        w(f"- {n}: {txt(BY[n]['f']['short_definition'])}")
w("")
w("## Help me figure it out (the two-question guide)")
w("")
w("Step 1 asks where it has been happening; step 2 asks which descriptions sound like it (pick any number); the guide then "
  "lists up to 18 entries ranked by how many of the picked descriptions point to them.")
w("")
for fg in D["feelingGroups"]:
    w(f"### {fg['label']}")
    w("")
    for f in [f for f in D["feelings"] if f["group"] == fg["key"]]:
        top = [n for n in (D["narrow"].get(f["key"]) or []) if n in BY][:8]
        w(f"- **{f['label']}**" + (f" → {', '.join(top)}" if top else ""))
    w("")
w("## Glossary")
w("")
for k, v in D["glossary"].items():
    w(f"- **{k}**: {txt(v)}")
w("")
w("## How tactics combine (patterns)")
w("")
for r in D["recipes"]:
    w(f"### {r['n']}")
    w("")
    w(txt(r["d"]))
    w("")
    w("Steps: " + " → ".join(r["c"]))
    w("")
w("## Other names (merged into one entry)")
w("")
for a, n in sorted(D["aliases"].items()):
    w(f"- {a} → see **{n}**")
w("")
w("## Index of all entries")
w("")
for g in D["groups"]:
    names = sorted([e["n"] for e in E if e["g"] == g["k"]], key=str.lower)
    w(f"**{g['label']}** ({len(names)}): " + ", ".join(f"[{n}](#{slug(n)})" for n in names))
    w("")
w("## Entries")
w("")
for g in D["groups"]:
    w(f"## Constellation: {g['label']}")
    w("")
    w(g["blurb"])
    w("")
    for e in sorted([e for e in E if e["g"] == g["k"]], key=lambda e: e["n"].lower()):
        f = e["f"]
        w(f"### {e['n']}")
        w("")
        meta = [f"No. {FOLIO[e['n']]} of {len(E)}", f"group: {g['label']}"]
        if e.get("sub"): meta.insert(0, f"*{txt(e['sub'])}*")
        if e.get("sens"): meta.append("**Safety-sensitive**")
        w(" | ".join(meta))
        w("")
        if e.get("w"): w("Where it happens: " + ", ".join(SET[k]["label"] for k in e["w"] if k in SET)); w("")
        names = list(dict.fromkeys((e.get("abs") or []) + ALIASES_OF.get(e["n"], [])))
        if names: w("Also called: " + ", ".join(names)); w("")
        w(f"Link: https://noblefathercreations.com/playbook#/entry/{e['s']}")
        w("")
        w("#### In short")
        w(""); w(txt(f.get("plain_language_summary"))); w("")
        w("Short definition: " + txt(f.get("short_definition"))); w("")
        if e.get("sens"):
            w("**Your safety comes first.** " + txt(f.get("safety_note"))); w("")
        w("It can sound like:"); bullets(f.get("what_it_sounds_like"), L); w("")
        w("It may be something else if:"); bullets((f.get("this_may_not_be_it_when") or [])[:2], L); w("")
        w("#### Understand it")
        w(""); w(txt(f.get("expanded_definition"))); w(""); w("Why it matters: " + txt(f.get("why_this_matters"))); w("")
        w("How it shows up:"); bullets(f.get("what_it_is"), L); w("")
        w("#### Is this it?")
        w("")
        w("Signs it might be this:"); bullets(f.get("this_may_be_it_when"), L); w("")
        w("Signs it is probably something else:"); bullets((f.get("this_may_not_be_it_when") or [])[2:] + (f.get("less_concerning_if") or []), L); w("")
        w("Questions to ask yourself:"); bullets(f.get("discernment_questions"), L); w("")
        w("More worrying if:"); bullets(f.get("more_concerning_if"), L); w("")
        w("What shows up over time:"); bullets(f.get("pattern_over_time_signs"), L); w("")
        w("What it is not:"); bullets(f.get("what_it_is_not"), L); w("")
        w("Ordinary explanations:"); bullets(f.get("innocent_or_ordinary_possibilities"), L); w("")
        w("Often mistaken for this:"); bullets(f.get("common_false_positives"), L); w("")
        w("#### What you can do")
        w("")
        w(f"{SCRIPT.get(e.get('kind'), 'Words you could use')}: \"{txt(re.sub(r'^Verification script[^:]*:\s*', '', f.get('boundary_script') or '', flags=re.I))}\"")
        w("")
        w("Ways to respond:")
        for k, lab in RESP:
            v = (f.get("response_options") or {}).get(k)
            if v: w(f"- **{lab}:** {txt(v)}")
        w("")
        w("Is it changing? " + txt(f.get("boundary_respect_check")) + " " + txt(f.get("repair_check"))); w("")
        if not e.get("sens"): w("When to take it more seriously: " + txt(f.get("safety_note"))); w("")
        w("#### Go deeper")
        w("")
        w("How it works: " + txt(f.get("psychological_mechanism"))); w("")
        w("How it can affect you: " + txt(f.get("possible_impact_on_receiver"))); w("")
        w("Telling it apart from its neighbours: " + txt(f.get("how_to_distinguish_from_related"))); w("")
        rel = [n for n in (e.get("rel") or []) if n in BY]
        if rel: w("Close relatives: " + ", ".join(rel)); w("")
        w("Using this label fairly:"); bullets(f.get("misuse_warning"), L); w("")
        if PATS_OF.get(e["n"]): w("Patterns it is part of: " + ", ".join(PATS_OF[e["n"]])); w("")
w("## Version history (as shown on the site)")
w("")
w(f"Current: {D['version']}")
w("")
for u in D["updates"]:
    w("- " + txt(u))
w("")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w", encoding="utf-8").write("\n".join(L))
print("wrote", os.path.relpath(OUT, ROOT), len("\n".join(L)) // 1024, "KB", len(E), "entries")
