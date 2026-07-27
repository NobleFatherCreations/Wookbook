#!/usr/bin/env python3
"""The Codex — compositional rebuild of The Divide.

The artifact here is a tactic entry, and every entry carries three registers
that were set identically: how the tactic appears, the defense you will hear,
and the counter. They are three different voices — observation, the abuser's
mouth, and the reader's weapon — and flattening them into one grey column
threw away the whole point. Here each is set as itself.

Presentation generators only: `secHead`, `relEntryHTML`, `box`, `gradeBadge`.
The data, the routing, the search and filter behaviour, the grading logic and
the case linking are untouched.
"""
import re

MARK = "cx-codex"

SEC_JS = r'''function secHead(id,kicker,title){
  const p = D.purpose[id];
  return `<header class="sec cx-sec" id="${id}">
    <span class="cx-sec-rule" aria-hidden="true"></span>
    <div class="sec-k cx-sec-k">${esc(kicker)}</div>
    <h2 class="sec-t cx-sec-t">${esc(title)}</h2>
    ${p?`<p class="sec-p cx-sec-p">${fmt(p)}</p>`:''}</header>`;
}'''

REL_JS = r'''function relEntryHTML(t, i, open){
  const r = D.religions[i-1], e = t.entries[String(i)];
  if(!e) return '';
  const g = gradeOf(r.id, t.order), cs = casesFor(r.id, t.order);
  return `<details class="rel cx-plate" id="rel-${i}" ${open?'open':''} data-rel="${i}">
    <summary class="cx-plate-head"><span class="rn cx-plate-n">${String(i).padStart(2,'0')}</span><span class="rt cx-plate-t">${esc(r.name)}</span>${g?gradeBadge(g):''}<span class="cx-plate-chev" aria-hidden="true"></span></summary>
    <div class="body cx-plate-body">
      <section class="cx-reg cx-reg-see">
        <div class="lbl cx-reg-l">How it appears</div>
        <ul class="tight cx-see">${e.examples.map(x=>`<li>${fmt(x)}</li>`).join('')}</ul>
      </section>
      <section class="cx-reg cx-reg-def">
        <div class="lbl def cx-reg-l">The defense you will hear</div>
        ${e.defenses.map(x=>`<blockquote class="def cx-def">${fmt(x)}</blockquote>`).join('')}
      </section>
      <section class="cx-reg cx-reg-ctr">
        <div class="lbl ctr cx-reg-l">The counter</div>
        ${e.counters.map(x=>`<div class="ctrtext cx-ctr">${fmt(x)}</div>`).join('')}
      </section>
      ${gradeLine(g)}
      ${cs.length?`<div class="tac-cases cx-cases"><span class="st8-k">Documented case${cs.length===1?'':'s'}</span>${cs.map(c=>`<a href="#/cases?c=${c.id}">${esc(c.title)} &middot; ${esc(c.when)}</a>`).join('')}</div>`:''}
      <div class="tac-more cx-more"><a href="#/religion/${r.id}?at=stage-${stageKeyFor(t.order)}">Read this inside ${esc(r.name)}'s cycle &rarr;</a></div>
    </div></details>`;
}'''

BOX_JS = r'''function box(kind,label,body){
  const arr = Array.isArray(body)?body:[body];
  return `<aside class="box cx-box ${kind}"><span class="box-l cx-box-l">${esc(label)}</span>${arr.map(x=>`<p>${fmt(x)}</p>`).join('')}</aside>`;
}'''

