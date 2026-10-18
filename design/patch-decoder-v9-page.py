#!/usr/bin/env python3
"""One-off page edits for Decoder v9 (kept for provenance, not a build step).

Run from the repo root:  python3 design/patch-decoder-v9-page.py [--apply]

Two changes to content/prose/_raw/playbook.html, each asserted to match exactly
the expected number of times so a changed page fails loudly instead of being
half-patched:

1. Safety badge. The page used to decide "safety-sensitive" by searching
   safety_note for the phrase "No elevated safety concern". Entries now carry
   tactic-specific safety notes and an explicit safety_sensitive boolean, so
   all five checks go through one helper, safetyFlag(), which reads the
   boolean and falls back to the old phrase test for any entry without it.

2. One safeguards page (#/about). The sentences that used to be copied onto
   every entry ("a signal to examine, not proof...", the emergency-help
   guidance, what the paste box can and cannot know) now live once, here,
   linked from the footer and from every entry.
"""
import argparse
import os
import sys

HTML = os.path.join(os.path.dirname(__file__), "..", "content", "prose", "_raw", "playbook.html")

OLD_TEST = 'c.safety_note&&c.safety_note.indexOf("No elevated safety concern")===-1'

ABOUT = r"""
function viewAbout(){
  const p=t=>'<p style="max-width:620px;margin:0 0 12px">'+t+'</p>';
  const h=t=>'<h2 style="margin:26px 0 8px">'+t+'</h2>';
  return '<div class="label">Before you use this guide</div><h1 class="view-h">How to use it safely</h1>'+
    '<p class="small" style="max-width:580px">This page says once what would otherwise be repeated on every entry. Each entry is written about its own tactic; the safeguards that apply to all of them are here.</p>'+
    h('What this guide is')+
    p('A reading aid. It helps you put a name to something that happened, see what else it can be mistaken for, and decide what to do next. Some entries are about everyday relationships; others are about institutions, online life and influence at the scale of a society.')+
    h('What it is not')+
    p('It is not a diagnosis, a legal opinion, or therapy. It cannot tell you what another person meant, what they are like, or whether you are in danger. Only you, and the people you trust, can weigh that.')+
    h('A signal, not a verdict')+
    p('One example of a pattern is a reason to look more closely, not proof of motive, abuse or character. Every entry says what its tactic is not, because most of these behaviors also have ordinary explanations. Please do not use a label from this guide to attack, shame, threaten, expose or get back at someone.')+
    h('The search box')+
    p('Pasting in something that was said to you finds entries whose wording is close to it. That is a pointer to read further, never a finding. It cannot see the tone, the history, or whether the words were meant seriously, and a single sentence says very little.')+
    h('If you are not safe')+
    p('If any of this involves threats, being watched or tracked, being cut off from people, money, housing, immigration status, sex, pressure toward self-harm, retaliation, or fear for your safety, please reach a real person: someone you trust, a local support service, a legal or workplace resource, or emergency services if you are in immediate danger. Entries marked <em>Safety-sensitive</em> say more about what to watch for.')+
    h('Your privacy')+
    p('There is no account. Your saved trail and starred entries stay on this device. The page counts anonymous visits, and nothing you type, paste or save is sent anywhere.')+
    '<div class="entry-actions" style="margin-top:22px"><button class="btn primary" onclick="nav(\'\')">Back to start</button><button class="btn" onclick="nav(\'all\')">All 349 entries</button></div>';
}
"""


def patch(html):
    n = html.count(OLD_TEST)
    assert n == 5, f"expected 5 safety tests, found {n}"
    html = html.replace(
        'const safety=c&&' + OLD_TEST + ';',
        'const safety=safetyFlag(c);')
    html = html.replace(
        'const isSafetySensitive=!!(' + OLD_TEST + ');',
        'const isSafetySensitive=safetyFlag(c);')
    html = html.replace(
        '(' + OLD_TEST + '?\'<span class="badge badge-safety">',
        '(safetyFlag(c)?\'<span class="badge badge-safety">')
    old_fn = ('function isSafetySensitive(name){\n  const c=CODEX_BY_NAME[name];\n'
              '  return !!(c&&c.safety_note&&c.safety_note.indexOf("No elevated safety concern")===-1);\n}')
    assert html.count(old_fn) == 1, "isSafetySensitive() changed"
    html = html.replace(old_fn,
        '/* One definition of "safety-sensitive": the explicit boolean the entry carries,\n'
        '   falling back to the old phrase test only for an entry that lacks it. */\n'
        'function safetyFlag(c){\n'
        '  if(!c) return false;\n'
        '  if(typeof c.safety_sensitive==="boolean") return c.safety_sensitive;\n'
        '  return !!(c.safety_note&&c.safety_note.indexOf("No elevated safety concern")===-1);\n}\n'
        'function isSafetySensitive(name){ return safetyFlag(CODEX_BY_NAME[name]); }')
    assert html.count(OLD_TEST) == 1, "only the helper's fallback should still use the phrase test"

    anchor = "function viewCore(){"
    assert html.count(anchor) == 1
    html = html.replace(anchor, ABOUT.strip("\n") + "\n" + anchor)

    route = 'else if(r.view==="core") body=viewCore();'
    assert html.count(route) == 1
    html = html.replace(route, route + '\n    else if(r.view==="about") body=viewAbout();')

    link = ("'<a href=\"'+BRAND_TIKTOK_URL+'\" target=\"_blank\" rel=\"noopener noreferrer\">")
    assert html.count(link) == 1, "footer TikTok link changed"
    html = html.replace(link,
        "'<a href=\"#/about\" onclick=\"event.preventDefault();nav(\\'about\\')\">'+ic(\"shield\",14)+' How to use this safely</a>'+\n          " + link)

    hint = "'<div class=\"prevnext-hint small\">Tip:"
    assert html.count(hint) == 1, "entry tip line changed"
    html = html.replace(hint,
        "'<p class=\"small\" style=\"margin:14px 0 0\">New here? <a href=\"#/about\" onclick=\"event.preventDefault();nav(\\'about\\')\">How to use these entries safely</a>.</p>'+\n    " + hint)
    return html


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    html = open(HTML, encoding="utf-8").read()
    if "function viewAbout(" in html:
        sys.exit("already patched")
    out = patch(html)
    print("page size:", len(html), "->", len(out))
    if a.apply:
        open(HTML, "w", encoding="utf-8").write(out)
        print("wrote", HTML)
    else:
        print("dry run -- pass --apply to write")


if __name__ == "__main__":
    main()
