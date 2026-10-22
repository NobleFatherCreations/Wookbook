/* The Pattern Decoder v10. Plain JS, no dependencies, offline.
   Data arrives once as JSON (#data); views render on demand into #main.
   Every route is a hash, so back/forward, bookmarks and shared links work. */
"use strict";
const D = JSON.parse(document.getElementById("data").textContent);
const $ = (s, el) => (el || document).querySelector(s);

/* ---------- small helpers ---------- */
function esc(s){return String(s==null?"":s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&#39;");}
/* Expand contractions while the apostrophe still marks them, so "won't" and
   "you're" survive normalisation as real words (carried over from v9). */
function expandContractions(s){
  return s
    .replace(/\bwon['’]t\b/g,"will not").replace(/\bcan['’]t\b/g,"can not")
    .replace(/\bshan['’]t\b/g,"shall not").replace(/n['’]t\b/g," not")
    .replace(/['’]re\b/g," are").replace(/['’]ve\b/g," have")
    .replace(/['’]ll\b/g," will").replace(/\bi['’]m\b/g,"i am")
    .replace(/['’]d\b/g," would").replace(/['’]s\b/g,"");
}
function norm(s){return expandContractions((s||"").toLowerCase()).replace(/[^a-z0-9]+/g," ").trim();}
function safeDecode(s){try{return decodeURIComponent(s)}catch(e){return String(s||"")}}
/* Typographic quotes for display: names are stored with straight quotes. */
function curly(s){return String(s).replace(/(^|[\s(—-])"/g,"$1“").replace(/"/g,"”").replace(/(^|[\s(])'/g,"$1‘").replace(/'/g,"’");}
const H = s => esc(curly(s));
function ic(name){return '<svg class="i" viewBox="0 0 24 24" aria-hidden="true">'+(ICONS[name]||"")+'</svg>';}
const ICONS={
  search:'<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
  close:'<path d="M18 6 6 18M6 6l12 12"/>',
  home:'<path d="M3 10.5 12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6h-6v6H4a1 1 0 0 1-1-1z"/>',
  grid:'<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>',
  compass:'<circle cx="12" cy="12" r="9"/><path d="m15.5 8.5-2 5-5 2 2-5z"/>',
  star:'<path d="m12 3 2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z"/>',
  starOn:'<path fill="currentColor" d="m12 3 2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z"/>',
  shield:'<path d="M12 3 4 6v6c0 4.5 3.4 8.4 8 9 4.6-.6 8-4.5 8-9V6z"/>',
  moon:'<path d="M20 14.5A8 8 0 0 1 9.5 4 8 8 0 1 0 20 14.5z"/>',
  sun:'<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
  copy:'<rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V5a2 2 0 0 1 2-2h10"/>',
  share:'<path d="M12 3v13M7 8l5-5 5 5"/><path d="M5 13v6a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-6"/>',
  print:'<path d="M7 9V3h10v6"/><rect x="3" y="9" width="18" height="8" rx="2"/><path d="M7 14h10v7H7z"/>',
  chevron:'<path d="m9 6 6 6-6 6"/>',
  check:'<path d="m5 12 5 5 9-10"/>',
  lock:'<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
  link:'<path d="M10 14a5 5 0 0 0 7 0l3-3a5 5 0 0 0-7-7l-1 1"/><path d="M14 10a5 5 0 0 0-7 0l-3 3a5 5 0 0 0 7 7l1-1"/>',
  steps:'<path d="M4 6h10M4 12h16M4 18h7"/>',
};

/* ---------- indexes ---------- */
const E = D.entries;
const BY = {}, BY_SLUG = {};
E.forEach((e,i)=>{ e.i=i; BY[e.n]=e; BY_SLUG[e.s]=e; });
const ALPHA = [...E].sort((a,b)=>a.n.localeCompare(b.n));
const GROUP = {}; D.groups.forEach(g=>GROUP[g.k]=g);
const SET = {}; D.settings.forEach(s=>SET[s.k]=s);
const IN_GROUP = {}; D.groups.forEach(g=>IN_GROUP[g.k]=E.filter(e=>e.g===g.k).sort((a,b)=>a.n.localeCompare(b.n)));
const ALIAS_SLUG = {}; Object.keys(D.aliases).forEach(a=>ALIAS_SLUG[slugify(a)]=D.aliases[a]);
function slugify(s){return (s||"").toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/(^-+|-+$)/g,"")||"x";}
const PATS_OF = {}; D.recipes.forEach((r,ri)=>r.c.forEach(n=>(PATS_OF[n]=PATS_OF[n]||[]).push(ri)));
const HAY = E.map(e=>({
  name:norm(e.n), names:[norm(e.n)].concat((e.abs||[]).map(norm)),
  said:norm((e.f.what_it_sounds_like||[]).join(" ")),
  words:norm((e.kw||[]).join(" ")),
  all:norm([e.n,(e.abs||[]).join(" "),e.sub||"",(e.kw||[]).join(" "),e.f.short_definition,e.f.plain_language_summary,(e.f.what_it_sounds_like||[]).join(" ")].join(" ")),
}));

/* ---------- storage (device only; survives being unavailable) ---------- */
const store=(()=>{let mem={},ok=false;
  try{localStorage.setItem("__t","1");localStorage.removeItem("__t");ok=true}catch(e){}
  return{
    get(k,d){try{if(ok){const v=localStorage.getItem("fg_"+k);if(v!==null){const p=JSON.parse(v);
      if(Array.isArray(d)&&!Array.isArray(p))return d; if(typeof d==="string"&&typeof p!=="string")return d; return p;}return d}}catch(e){}
      return (k in mem)?mem[k]:d},
    set(k,v){mem[k]=v;try{if(ok)localStorage.setItem("fg_"+k,JSON.stringify(v))}catch(e){ok=false}},
  };})();
/* Saved items from before the merge may name a tactic that is now an alias. */
(function normaliseSaved(){
  const canon=n=>D.aliases[n]||n;
  const tr=store.get("trail",[]), st=store.get("starred",[]);
  const seen=new Set(), t2=[];
  tr.forEach(t=>{ if(!t||typeof t.name!=="string")return; const c=canon(t.name); if(!BY[c]||seen.has(c))return; seen.add(c); t2.push({name:c,ts:t.ts}); });
  store.set("trail",t2);
  const s2=[...new Set(st.filter(n=>typeof n==="string").map(canon))].filter(n=>BY[n]);
  store.set("starred",s2);
})();
function isStarred(n){return store.get("starred",[]).includes(n)}
function toggleStar(n){let s=store.get("starred",[]); s=s.includes(n)?s.filter(x=>x!==n):[n].concat(s); store.set("starred",s); return s.includes(n);}
function logTrail(n){let t=store.get("trail",[]).filter(x=>x.name!==n); t.unshift({name:n,ts:Date.now()}); store.set("trail",t.slice(0,200));}

/* ---------- links ---------- */
const href = h => "#/"+h;
const entryHref = e => href("entry/"+e.s);
function rowHTML(e, opts){
  opts=opts||{};
  return '<a class="row" href="'+entryHref(e)+'" data-vt="'+e.i+'">'+
    '<span class="nm"><span data-vtn="'+e.i+'">'+H(e.n)+'</span>'+(e.sens?'<span class="dot-safe" title="Safety-sensitive">'+ic("shield")+'<span class="sr-only">Safety-sensitive</span></span>':'')+'</span>'+
    (e.sub?'<span class="sub">'+H(e.sub)+'</span>':'')+
    '<span class="df">'+H(e.f.short_definition)+'</span>'+
    (opts.group?'<span class="meta">'+H(GROUP[e.g].label)+'</span>':'')+
  '</a>';
}
function rows(list,opts){return '<div class="rows">'+list.map(e=>rowHTML(e,opts)).join("")+'</div>';}
function ul(items,cls){return items&&items.length?'<ul'+(cls?' class="'+cls+'"':'')+'>'+items.map(x=>'<li>'+H(x)+'</li>').join("")+'</ul>':"";}
function blk(title,inner,cls){return inner?'<div class="blk'+(cls?' '+cls:'')+'"><h3>'+title+'</h3>'+inner+'</div>':"";}

/* ---------- search ---------- */
const STOP = new Set(D.stop);
function searchTokens(n){return n.split(" ").filter(w=>w.length>2&&!STOP.has(w));}
/* Ranking carried over from v9 (name > folded-in name > what people say > the rest),
   plus everyday words written for each entry, so "ignoring me" finds the silent treatment. */
function search(q){
  const n=norm(String(q||"").slice(0,400));
  if(!n) return {list:[],fuzzy:false,n};
  let list=[];
  if(n.replace(/ /g,"").length>=2){
    list=E.map((e,i)=>{const h=HAY[i]; if(!h.all.includes(n)) return null;
      const r=h.names.some(x=>x===n)?0:h.names.some(x=>x.startsWith(n))?1:h.names.some(x=>x.includes(n))?2:h.words.includes(n)?3:h.said.includes(n)?4:5;
      return {e,r};}).filter(Boolean).sort((a,b)=>a.r-b.r||a.e.n.localeCompare(b.e.n)).map(x=>x.e);
    if(n.length<4&&list.length>40) list=[];
  }
  if(list.length) return {list,fuzzy:false,n};
  const toks=searchTokens(n); if(!toks.length) return {list:[],fuzzy:false,n};
  const w=n.split(" "), grams=[];
  for(let i=0;i<w.length-1;i++){grams.push(w[i]+" "+w[i+1]); if(i<w.length-2) grams.push(w[i]+" "+w[i+1]+" "+w[i+2]);}
  const scored=[];
  E.forEach((e,i)=>{const h=HAY[i]; let hits=0,score=0;
    toks.forEach(t=>{ if(!h.all.includes(t)) return; hits++; score+= h.name.includes(t)?4 : h.words.includes(t)?3 : h.said.includes(t)?3 : 1; });
    if(!hits) return;
    grams.forEach(g=>{ if(h.said.includes(g)||h.words.includes(g)) score+=6; else if(h.all.includes(g)) score+=2; });
    scored.push({e,hits,score});});
  const need=toks.length<=2?toks.length:Math.min(4,Math.ceil(toks.length/2));
  const kept=scored.filter(x=>x.hits>=need).sort((a,b)=>b.score-a.score||b.hits-a.hits||a.e.n.localeCompare(b.e.n));
  const top=kept.length?kept[0].score:0;
  return {list:kept.filter(x=>x.score>=Math.max(2,top*.5)).slice(0,12).map(x=>x.e),fuzzy:true,n};
}
/* Held in memory, never in the URL: what someone pastes here can be what was
   said to them, and it must not land in history, the address bar or autocomplete. */
let SEARCH_Q = "";
function searchBox(id,value,autofocus){
  return '<form class="search'+(value?' has':'')+'" role="search" data-search>'+
    '<span class="s-ic">'+ic("search")+'</span>'+
    '<label class="sr-only" for="'+id+'">Search the guide</label>'+
    '<input id="'+id+'" type="search" enterkeyhint="search" autocomplete="off" autocapitalize="off" spellcheck="false" value="'+esc(value||"")+'" placeholder="What happened? Or a name"'+(autofocus?' autofocus':'')+'>'+
    '<button type="button" class="s-clear" data-clear aria-label="Clear search">'+ic("close")+'</button></form>';
}

/* ---------- views ---------- */
function viewHome(){
  const trail=store.get("trail",[]);
  const last=trail[0]&&BY[trail[0].name];
  return '<section class="hero">'+
    '<div>'+
      '<h1 class="sr-only">The Pattern Decoder</h1>'+
      '<span class="hero-mark" aria-hidden="true">'+D.wordmark+'</span>'+
      '<p class="h2" style="max-width:20ch">Put a name to what is happening.</p>'+
      '<p class="lede">'+E.length+' manipulation and control tactics, each explained in plain words: what it looks like, how to tell if it fits, and what you can do.</p>'+
      '<div style="margin-top:32px">'+searchBox("q-home","")+'</div>'+
      '<div class="tries"><span class="muted">Try</span>'+D.tries.map(t=>'<button class="chip" type="button" data-try="'+esc(t)+'">'+H(t)+'</button>').join("")+'</div>'+
      '<p class="privacy">'+ic("lock")+'Nothing you type leaves this device.</p>'+
    '</div>'+
    '<figure class="hero-art" style="margin:0"><img src="'+D.cover+'" alt="An engraved star chart in gold on deep indigo, its constellations drawn as people: one turning away, a hand on a shoulder, a pair of watching eyes." width="1800" height="1004" fetchpriority="high" decoding="async"></figure>'+
  '</section>'+
  (last?'<div class="continue"><p class="small">You were reading <strong>'+H(last.n)+'</strong></p><a class="btn" href="'+entryHref(last)+'">Continue</a></div>':'')+
  '<div class="ways">'+
    way("guide","compass","Help me figure it out","Answer two short questions about what has been happening. No names needed.","Start")+
    way("browse","grid","Browse by what it does",D.groups.length+" plain groups, from twisting the truth to control over money.","Browse")+
    way("common","star","Start with the most common","The "+D.common.length+" tactics people run into most often.","See them")+
  '</div>'+
  '<section class="sect"><div class="sect-head"><div><h2 class="h2">Browse by what it does</h2><p>Every tactic sits in one group. Open a group to see them all.</p></div><a class="btn ghost" href="'+href("all")+'">A–Z of all '+E.length+'</a></div>'+
  groupTiles()+'</section>'+
  '<section class="sect"><div class="sect-head"><div><h2 class="h2">Where is it happening?</h2><p>Narrow the guide to one part of life.</p></div></div>'+
  '<div class="chips">'+D.settings.map(s=>'<a class="chip" href="'+href("where/"+s.k)+'">'+H(s.label)+' <span class="n">'+E.filter(e=>(e.w||[]).includes(s.k)).length+'</span></a>').join("")+'</div></section>';
}
function way(route,icon,title,text,go){
  return '<a class="way" href="'+href(route)+'"><span class="w-ic">'+ic(icon)+'</span><span><h2>'+title+'</h2><p>'+text+'</p></span><span class="go">'+go+'</span></a>';
}
function groupTiles(){
  return '<div class="groups">'+D.groups.map(g=>{
    const list=IN_GROUP[g.k];
    return '<a class="group" href="'+href("browse/"+g.k)+'"><h3>'+H(g.label)+'</h3><p>'+H(g.blurb)+'</p><span class="eg">'+list.length+' tactics, including '+list.slice().sort((a,b)=>(b.pop||0)-(a.pop||0)).slice(0,2).map(e=>H(e.n)).join(" and ")+'</span></a>';
  }).join("")+'</div>';
}
function viewSearch(){
  const r=search(SEARCH_Q);
  return '<p class="eyebrow"><a href="'+href("")+'">Home</a></p><h1 class="h1">Search</h1>'+
    '<div style="margin-top:24px">'+searchBox("q-page",SEARCH_Q,true)+'</div>'+
    '<div id="results" aria-live="polite">'+resultsHTML(r)+'</div>';
}
function resultsHTML(r){
  if(!r.n) return '<p class="small muted" style="margin-top:24px">Search by name ("gaslighting"), by everyday words ("ignoring me"), or paste something that was said to you. Press / from anywhere to search.</p>'+
    '<div class="tries">'+D.tries.map(t=>'<button class="chip" type="button" data-try="'+esc(t)+'">'+H(t)+'</button>').join("")+'</div>';
  if(!r.list.length) return '<div class="empty" style="margin-top:24px"><p><strong>Nothing matched that wording.</strong></p><p class="small muted">Search goes by words, so an unusual phrasing can miss a tactic that is here. Two short questions work from what happened instead.</p>'+
    '<div class="chips" style="justify-content:center"><a class="btn primary" href="'+href("guide")+'">Help me figure it out</a><a class="btn" href="'+href("browse")+'">Browse the groups</a></div></div>';
  return '<p class="count">'+(r.fuzzy?(r.list.length===1?'1 close match':r.list.length+' close matches'):(r.list.length===1?'1 result':r.list.length+' results'))+'</p>'+
    (r.fuzzy?'<p class="small muted" style="margin-top:-8px">No entry used those exact words, so these are ranked by how much of what you typed they share.</p>':'')+
    rows(r.list,{group:true});
}
function viewBrowse(){
  return '<p class="eyebrow"><a href="'+href("")+'">Home</a></p><h1 class="h1">Browse by what it does</h1>'+
    '<p class="lede">'+D.groups.length+' groups. Each tactic sits in the one that fits it best, and links to its close relatives in other groups.</p>'+
    '<div style="margin-top:40px">'+groupTiles()+'</div>'+
    '<section class="sect"><div class="sect-head"><div><h2 class="h2">Or by where it happens</h2></div></div><div class="chips">'+
    D.settings.map(s=>'<a class="chip" href="'+href("where/"+s.k)+'">'+H(s.label)+'</a>').join("")+'</div></section>';
}
let FILTER_SET = "";
function viewGroup(k){
  const g=GROUP[k]; if(!g) return notFound();
  const all=IN_GROUP[k];
  const counts=D.settings.map(s=>({s,n:all.filter(e=>(e.w||[]).includes(s.k)).length})).filter(x=>x.n);
  const list=FILTER_SET?all.filter(e=>(e.w||[]).includes(FILTER_SET)):all;
  return '<p class="eyebrow"><a href="'+href("browse")+'">Browse</a></p><h1 class="h1">'+H(g.label)+'</h1><p class="lede">'+H(g.blurb)+'</p>'+
    '<div class="chips" style="margin-top:32px" role="group" aria-label="Where it happens">'+
      '<button class="chip" type="button" data-setfilter="" aria-pressed="'+(!FILTER_SET)+'">Everywhere <span class="n">'+all.length+'</span></button>'+
      counts.map(x=>'<button class="chip" type="button" data-setfilter="'+x.s.k+'" aria-pressed="'+(FILTER_SET===x.s.k)+'">'+H(x.s.label)+' <span class="n">'+x.n+'</span></button>').join("")+
    '</div><p class="count">'+list.length+' tactics</p>'+rows(list);
}
function viewWhere(k){
  const s=SET[k]; if(!s) return notFound();
  const list=E.filter(e=>(e.w||[]).includes(k));
  return '<p class="eyebrow"><a href="'+href("browse")+'">Browse</a></p><h1 class="h1">'+H(s.label)+'</h1><p class="lede">'+H(s.blurb)+'</p>'+
    D.groups.map(g=>{const l=list.filter(e=>e.g===g.k).sort((a,b)=>a.n.localeCompare(b.n)); return l.length?'<section class="sect" style="margin-top:48px"><h2 class="h2" style="margin-bottom:16px">'+H(g.label)+'</h2>'+rows(l)+'</section>':"";}).join("");
}
function viewCommon(){
  const list=D.common.map(n=>BY[n]).filter(Boolean);
  return '<p class="eyebrow"><a href="'+href("")+'">Home</a></p><h1 class="h1">The most common</h1>'+
    '<p class="lede">If you are not sure where to begin, begin here. These '+list.length+' come up most often, alone and as parts of larger patterns.</p>'+
    D.groups.map(g=>{const l=list.filter(e=>e.g===g.k); return l.length?'<section class="sect" style="margin-top:48px"><h2 class="h2" style="margin-bottom:16px">'+H(g.label)+'</h2>'+rows(l)+'</section>':"";}).join("");
}
let AZ_Q = "";
function viewAll(){
  return '<p class="eyebrow"><a href="'+href("browse")+'">Browse</a></p><h1 class="h1">A–Z</h1><p class="lede">All '+E.length+' tactics. Names that were merged into another entry are listed under the entry that covers them.</p>'+
    '<div style="margin-top:32px"><label class="sr-only" for="azf">Filter by name</label><input id="azf" class="filter" type="search" placeholder="Filter by name" value="'+esc(AZ_Q)+'" autocomplete="off"></div>'+
    '<div id="azlist">'+azList()+'</div>';
}
function azList(){
  const q=norm(AZ_Q);
  const list=q?ALPHA.filter(e=>HAY[e.i].names.some(x=>x.includes(q))):ALPHA;
  const letters={};
  list.forEach(e=>{const L=(e.n.replace(/^[^A-Za-z]+/,"")[0]||"#").toUpperCase(); (letters[L]=letters[L]||[]).push(e);});
  const keys=Object.keys(letters).sort();
  return (q?'':'<nav class="az" aria-label="Jump to letter">'+keys.map(L=>'<a href="#" data-jump="L-'+L+'">'+L+'</a>').join("")+'</nav>')+
    '<p class="count">'+list.length+' tactics</p>'+
    keys.map(L=>'<h2 class="letter" id="L-'+L+'">'+L+'</h2>'+rows(letters[L],{group:true})).join("");
}

/* ---------- the entry ---------- */
const RESP = [["soft_clarification","Ask about it gently"],["firm_boundary","Set a clear limit"],["disengagement","Step back"],["support_seeking","Get support"],["workplace_or_professional","At work, school or with services"]];
/* A part of the entry: open by default on wide screens, folded behind its
   heading on a phone so the page starts as a 30-second read. */
function part(id,title,hint,inner){
  return '<details class="part" id="'+id+'"'+(OPEN_PARTS?' open':'')+'><summary><span class="p-t"><h2 class="h2">'+title+'</h2><span class="p-h">'+hint+'</span></span><span class="p-ic">'+ic("chevron")+'</span></summary><div class="p-body">'+inner+'</div></details>';
}
let OPEN_PARTS = !matchMedia("(max-width: 760px)").matches;
const PARTS = [["short","In short"],["understand","Understand it"],["fit","Is this it?"],["do","What you can do"],["deeper","Go deeper"]];
function viewEntry(slug){
  let e=BY_SLUG[slug];
  if(!e&&ALIAS_SLUG[slug]){ e=BY[ALIAS_SLUG[slug]]; try{history.replaceState(null,"",entryHref(e))}catch(x){} }
  if(!e) return notFound();
  logTrail(e.n);
  const f=e.f, g=GROUP[e.g], starred=isStarred(e.n);
  const inG=IN_GROUP[e.g], gi=inG.indexOf(e);
  const prev=inG[(gi-1+inG.length)%inG.length], next=inG[(gi+1)%inG.length];
  const says=(f.what_it_sounds_like||[]);
  const toc=PARTS.map(p=>'<a href="#'+p[0]+'" data-part="'+p[0]+'">'+p[1]+'</a>').join("");
  const safety = e.sens
    ? '<div class="callout" role="note"><h3>'+ic("shield")+'Your safety comes first</h3><p>'+H(f.safety_note)+'</p><p class="small" style="margin-top:8px"><a href="'+href("about")+'">How to use this guide safely</a></p></div>'
    : '';
  const pats=(PATS_OF[e.n]||[]).map(ri=>D.recipes[ri]);
  return '<article class="entry">'+
    '<nav class="toc" aria-label="On this page">'+toc+'</nav>'+
    '<div>'+
    '<header class="e-head">'+
      '<p class="eyebrow"><a href="'+href("browse")+'">Browse</a> <span aria-hidden="true">/</span> <a href="'+href("browse/"+g.k)+'">'+H(g.label)+'</a></p>'+
      '<h1 class="h1" style="--vt:t'+e.i+'">'+H(e.n)+'</h1>'+
      (e.sub?'<p class="e-sub">'+H(e.sub)+'</p>':'')+
      '<div class="e-meta">'+(e.sens?'<span class="badge safety">'+ic("shield")+'Safety-sensitive</span>':'')+
        (e.abs&&e.abs.length?'<span>Also called '+e.abs.map(H).join(", ")+'</span>':'')+'</div>'+
      '<div class="e-actions">'+
        '<button class="btn" type="button" data-star="'+esc(e.n)+'" aria-pressed="'+starred+'">'+ic(starred?"starOn":"star")+'<span>'+(starred?"Saved":"Save")+'</span></button>'+
        '<button class="btn" type="button" data-share>'+ic("share")+'Share link</button>'+
        '<button class="btn" type="button" data-print>'+ic("print")+'Print</button>'+
      '</div>'+
    '</header>'+
    '<nav class="chipbar" aria-label="Jump to a part">'+PARTS.map(p=>'<a class="chip" href="#'+p[0]+'" data-part="'+p[0]+'">'+p[1]+'</a>').join("")+'<button class="chip open-all" type="button" data-openall>Open all</button></nav>'+

    '<section class="part" id="short" aria-labelledby="h-short" style="padding-top:24px"><h2 class="sr-only" id="h-short">In short</h2>'+
      '<div class="short"><p class="sum">'+H(f.plain_language_summary)+'</p>'+
      (says.length?'<p class="says-h">It can sound like</p><ul class="says">'+says.slice(0,3).map(s=>'<li>'+H(s)+'</li>').join("")+'</ul>':'')+
      (f.this_may_not_be_it_when&&f.this_may_not_be_it_when.length?'<p class="says-h">It may be something else if</p>'+ul(f.this_may_not_be_it_when.slice(0,2),"away"):'')+
      '</div>'+safety+
    '</section>'+
    part("understand","Understand it","What it is, why it matters, and how it shows up",
      '<div class="text"><p>'+H(f.expanded_definition)+'</p><p>'+H(f.why_this_matters)+'</p></div>'+
      blk("How it shows up",ul(f.what_it_is))+
      (says.length>3?blk("More things people say",ul(says.slice(3),"said")):""))+
    part("fit","Is this it?","Signs in both directions, and questions to ask yourself",
      '<p class="intro">One moment proves very little. Weigh it honestly, in both directions.</p>'+
      '<div class="compare"><div class="tw"><h3>Signs it might be this</h3>'+ul(f.this_may_be_it_when)+'</div><div class="aw"><h3>Signs it is probably something else</h3>'+ul(f.this_may_not_be_it_when.slice(2).concat(f.less_concerning_if))+'</div></div>'+
      blk("Questions to ask yourself",ul(f.discernment_questions),"qs")+
      blk("More worrying if",ul(f.more_concerning_if))+
      blk("What shows up over time",ul(f.pattern_over_time_signs))+
      blk("What it is not",ul(f.what_it_is_not))+
      blk("Ordinary explanations",ul(f.innocent_or_ordinary_possibilities))+
      blk("Often mistaken for this",ul(f.common_false_positives)))+
    part("do","What you can do","Words you could use, ways to respond, and signs of change",
      (e.sens?'<p class="intro">Read the safety note first. If speaking up could make things worse, skip the wording below and talk to someone you trust or a local support service.</p>':'<p class="intro">Pick what fits. You do not owe anyone a confrontation.</p>')+
      '<div class="script"><p class="lbl">'+(e.kind==="verify"?"A check to run before you share or act":"Words you could use")+'</p><blockquote id="bs">'+H(f.boundary_script.replace(/^Verification script[^:]*:\s*/i,""))+'</blockquote>'+
        '<div class="row-act"><button class="btn" type="button" data-copy="bs">'+ic("copy")+'<span>Copy</span></button></div></div>'+
      '<div class="blk"><h3>Ways to respond</h3><div class="resp">'+RESP.map(r=>f.response_options&&f.response_options[r[0]]?'<div><h4>'+r[1]+'</h4><p>'+H(f.response_options[r[0]])+'</p></div>':'').join("")+'</div></div>'+
      blk("Is it changing?",'<p>'+H(f.boundary_respect_check)+'</p><p>'+H(f.repair_check)+'</p>')+
      (!e.sens?'<div class="note"><h3>When to take it more seriously</h3><p>'+H(f.safety_note)+'</p></div>':''))+
    part("deeper","Go deeper","How it works, its effects, and its close relatives",
      blk("How it works",'<p>'+H(f.psychological_mechanism)+'</p>')+
      blk("How it can affect you",'<p>'+H(f.possible_impact_on_receiver)+'</p>')+
      blk("Telling it apart from its neighbours",'<p>'+H(f.how_to_distinguish_from_related)+'</p>'+
        (e.rel&&e.rel.length?'<div class="related">'+e.rel.map(n=>BY[n]?'<a class="chip" href="'+entryHref(BY[n])+'">'+H(n)+'</a>':'').join("")+'</div>':''))+
      blk("Using this label fairly",ul(f.misuse_warning))+
      (pats.length?blk("Patterns it is part of",'<div class="pats">'+pats.slice(0,6).map(r=>'<a href="'+href("patterns/"+slugify(r.n))+'"><b>'+H(r.n)+'</b><span>'+r.c.length+' tactics in sequence</span></a>').join("")+'</div>'):""))+

    '<nav class="pn" aria-label="More in '+esc(g.label)+'">'+
      '<a href="'+entryHref(prev)+'"><span class="k">Previous in '+H(g.label)+'</span><span class="t">'+H(prev.n)+'</span></a>'+
      '<a class="nx" href="'+entryHref(next)+'"><span class="k">Next</span><span class="t">'+H(next.n)+'</span></a>'+
    '</nav>'+
    '<p class="back-to"><a class="btn ghost" href="'+href("browse/"+g.k)+'">All '+inG.length+' in '+H(g.label)+'</a></p>'+
    '</div></article>';
}

/* ---------- guide: two questions, then a short list ---------- */
let GUIDE = {step:0, where:null, feels:[]};
function guideList(){
  const tally={};
  GUIDE.feels.forEach(k=>(D.narrow[k]||[]).forEach((n,rank)=>{ tally[n]=(tally[n]||0)+10-Math.min(rank,9)/2; }));
  return Object.keys(tally).filter(n=>BY[n]).sort((a,b)=>tally[b]-tally[a]||a.localeCompare(b)).slice(0,18).map(n=>BY[n]);
}
function viewGuide(){
  const steps='<div class="steps" aria-hidden="true">'+[0,1,2].map(i=>'<i class="'+(i<=GUIDE.step?"on":"")+'"></i>').join("")+'</div>';
  const head='<p class="eyebrow"><a href="'+href("")+'">Home</a> <span aria-hidden="true">/</span> Help me figure it out</p>'+steps;
  if(GUIDE.step===0){
    return head+'<h1 class="h1">Where has this been happening?</h1>'+
      '<p class="lede">There are no wrong answers, and nothing you pick is stored anywhere but this device.</p>'+
      '<div class="opts">'+D.feelingGroups.map(g=>'<button class="opt" type="button" data-where="'+g.key+'"><span>'+H(g.label)+'</span></button>').join("")+
      '<button class="opt" type="button" data-where=""><span>I am not sure, or more than one</span></button></div>';
  }
  if(GUIDE.step===1){
    const pool=D.feelings.filter(f=>!GUIDE.where||f.group===GUIDE.where);
    return head+'<h1 class="h1">Which of these sound like it?</h1>'+
      '<p class="lede">Pick as many as fit. Each one adds possibilities.</p>'+
      '<div class="opts">'+pool.map(f=>{const on=GUIDE.feels.includes(f.key); return '<button class="opt" type="button" data-feel="'+f.key+'" aria-pressed="'+on+'"><span class="bx">'+ic("check")+'</span><span>'+H(f.label)+'</span></button>';}).join("")+'</div>'+
      '<div class="guide-bar"><button class="btn ghost" type="button" data-gstep="0">Back</button>'+
      '<span class="small muted" aria-live="polite">'+(GUIDE.feels.length?GUIDE.feels.length+' picked':'Pick at least one')+'</span>'+
      '<button class="btn primary" type="button" data-gstep="2"'+(GUIDE.feels.length?'':' disabled')+'>Show what fits</button></div>';
  }
  const list=guideList();
  const sens=list.filter(e=>e.sens).length;
  return head+'<h1 class="h1">These are worth a look</h1>'+
    '<p class="lede">Start with the first few. Each entry helps you check whether it really fits, and what you can do.</p>'+
    (sens?'<div class="callout"><h3>'+ic("shield")+'If you feel unsafe</h3><p>Some of these can come with real danger. If you are afraid of someone, reach a person you trust, a local support service, or emergency services if you are in immediate danger. <a href="'+href("about")+'">More on staying safe</a></p></div>':'')+
    '<p class="count">'+list.length+' possibilities</p>'+rows(list,{group:true})+
    '<div class="chips" style="margin-top:32px"><button class="btn" type="button" data-gstep="1">Change my answers</button><button class="btn ghost" type="button" data-greset>Start over</button></div>';
}

/* ---------- patterns ---------- */
function viewPatterns(k){
  if(k){
    const r=D.recipes.find(x=>slugify(x.n)===k); if(!r) return notFound();
    return '<p class="eyebrow"><a href="'+href("patterns")+'">How tactics combine</a></p><h1 class="h1">'+H(r.n)+'</h1><p class="lede">'+H(r.d)+'</p>'+
      '<ol class="chain">'+r.c.map(n=>{const e=BY[n]; return e?'<li><a href="'+entryHref(e)+'">'+H(e.n)+'</a><p>'+H(e.f.short_definition)+'</p></li>':'';}).join("")+'</ol>';
  }
  return '<p class="eyebrow"><a href="'+href("")+'">Home</a></p><h1 class="h1">How tactics combine</h1>'+
    '<p class="lede">Tactics rarely arrive alone. These '+D.recipes.length+' patterns show how several tend to follow one another, step by step.</p>'+
    '<div class="rows" style="margin-top:40px">'+D.recipes.map(r=>'<a class="row" href="'+href("patterns/"+slugify(r.n))+'"><span class="nm">'+H(r.n)+'</span><span class="df">'+H(r.d)+'</span><span class="meta">'+r.c.length+' steps</span></a>').join("")+'</div>';
}

/* ---------- saved ---------- */
function viewSaved(){
  const st=store.get("starred",[]).map(n=>BY[n]).filter(Boolean);
  const tr=store.get("trail",[]).map(t=>BY[t.name]).filter(Boolean).slice(0,24);
  return '<p class="eyebrow"><a href="'+href("")+'">Home</a></p><h1 class="h1">Saved and recent</h1>'+
    '<p class="lede">Kept on this device only. Clearing your browser data clears these too.</p>'+
    '<section class="sect" style="margin-top:48px"><h2 class="h2" style="margin-bottom:16px">Saved</h2>'+(st.length?rows(st,{group:true}):'<div class="empty"><p class="muted">Tap Save on any entry to keep it here.</p></div>')+'</section>'+
    '<section class="sect" style="margin-top:48px"><h2 class="h2" style="margin-bottom:16px">Recently read</h2>'+(tr.length?rows(tr,{group:true}):'<div class="empty"><p class="muted">Entries you open will show up here.</p></div>')+'</section>'+
    (st.length||tr.length?'<p style="margin-top:32px"><button class="btn ghost" type="button" data-clearsaved>Clear saved and recent</button></p>':'');
}

/* ---------- about / safety ---------- */
function viewAbout(){
  const p=t=>'<p>'+t+'</p>', h=t=>'<h2 class="h2" style="margin:48px 0 16px">'+t+'</h2>';
  return '<div class="read"><p class="eyebrow"><a href="'+href("")+'">Home</a></p><h1 class="h1">How to use this guide safely</h1>'+
    '<p class="lede">What applies to every entry, said once.</p>'+
    '<div class="callout" style="margin-top:32px"><h3>'+ic("shield")+'If you are not safe</h3><p>If any of this involves threats, being watched or tracked, being cut off from people or money, housing or immigration status, sex, pressure toward self-harm, or fear for your safety, reach a real person: someone you trust, a local support service, a legal or workplace resource, or emergency services if you are in immediate danger. Entries marked Safety-sensitive say more about what to watch for.</p></div>'+
    h("What this guide is")+p("A reading aid. It helps you put a name to something that happened, see what else it could be, and decide what to do next. Some entries are about everyday relationships; others are about workplaces, online life, and influence on a whole society.")+
    h("What it is not")+p("It is not a diagnosis, a legal opinion, or therapy. It cannot tell you what another person meant, what they are like, or whether you are in danger. Only you, and the people you trust, can weigh that.")+
    h("A signal, not a verdict")+p("One example of a pattern is a reason to look more closely, not proof of motive or character. Every entry says what its tactic is not, because most of these behaviors also have ordinary explanations. Please do not use a label from this guide to attack, shame, threaten, expose or get back at someone.")+
    h("The search box")+p("Pasting in something that was said to you finds entries whose wording is close to it. That is a pointer to read further, never a finding. It cannot see the tone, the history, or whether the words were meant seriously. What you type is never added to the address bar or your history.")+
    h("Your privacy")+p("There is no account. Your saved and recent entries stay on this device. The page counts anonymous visits, and nothing you type, paste or save is sent anywhere.")+
    h("What changed")+'<p class="small muted">'+esc(D.version)+'</p><ul class="updates">'+D.updates.map(u=>'<li>'+u+'</li>').join("")+'</ul>'+
  '</div>';
}
function notFound(){
  return '<div class="empty" style="margin-top:40px"><p><strong>That page is not here.</strong></p><p class="small muted">The link may be out of date or cut short.</p><div class="chips" style="justify-content:center"><a class="btn primary" href="'+href("")+'">Go home</a><a class="btn" href="'+href("search")+'">Search</a></div></div>';
}

/* ---------- router ---------- */
function parse(){
  const raw=(location.hash||"").replace(/^#\/?/,"");
  const parts=raw.split("/").map(safeDecode);
  return {view:parts[0]||"", arg:parts.slice(1).join("/")};
}
/* Old v9 routes keep working. */
const LEGACY={core:"common",trail:"saved",narrow:"guide",index:"all",constellation:"browse",category:"browse",feeling:"guide"};
const ROUTES={"":viewHome,search:viewSearch,browse:a=>a?viewGroup(a):viewBrowse(),where:viewWhere,common:viewCommon,all:viewAll,
  entry:viewEntry,guide:viewGuide,patterns:viewPatterns,saved:viewSaved,about:viewAbout};
const SCROLL = {};
let FRESH = false, LAST_KEY = null, PENDING_VT = null;
function key(){return location.hash||"#/";}
function render(){
  let r=parse();
  if(LEGACY[r.view]){
    /* a v9 category link names a v9 category; send it to its new group when one matches */
    let to=LEGACY[r.view];
    if(r.view==="category"&&r.arg&&D.catToGroup[r.arg]) to="browse/"+D.catToGroup[r.arg];
    try{history.replaceState(null,"",href(to))}catch(e){} r=parse();
  }
  const fn=ROUTES[r.view];
  const html=fn?fn(r.arg):notFound();
  const main=$("#main");
  const go=()=>{
    main.innerHTML='<div class="wrap view">'+html+'</div>';
    setNav(r.view);
    document.title=titleFor(r);
    const k=key();
    if(!FRESH&&SCROLL[k]!=null) window.scrollTo(0,SCROLL[k]);
    else if(r.view==="entry"&&location.hash.indexOf("#",1)>0){}
    else window.scrollTo(0,0);
    FRESH=false; LAST_KEY=k;
    afterRender(r);
  };
  const reduce=matchMedia("(prefers-reduced-motion: reduce)").matches;
  if(document.startViewTransition&&!reduce&&LAST_KEY!==null){
    if(PENDING_VT!=null){ const t=$('[data-vtn="'+PENDING_VT+'"]'); if(t) t.style.viewTransitionName="t"+PENDING_VT; }
    document.startViewTransition(go); PENDING_VT=null;
  } else go();
}
function titleFor(r){
  const base="The Pattern Decoder";
  if(r.view==="entry"){const e=BY_SLUG[r.arg]||BY[ALIAS_SLUG[r.arg]]; return e?curly(e.n)+" — "+base:base;}
  if(r.view==="browse"&&r.arg&&GROUP[r.arg]) return GROUP[r.arg].label+" — "+base;
  const t={search:"Search",browse:"Browse",where:"Where it happens",common:"The most common",all:"A–Z",guide:"Help me figure it out",patterns:"How tactics combine",saved:"Saved and recent",about:"Use this safely"}[r.view];
  return t?t+" — "+base:base+" — "+E.length+" manipulation and control tactics, explained";
}
function setNav(view){
  const map={"":"home",search:"search",browse:"browse",where:"browse",all:"browse",common:"browse",entry:"browse",guide:"guide",patterns:"browse",saved:"saved",about:"about"};
  const cur=map[view];
  document.querySelectorAll("[data-nav]").forEach(a=>{ if(a.dataset.nav===cur) a.setAttribute("aria-current","page"); else a.removeAttribute("aria-current"); });
}
function afterRender(r){
  const live=$("#q-page");
  if(live){ live.focus({preventScroll:true}); const v=live.value; live.setSelectionRange(v.length,v.length); }
  if(r.view==="entry") watchParts();
}
let PART_OBS=null;
function watchParts(){
  if(PART_OBS) PART_OBS.disconnect();
  if(!("IntersectionObserver" in window)) return;
  PART_OBS=new IntersectionObserver(es=>{
    es.forEach(x=>{ if(x.isIntersecting){ const id=x.target.id;
      document.querySelectorAll("[data-part]").forEach(a=>a.classList.toggle("on",a.dataset.part===id));
      const chip=$('.chipbar [data-part="'+id+'"]'); if(chip&&chip.scrollIntoView&&window.innerWidth<1040){ const bar=chip.parentNode; bar.scrollTo({left:chip.offsetLeft-16,behavior:"smooth"}); } } });
  },{rootMargin:"-30% 0px -60% 0px"});
  document.querySelectorAll(".part").forEach(p=>PART_OBS.observe(p));
}

/* ---------- events (one delegated listener) ---------- */
window.addEventListener("hashchange",()=>{ render(); });
window.addEventListener("scroll",()=>{ if(LAST_KEY) SCROLL[LAST_KEY]=window.scrollY; },{passive:true});
document.addEventListener("click",ev=>{
  const a=ev.target.closest("a[href^='#/']");
  if(a){ if(LAST_KEY) SCROLL[LAST_KEY]=window.scrollY; FRESH=true; delete SCROLL[a.getAttribute("href")]; const vt=a.dataset.vt; PENDING_VT=vt!=null?vt:null; return; }
  const t=ev.target.closest("[data-try],[data-clear],[data-star],[data-share],[data-print],[data-copy],[data-where],[data-feel],[data-gstep],[data-greset],[data-setfilter],[data-jump],[data-part],[data-clearsaved],[data-theme-toggle],[data-openall]");
  if(!t) return;
  const d=t.dataset;
  if(d.try!==undefined){ SEARCH_Q=d.try; if(parse().view==="search"){ const i=$("#q-page"); i.value=SEARCH_Q; updateResults(); } else { FRESH=true; location.hash="#/search"; } return; }
  if(d.clear!==undefined){ const f=t.closest("form"), i=f.querySelector("input"); i.value=""; f.classList.remove("has"); if(i.id==="q-page"){SEARCH_Q="";updateResults();} i.focus(); return; }
  if(d.star!==undefined){ const on=toggleStar(d.star); t.setAttribute("aria-pressed",on); t.innerHTML=ic(on?"starOn":"star")+'<span>'+(on?"Saved":"Save")+'</span>'; toast(on?"Saved on this device":"Removed from saved"); return; }
  if(d.share!==undefined){ const url=location.href; if(navigator.share){ navigator.share({title:document.title,url}).catch(()=>{}); } else copyText(url,"Link copied"); return; }
  if(d.print!==undefined){ document.querySelectorAll("details.more").forEach(x=>x.open=true); window.print(); return; }
  if(d.copy!==undefined){ copyText($("#"+d.copy).textContent,"Copied"); return; }
  if(d.where!==undefined){ GUIDE.where=d.where||null; GUIDE.feels=[]; GUIDE.step=1; render(); return; }
  if(d.feel!==undefined){ const k=d.feel; GUIDE.feels=GUIDE.feels.includes(k)?GUIDE.feels.filter(x=>x!==k):GUIDE.feels.concat(k);
    t.setAttribute("aria-pressed",GUIDE.feels.includes(k)); const bar=$(".guide-bar"); if(bar){ bar.children[1].textContent=GUIDE.feels.length?GUIDE.feels.length+" picked":"Pick at least one"; bar.children[2].disabled=!GUIDE.feels.length; } return; }
  if(d.gstep!==undefined){ GUIDE.step=+d.gstep; render(); window.scrollTo(0,0); return; }
  if(d.greset!==undefined){ GUIDE={step:0,where:null,feels:[]}; render(); return; }
  if(d.setfilter!==undefined){ FILTER_SET=d.setfilter; const y=window.scrollY; render(); window.scrollTo(0,y); return; }
  if(d.jump!==undefined){ ev.preventDefault(); const el=document.getElementById(d.jump); if(el) el.scrollIntoView({behavior:matchMedia("(prefers-reduced-motion: reduce)").matches?"auto":"smooth"}); return; }
  if(d.part!==undefined){ ev.preventDefault(); const el=document.getElementById(d.part); if(el){ if(el.tagName==="DETAILS") el.open=true; el.scrollIntoView({behavior:matchMedia("(prefers-reduced-motion: reduce)").matches?"auto":"smooth"}); const h=el.querySelector("h2"); if(h){h.setAttribute("tabindex","-1");h.focus({preventScroll:true});} } return; }
  if(d.openall!==undefined){ const all=[...document.querySelectorAll("details.part")]; const open=!all.every(x=>x.open); all.forEach(x=>x.open=open); OPEN_PARTS=open; t.textContent=open?"Fold all":"Open all"; return; }
  if(d.clearsaved!==undefined){ if(confirm("Clear your saved and recent entries on this device?")){ store.set("starred",[]); store.set("trail",[]); render(); } return; }
  if(d.themeToggle!==undefined){ const cur=document.documentElement.getAttribute("data-theme")==="light"?"dark":"light"; document.documentElement.setAttribute("data-theme",cur); store.set("theme",cur); themeIcon(); return; }
});
document.addEventListener("submit",ev=>{
  const f=ev.target.closest("[data-search]"); if(!f) return; ev.preventDefault();
  const i=f.querySelector("input"); SEARCH_Q=i.value;
  if(parse().view!=="search"){ FRESH=true; location.hash="#/search"; } else { updateResults(); i.blur(); }
});
const updateResults=(()=>{let t; return ()=>{clearTimeout(t); t=setTimeout(()=>{ const r=$("#results"); if(r) r.innerHTML=resultsHTML(search(SEARCH_Q)); },120);};})();
document.addEventListener("input",ev=>{
  const i=ev.target;
  if(i.closest&&i.closest("[data-search]")){ i.closest("form").classList.toggle("has",!!i.value);
    if(i.id==="q-page"){ SEARCH_Q=i.value; updateResults(); }
    else if(i.id==="q-home"&&i.value.trim().length>=3){ SEARCH_Q=i.value; FRESH=true; location.hash="#/search"; }
  }
  if(i.id==="azf"){ AZ_Q=i.value; const l=$("#azlist"); if(l) l.innerHTML=azList(); }
});
document.addEventListener("keydown",ev=>{
  if(ev.key==="/"&&!/INPUT|TEXTAREA|SELECT/.test((document.activeElement||{}).tagName||"")&&!ev.metaKey&&!ev.ctrlKey){
    ev.preventDefault(); const h=$("#q-home")||$("#q-page"); if(h) h.focus(); else { FRESH=true; location.hash="#/search"; } }
});
function copyText(text,msg){
  const done=()=>toast(msg);
  const fallback=()=>{ try{ const ta=document.createElement("textarea"); ta.value=text; ta.style.position="fixed"; ta.style.opacity="0"; document.body.appendChild(ta); ta.select();
    const ok=document.execCommand("copy"); ta.remove(); toast(ok?msg:"Press and hold the text to copy it"); }catch(e){ toast("Press and hold the text to copy it"); } };
  if(navigator.clipboard&&navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(done).catch(fallback); else fallback();
}
let TOAST_T;
function toast(msg){ const t=$("#toast"); t.textContent=msg; t.classList.add("on"); clearTimeout(TOAST_T); TOAST_T=setTimeout(()=>t.classList.remove("on"),1800); }
function themeIcon(){ const b=$("[data-theme-toggle]"); if(!b) return; const light=document.documentElement.getAttribute("data-theme")==="light";
  b.innerHTML=ic(light?"moon":"sun"); b.setAttribute("aria-label",light?"Switch to the dark theme":"Switch to the light theme"); }
themeIcon();
render();