CSS = r"""
/* ======================= THE CODEX — The Divide ======================= */
/* one sage that reads on parchment and on ink alike */
:root{--cx-ease:cubic-bezier(.2,.7,.2,1);--sage-ac:#3F7F5E}
@media (prefers-color-scheme: dark){:root{--sage-ac:#7FBF9A}}
html[data-theme="dark"],body.dark,body.night{--sage-ac:#7FBF9A}

/* ---- chapter openings ---- */
.cx-sec{position:relative;padding-top:34px}
.cx-sec-rule{position:absolute;top:0;left:0;width:74px;height:1px;
  background:linear-gradient(90deg,var(--gilt,#C29A52),transparent)}
.cx-sec-k{letter-spacing:.3em;font-size:10px;text-transform:uppercase}
.cx-sec-t{letter-spacing:-.022em;text-wrap:balance;line-height:1.06}
.cx-sec-p{max-width:62ch}

/* ---- a tactic entry, set as a codex plate ---- */
.cx-plate{position:relative;border-radius:3px;overflow:hidden;
  border:1px solid color-mix(in srgb,var(--gilt) 22%,transparent);
  background:color-mix(in srgb,var(--gilt) 4%,transparent);
  transition:border-color .3s var(--cx-ease),box-shadow .3s var(--cx-ease)}
.cx-plate+.cx-plate{margin-top:10px}
.cx-plate:hover{border-color:color-mix(in srgb,var(--gilt) 45%,transparent)}
.cx-plate[open]{border-color:color-mix(in srgb,var(--gilt) 58%,transparent);
  box-shadow:0 18px 46px -24px rgba(0,0,0,.85)}
.cx-plate-head{display:flex;align-items:center;gap:13px;cursor:pointer;
  padding:15px 17px;list-style:none;position:relative}
.cx-plate-head::-webkit-details-marker{display:none}
.cx-plate-n{font-family:var(--mono,ui-monospace,monospace);font-size:10.5px;
  letter-spacing:.14em;color:var(--gilt);opacity:.9;flex:none;
  padding:4px 7px;border:1px solid color-mix(in srgb,var(--gilt) 34%,transparent);border-radius:2px}
.cx-plate-t{font-family:var(--display,Georgia,serif);font-size:1.06rem;font-weight:600;
  letter-spacing:.004em;flex:1;min-width:0;
  transition:color .26s var(--cx-ease)}
.cx-plate:hover .cx-plate-t,.cx-plate[open] .cx-plate-t{color:var(--gilt)}
.cx-plate-chev{width:9px;height:9px;flex:none;border-right:1px solid var(--gilt);border-bottom:1px solid var(--gilt);opacity:.75;transform:rotate(45deg);
  transition:transform .34s var(--cx-ease);margin-left:2px}
.cx-plate[open] .cx-plate-chev{transform:rotate(-135deg)}
.cx-plate-body{padding:4px 17px 20px}
@media (prefers-reduced-motion: no-preference){
  .cx-plate[open] .cx-plate-body{animation:cx-unfurl .42s var(--cx-ease) both}
  @keyframes cx-unfurl{from{opacity:0;transform:translateY(-7px)}to{opacity:1;transform:none}}
}

/* ---- the three registers, each in its own voice ---- */
.cx-reg{position:relative;padding:16px 0 16px 20px}
.cx-reg+.cx-reg{border-top:1px solid color-mix(in srgb,var(--gilt) 16%,transparent)}
.cx-reg::before{content:"";position:absolute;left:0;top:20px;bottom:16px;width:1px}
.cx-reg-l{font-family:var(--mono,ui-monospace,monospace);font-size:9.5px;
  letter-spacing:.24em;text-transform:uppercase;margin-bottom:11px;display:block}

/* observation — plain, evidentiary */
.cx-reg-see::before{background:linear-gradient(180deg,var(--gilt),transparent)}
.cx-reg-see .cx-reg-l{color:var(--gilt)}
.cx-see{list-style:none;margin:0;padding:0}
.cx-see li{position:relative;padding-left:19px;margin-bottom:9px;line-height:1.72}
.cx-see li::before{content:"";position:absolute;left:2px;top:.62em;width:7px;height:1px;
  background:var(--gilt);opacity:.7}

/* the defense — someone else's mouth, so it is quoted and set cooler */
.cx-reg-def::before{background:linear-gradient(180deg,currentColor,transparent);opacity:.34}
.cx-reg-def .cx-reg-l{color:var(--ink);opacity:.62}
.cx-def{margin:0 0 10px;padding:0 0 0 16px;border:0;border-left:1px solid currentColor;
  font-family:var(--display,Georgia,serif);font-style:italic;line-height:1.66;
  color:var(--ink);opacity:.78;background:none;quotes:"\201C" "\201D"}
.cx-def::before{content:open-quote;opacity:.6;margin-right:.1em}
.cx-def::after{content:close-quote;opacity:.6}

/* the counter — the reader's weapon, so it carries the most light */
.cx-reg-ctr::before{background:linear-gradient(180deg,var(--sage-ac),transparent)}
.cx-reg-ctr .cx-reg-l{color:var(--sage-ac)}
.cx-ctr{position:relative;padding:12px 15px 12px 15px;margin-bottom:9px;border-radius:3px;
  background:color-mix(in srgb,var(--sage-ac) 13%,transparent);
  box-shadow:inset 0 0 0 1px color-mix(in srgb,var(--sage-ac) 34%,transparent);
  color:var(--ink);line-height:1.7;font-weight:600}

/* ---- the evidence grade, struck as a stamp ---- */
.gbadge{font-family:var(--mono,ui-monospace,monospace)!important;font-size:9px!important;
  letter-spacing:.16em;text-transform:uppercase;padding:5px 9px!important;
  border-radius:2px!important;flex:none}
.tier{font-family:var(--mono,ui-monospace,monospace);font-size:8.5px;letter-spacing:.16em;
  text-transform:uppercase;padding:4px 8px;border-radius:2px;flex:none;
  border:1px solid color-mix(in srgb,var(--gilt) 34%,transparent);color:var(--gilt);opacity:.9}
.tier-s{border-color:color-mix(in srgb,var(--sage-ac) 50%,transparent);color:var(--sage-ac)}

/* ---- apparatus ---- */
.cx-cases{margin-top:16px;padding-top:14px;border-top:1px solid color-mix(in srgb,var(--gilt) 20%,transparent);
  display:flex;flex-wrap:wrap;gap:9px;align-items:center}
.cx-cases a{font-size:12.5px;padding:6px 11px;border-radius:2px;text-decoration:none;
  border:1px solid color-mix(in srgb,var(--gilt) 30%,transparent);
  transition:border-color .24s var(--cx-ease),transform .24s var(--cx-ease)}
.cx-cases a:hover{border-color:var(--gilt);transform:translateY(-1px)}
.cx-more{margin-top:14px}
.cx-more a{font-family:var(--mono,ui-monospace,monospace);font-size:10px;
  letter-spacing:.18em;text-transform:uppercase;text-decoration:none;
  border-bottom:1px solid color-mix(in srgb,var(--gilt) 44%,transparent);padding-bottom:4px;
  transition:border-color .24s var(--cx-ease),color .24s var(--cx-ease)}
.cx-more a:hover{border-color:var(--gilt)}

/* ---- marginal apparatus boxes ---- */
.cx-box{position:relative;border-radius:3px;padding:20px 22px 20px 24px;
  border:1px solid color-mix(in srgb,var(--gilt) 22%,transparent);
  background:color-mix(in srgb,var(--gilt) 5%,transparent)}
.cx-box::before{content:"";position:absolute;left:0;top:18px;bottom:18px;width:2px;
  background:linear-gradient(180deg,var(--gilt),transparent)}
.cx-box-l{font-family:var(--mono,ui-monospace,monospace);font-size:9.5px;
  letter-spacing:.24em;text-transform:uppercase;color:var(--gilt);
  display:block;margin-bottom:10px}
.cx-box.breathe::before{background:linear-gradient(180deg,var(--sage-ac),transparent)}
.cx-box.breathe .cx-box-l{color:var(--sage-ac)}

/* ---- the threshold sequence ---- */
.wt-title{letter-spacing:-.022em;text-wrap:balance}
.wt-btn{transition:transform .22s var(--cx-ease),box-shadow .22s var(--cx-ease)}
.wt-btn:hover{transform:translateY(-2px)}
.entry-title{letter-spacing:-.022em;text-wrap:balance}

@media(max-width:560px){
  .cx-plate-head{gap:9px;padding:13px 13px}
  .cx-plate-t{font-size:.98rem}
  .cx-plate-body{padding:2px 13px 16px}
  .cx-reg{padding-left:15px}
}
@media (prefers-reduced-motion: reduce){
  .cx-plate,.cx-plate-chev,.cx-cases a,.wt-btn{transition:none}
  .cx-plate[open] .cx-plate-body{animation:none}
}
"""


def build(html):
    if MARK in html:
        return html
    html = re.sub(r'function secHead\(id,kicker,title\)\{.*?\n\}',
                  lambda m: SEC_JS, html, count=1, flags=re.S)
    html = re.sub(r'function relEntryHTML\(t, i, open\)\{.*?\n\}',
                  lambda m: REL_JS, html, count=1, flags=re.S)
    html = re.sub(r'function box\(kind,label,body\)\{.*?\n\}',
                  lambda m: BOX_JS, html, count=1, flags=re.S)
    return html.replace("</head>", '<style id="%s">%s</style>\n</head>' % (MARK, CSS), 1)
