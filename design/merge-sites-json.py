#!/usr/bin/env python3
"""Three-way merge of sites.json at field level, for branch merges.

    python3 design/merge-sites-json.py BASE OURS THEIRS OUT

BASE/OURS/THEIRS are paths to the three versions (git show REF:sites.json).
Why this exists: sites.json is a registry, and a line-based merge cannot tell
which side holds the newer fact about a project, so it conflicts on the long
note strings both sides rewrote. This decides per field instead:

  - one side unchanged since BASE  -> take the side that changed
  - both changed                   -> OURS wins (the branch being merged INTO is
                                      the one that has been kept current)
  - changelog, both changed        -> keep OURS, then add THEIRS' new entries,
                                      unless the version label is already used on
                                      OURS (two different "v2"s would break the
                                      rule that a version is one deployed round);
                                      those are skipped and printed
  - a project only THEIRS has      -> added
Every decision that is not "took the only side that changed" is printed.
"""
import json
import sys


def load(p):
    return json.load(open(p, encoding="utf-8"))


def key(p):
    return p.get("slug") or p.get("codename")


def merge_value(k, b, o, t, where, log):
    if o == t:
        return o
    if o == b:
        return t
    if t == b:
        return o
    # both changed
    if k == "updated":
        return max(o, t)
    if k == "changelog" and isinstance(o, list) and isinstance(t, list):
        used = {c.get("version") for c in o}
        seen = {(c.get("date"), c.get("version")) for c in o}
        base_seen = {(c.get("date"), c.get("version")) for c in (b or [])}
        merged = list(o)
        for c in t:
            ident = (c.get("date"), c.get("version"))
            if ident in base_seen or ident in seen:
                continue
            if c.get("version") in used:
                log.append(f"  {where}: skipped their changelog {c.get('date')} {c.get('version')} "
                           f"(label already used on our side): {c.get('summary','')[:70]!r}")
                continue
            merged.append(c)
            log.append(f"  {where}: added their changelog {c.get('date')} {c.get('version')}")
        merged.sort(key=lambda c: c["date"] if str(c.get("date", "")).startswith("20") else "0000", reverse=True)
        return merged
    if isinstance(o, list) and isinstance(t, list) and all(isinstance(x, str) for x in o + t):
        extra = [x for x in t if x not in o and x not in (b or [])]
        if extra:
            log.append(f"  {where}.{k}: appended {len(extra)} of their notes")
        return o + extra
    log.append(f"  {where}.{k}: both changed, kept ours")
    return o


def merge_obj(b, o, t, where, log):
    out = {}
    for k in list(o) + [k for k in t if k not in o]:
        if k in o and k in t:
            out[k] = merge_value(k, b.get(k), o[k], t[k], where, log)
        elif k in o:
            if k in b and k not in t:
                log.append(f"  {where}.{k}: they removed it, kept ours")
            out[k] = o[k]
        else:
            if k in b:
                log.append(f"  {where}.{k}: we removed it, left it out")
                continue
            out[k] = t[k]
            log.append(f"  {where}.{k}: added from theirs")
    return out


def main():
    base, ours, theirs = (load(p) for p in sys.argv[1:4])
    log = []
    top = merge_obj({k: v for k, v in base.items() if k != "projects"},
                    {k: v for k, v in ours.items() if k != "projects"},
                    {k: v for k, v in theirs.items() if k != "projects"}, "top", log)
    bmap = {key(p): p for p in base["projects"]}
    omap = {key(p): p for p in ours["projects"]}
    tmap = {key(p): p for p in theirs["projects"]}
    projects = []
    for p in ours["projects"]:
        s = key(p)
        if s in tmap:
            projects.append(merge_obj(bmap.get(s, {}), p, tmap[s], s, log))
        else:
            projects.append(p)
    for s, p in tmap.items():
        if s not in omap:
            projects.append(p)
            log.append(f"  project added from theirs: {s}")
    out = {}
    for k in ours:
        out[k] = projects if k == "projects" else top.get(k, ours[k])
    for k in top:
        if k not in out:
            out[k] = top[k]
    json.dump(out, open(sys.argv[4], "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    open(sys.argv[4], "a").write("\n")
    print("\n".join(log) if log else "no non-trivial decisions")


if __name__ == "__main__":
    main()
