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
  telescope:'<path d="m10.5 8.5 7-4 2 3.5-7 4z"/><path d="m8 11-3.5 2 1 1.7L9 12.7"/><path d="M12 14.5 9 21M12 14.5l3 6.5"/>',
  up:'<path d="m6 15 6-6 6 6"/>', down:'<path d="m6 9 6 6 6-6"/>', enter:'<path d="M20 5v7a3 3 0 0 1-3 3H5"/><path d="m9 11-4 4 4 4"/>',
  plus:'<path d="M12 5v14M5 12h14"/>', minus:'<path d="M5 12h14"/>', reset:'<path d="M3 12a9 9 0 1 0 3-6.7"/><path d="M3 4v5h5"/>', calm:'<path d="M4 12c3-5 5-5 8 0s5 5 8 0"/>',
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
/* Private reading keeps what you read, save and search in memory only: it is gone when the tab closes. */
const VOLATILE=new Set(["trail","starred"]);
const store=(()=>{let mem={},ok=false;
  try{localStorage.setItem("__t","1");localStorage.removeItem("__t");ok=true}catch(e){}
  let priv=false; try{priv=ok&&JSON.parse(localStorage.getItem("fg_private")||"false")===true}catch(e){}
  return{
    get private(){return priv},
    setPrivate(v){ priv=!!v; try{ if(ok){ localStorage.setItem("fg_private",JSON.stringify(priv)); if(priv) VOLATILE.forEach(k=>localStorage.removeItem("fg_"+k)); } }catch(e){} },
    get(k,d){if(priv&&VOLATILE.has(k)) return (k in mem)?mem[k]:d; try{if(ok){const v=localStorage.getItem("fg_"+k);if(v!==null){const p=JSON.parse(v);
      if(Array.isArray(d)&&!Array.isArray(p))return d; if(typeof d==="string"&&typeof p!=="string")return d; return p;}return d}}catch(e){}
      return (k in mem)?mem[k]:d},
    set(k,v){mem[k]=v; if(priv&&VOLATILE.has(k)) return; try{if(ok)localStorage.setItem("fg_"+k,JSON.stringify(v))}catch(e){ok=false}},
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
function toggleStar(n){let s=store.get("starred",[]); s=s.includes(n)?s.filter(x=>x!==n):[n].concat(s); store.set("starred",s); if(typeof Sky!=="undefined") refreshMarks(); return s.includes(n);}
function logTrail(n){let t=store.get("trail",[]).filter(x=>x.name!==n); t.unshift({name:n,ts:Date.now()}); store.set("trail",t.slice(0,200)); if(typeof Sky!=="undefined") refreshMarks();}
function refreshMarks(){ Sky.setMarks(store.get("trail",[]).map(t=>BY[t.name]&&BY[t.name].i).filter(x=>x!=null), store.get("starred",[]).map(n=>BY[n]&&BY[n].i).filter(x=>x!=null)); }

/* ---------- links ---------- */
const href = h => "#/"+h;
const entryHref = e => href("entry/"+e.s);
function rowHTML(e, opts){
  opts=opts||{};
  return '<a class="row" href="'+entryHref(e)+'" data-vt="'+e.i+'" data-i="'+e.i+'" style="--c:'+GROUP[e.g].c+'">'+
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
/* A few everyday words people use for the same thing, folded together so
   "reads my texts" meets "reads my messages". Small on purpose. */
const SAME={text:"messag",dm:"messag",chat:"messag",email:"messag",boyfriend:"partner",girlfriend:"partner",husband:"partner",wife:"partner",spouse:"partner",ex:"partner",
  boss:"manag",supervisor:"manag",mom:"parent",mum:"parent",dad:"parent",mother:"parent",father:"parent",cell:"phone",mobile:"phone",
  yell:"shout",scream:"shout",ignor:"silen",cash:"money",paycheck:"money",wage:"money"};
function stem(w){w=w.length>4?w.replace(/(ings|ing|edly|ed|ies|es|s|ly)$/,""):w.replace(/s$/,"");return SAME[w]||w;}
function stems(t){return new Set(t.split(" ").filter(Boolean).map(stem));}
const stemLine=t=>t.split(" ").filter(Boolean).map(stem).join(" ");
const STEMS = HAY.map(h=>({name:stems(h.name), words:stems(h.words), said:stems(h.said), all:stems(h.all), wline:stemLine(h.words), sline:stemLine(h.said)}));
function fuzzy(n){
  const toks=searchTokens(n).map(stem); if(!toks.length) return [];
  const w=n.split(" ").map(stem), grams=[];
  for(let i=0;i<w.length-1;i++){grams.push(w[i]+" "+w[i+1]); if(i<w.length-2) grams.push(w[i]+" "+w[i+1]+" "+w[i+2]);}
  const scored=[];
  E.forEach((e,i)=>{const h=HAY[i], st=STEMS[i]; let hits=0,score=0;
    toks.forEach(t=>{ if(!st.all.has(t)) return; hits++; score+= st.name.has(t)?4 : st.words.has(t)?3.5 : st.said.has(t)?3 : 1; });
    if(!hits) return;
    grams.forEach(g=>{ if(st.wline.includes(g)) score+=8; else if(st.sline.includes(g)) score+=6; });
    scored.push({e,hits,score});});
  const need=toks.length<=2?toks.length:Math.min(3,Math.ceil(toks.length/2));
  const kept=scored.filter(x=>x.hits>=need).sort((a,b)=>b.score-a.score||b.hits-a.hits||a.e.n.localeCompare(b.e.n));
  const top=kept.length?kept[0].score:0;
  return kept.filter(x=>x.score>=Math.max(2,top*.5)).slice(0,12).map(x=>x.e);
}
/* Ranking carried over from v9 (name > folded-in name > everyday words > what
   people say > the rest). When few entries contain the exact wording, close
   matches by shared words are added after them, never mixed in above. */
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
  const exact=list.length;
  if(exact<5&&n.split(" ").length>1){ const seen=new Set(list); fuzzy(n).forEach(e=>{ if(!seen.has(e)&&list.length<12) list.push(e); }); }
  return {list,fuzzy:!exact&&list.length>0,n};
}
/* Held in memory, never in the URL: what someone pastes here can be what was
   said to them, and it must not land in history, the address bar or autocomplete. */
let SEARCH_Q = "";
function searchBox(id,value,autofocus){
  return '<form class="search'+(value?' has':'')+'" role="search" data-search>'+
    '<span class="s-ic">'+ic("search")+'</span>'+
    '<label class="sr-only" for="'+id+'">Search the guide</label>'+
    '<input id="'+id+'" type="search" enterkeyhint="search" autocomplete="off" autocapitalize="off" spellcheck="false" value="'+esc(value||"")+'" placeholder="What happened, or a name"'+(autofocus?' autofocus':'')+'>'+
    '<button type="button" class="s-clear" data-clear aria-label="Clear search">'+ic("close")+'</button></form>';
}

//@@SKY@@
/* ---------- views ---------- */
function viewHome(){
  const trail=store.get("trail",[]);
  const last=trail[0]&&BY[trail[0].name];
  return '<section class="stage">'+
    '<div class="stage-copy">'+
      '<h1 class="stage-h">Put a name to what is happening.</h1>'+
      '<p class="lede">'+E.length+' manipulation and control tactics, explained in plain words: what each looks like, how to tell if it really fits, and what you can do.</p>'+
      '<button class="pill pill-xl" type="button" data-palette aria-haspopup="dialog">'+ic("search")+'<span class="pill-t">Search, or describe what happened</span><kbd class="kb" aria-hidden="true">⌘K</kbd></button>'+
      '<div class="tries"><span class="muted">Try</span>'+D.tries.map(t=>'<button class="chip" type="button" data-try="'+esc(t)+'">'+H(t)+'</button>').join("")+'</div>'+
      '<div class="ways-row">'+
        '<a class="btn primary" href="'+href("guide")+'">Help me figure it out</a>'+
        '<a class="btn" href="'+href("common")+'">The most common</a>'+
        '<a class="btn" href="'+href("sky")+'">Explore the sky</a>'+
      '</div>'+
      (last?'<p class="continue small">You were reading <a href="'+entryHref(last)+'" data-vt="'+last.i+'"><span data-vtn="'+last.i+'">'+H(last.n)+'</span></a></p>':'')+
    '</div>'+
    '<nav class="dock" aria-label="The ten constellations">'+D.groups.map(g=>'<a href="'+href("browse/"+g.k)+'" data-preview="'+g.k+'" style="--c:'+g.c+'"><i class="gd" aria-hidden="true"></i><span>'+H(g.short||g.label)+'</span></a>').join("")+'</nav>'+
    '<p class="privacy">'+ic("lock")+'Nothing you type leaves this device.</p>'+
  '</section>';
}
function way(route,icon,title,text,go){
  return '<a class="way" href="'+href(route)+'"><span class="w-ic">'+ic(icon)+'</span><span><h2>'+title+'</h2><p>'+text+'</p></span><span class="go">'+go+'</span></a>';
}
function groupTiles(lv){ lv=lv||3;
  return '<div class="groups">'+D.groups.map(g=>{
    const list=IN_GROUP[g.k];
    return '<a class="group" href="'+href("browse/"+g.k)+'" data-preview="'+g.k+'" style="--c:'+g.c+'"><h'+lv+' class="gt"><i class="gd" aria-hidden="true"></i>'+H(g.label)+'</h'+lv+'><p>'+H(g.blurb)+'</p><span class="n">'+list.length+' tactics</span></a>';
  }).join("")+'</div>';
}
function viewSearch(){
  const r=search(SEARCH_Q);
  return '<div class="sky-window" aria-hidden="true"></div><p class="eyebrow"><a href="'+href("")+'">Home</a></p><h1 class="h1">Search</h1>'+
    '<div style="margin-top:24px">'+searchBox("q-page",SEARCH_Q,true)+'</div>'+
    '<p class="sr-only" id="rcount" aria-live="polite"></p><div id="results">'+resultsHTML(r)+'</div>';
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
    '<div style="margin-top:40px">'+groupTiles(2)+'</div>'+
    '<section class="sect"><div class="sect-head"><div><h2 class="h2">Or by where it happens</h2></div></div><div class="chips">'+
    D.settings.map(s=>'<a class="chip" href="'+href("where/"+s.k)+'">'+H(s.label)+'</a>').join("")+'</div></section>';
}
let FILTER_SET = "";
function groupTrack(cur){
  return '<nav class="track" aria-label="Constellations"><span class="ind" aria-hidden="true"></span>'+D.groups.map(g=>'<a href="'+href("browse/"+g.k)+'" data-track="'+g.k+'" style="--c:'+g.c+'"'+(g.k===cur?' class="on" aria-current="page"':'')+'><i class="gd" aria-hidden="true"></i><span>'+H(g.label)+'</span><span class="n">'+IN_GROUP[g.k].length+'</span></a>').join("")+'</nav>';
}
function tacticTile(e,big){
  return '<a class="tile tac'+(big?' s3 big':' s2')+'" href="'+entryHref(e)+'" data-vt="'+e.i+'" data-i="'+e.i+'" style="--c:'+GROUP[e.g].c+'">'+
    '<span class="nm"><span data-vtn="'+e.i+'">'+H(e.n)+'</span>'+(e.sens?'<span class="dot-safe" title="Safety-sensitive">'+ic("shield")+'<span class="sr-only">Safety-sensitive</span></span>':'')+'</span>'+
    (e.sub?'<span class="sub">'+H(e.sub)+'</span>':'')+'<span class="df">'+H(e.f.short_definition)+'</span><span class="go" aria-hidden="true">'+ic("chevron")+'</span></a>';
}
function viewGroup(k){
  const g=GROUP[k]; if(!g) return notFound();
  const all=IN_GROUP[k];
  const counts=D.settings.map(s=>({s,n:all.filter(e=>(e.w||[]).includes(s.k)).length})).filter(x=>x.n);
  const list=FILTER_SET?all.filter(e=>(e.w||[]).includes(FILTER_SET)):all;
  const top=new Set([...list].sort((a,b)=>(b.pop||0)-(a.pop||0)).slice(0,2).map(e=>e.n));
  const ordered=list.filter(e=>top.has(e.n)).concat(list.filter(e=>!top.has(e.n)));
  return '<div class="split">'+
    '<aside class="pane-l"><div class="sky-window" aria-hidden="true"></div>'+
      '<p class="eyebrow"><a href="'+href("browse")+'">Browse</a></p><h1 class="h1">'+H(g.label)+'</h1><p class="lede">'+H(g.blurb)+'</p>'+
      groupTrack(k)+
    '</aside>'+
    '<section class="pane-r scroll" aria-label="Tactics in '+esc(g.label)+'">'+
      '<div class="chips filter" role="group" aria-label="Where it happens">'+
        '<button class="chip" type="button" data-setfilter="" aria-pressed="'+(!FILTER_SET)+'">Everywhere <span class="n">'+all.length+'</span></button>'+
        counts.map(x=>'<button class="chip" type="button" data-setfilter="'+x.s.k+'" aria-pressed="'+(FILTER_SET===x.s.k)+'">'+H(x.s.label)+' <span class="n">'+x.n+'</span></button>').join("")+
      '</div><p class="count">'+list.length+' tactics'+(FILTER_SET?' in '+H(SET[FILTER_SET].label.toLowerCase()):'')+', most common first</p>'+
      '<div class="bento">'+ordered.map((e,i)=>tacticTile(e,i<2)).join("")+'</div>'+foot()+
    '</section></div>';
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
const PARTS = [["short","In short"],["understand","Understand it"],["fit","Is this it?"],["do","What you can do"],["deeper","Go deeper"]];
/* Scannable prose: the first sentence (the answer) is set in bold, and long
   paragraphs are broken into fragments of two sentences. */
function sentences(t){ const m=String(t||"").match(/[^.!?]+(?:[.!?]+["”’)]*|$)\s*/g); return (m||[String(t||"")]).map(x=>x.trim()).filter(Boolean); }
function prose(t){
  const ss=sentences(t); if(!ss.length) return "";
  let out='<p><strong>'+H(ss[0])+'</strong>'+(ss[1]?' '+H(ss[1]):'')+'</p>';
  for(let i=2;i<ss.length;i+=2) out+='<p>'+H(ss[i])+(ss[i+1]?' '+H(ss[i+1]):'')+'</p>';
  return out;
}
/* In a list, the lead phrase of each point is what you scan for: bold it. */
function leadLi(t){
  t=String(t||""); const m=t.match(/^(.{6,64}?)(\s[—–-]\s|:\s|,\s)/);
  return m?'<strong>'+H(m[1])+'</strong>'+H(m[2]+t.slice(m[0].length)):H(t);
}
function bl(items,cls){ return items&&items.length?'<ul'+(cls?' class="'+cls+'"':'')+'>'+items.map(x=>'<li>'+leadLi(x)+'</li>').join("")+'</ul>':""; }
function tile(title,inner,span,cls){ return inner?'<article class="tile s'+span+(cls?' '+cls:'')+'">'+(title?'<h3>'+title+'</h3>':'')+inner+'</article>':""; }
function sec(id,title,hint,tiles){ return '<section class="sec part" id="'+id+'" aria-labelledby="h-'+id+'"><header class="sec-h"><h2 class="h2" id="h-'+id+'" data-reveal>'+title+'</h2>'+(hint?'<p>'+hint+'</p>':'')+'</header><div class="bento">'+tiles+'</div></section>'; }
/* The first use of each glossary term on an entry page becomes a button that
   opens a one-line plain explanation right under it. */
function gloss(html){
  const used=new Set();
  return html.replace(/<(p|li)>([\s\S]*?)<\/\1>/g,(m,tag,inner)=>{ const orig=inner;
    let defs="";
    Object.keys(D.glossary).forEach(t=>{
      if(used.has(t)) return;
      const re=new RegExp("\\b("+t.replace(/ /g,"\\s")+"s?)\\b","i");
      if(re.test(inner.replace(/<[^>]+>/g," "))&&re.test(inner)&&!/<(button|a) /.test(orig)){
        used.add(t);
        const id="g-"+t.replace(/ /g,"-");
        inner=inner.replace(re,'<button type="button" class="term" data-term="'+id+'" aria-expanded="false" aria-controls="'+id+'">$1</button>');
        defs+='<span class="term-def" id="'+id+'" hidden><b>'+t.charAt(0).toUpperCase()+t.slice(1)+':</b> '+esc(D.glossary[t])+'</span>';
      }
    });
    return "<"+tag+">"+inner+defs+"</"+tag+">";
  });
}
function viewEntry(slug){
  let e=BY_SLUG[slug];
  if(!e&&ALIAS_SLUG[slug]){ e=BY[ALIAS_SLUG[slug]]; try{history.replaceState(null,"",entryHref(e))}catch(x){} }
  if(!e) return notFound();
  logTrail(e.n);
  const f=e.f, g=GROUP[e.g], starred=isStarred(e.n);
  const inG=IN_GROUP[e.g], gi=inG.indexOf(e);
  const prev=inG[(gi-1+inG.length)%inG.length], next=inG[(gi+1)%inG.length];
  const says=(f.what_it_sounds_like||[]);
  const pats=(PATS_OF[e.n]||[]).map(ri=>D.recipes[ri]);
  const notIt=(f.this_may_not_be_it_when||[]);
  const left='<aside class="pane-l"><div class="sky-window" aria-hidden="true"></div>'+
      '<p class="eyebrow"><a href="'+href("browse")+'">Browse</a> <span aria-hidden="true">/</span> <a href="'+href("browse/"+g.k)+'">'+H(g.label)+'</a></p>'+
      '<h1 class="h1" data-vtn="'+e.i+'">'+H(e.n)+'</h1>'+
      (e.sub?'<p class="e-sub">'+H(e.sub)+'</p>':'')+
      '<div class="e-meta"><span class="pager" role="group" aria-label="Position in '+esc(g.label)+'"><a class="pg" href="'+entryHref(prev)+'" data-pg="prev" aria-label="Previous in '+esc(g.label)+': '+esc(prev.n)+'">'+ic("up")+'</a><span class="pos"><b>'+(gi+1)+'</b> / '+inG.length+'</span><a class="pg" href="'+entryHref(next)+'" data-pg="next" aria-label="Next in '+esc(g.label)+': '+esc(next.n)+'">'+ic("down")+'</a><span class="kb-hint" aria-hidden="true"><kbd>J</kbd><kbd>K</kbd></span></span>'+
        (e.sens?'<span class="badge safety">'+ic("shield")+'Safety-sensitive</span>':'')+'</div>'+
      '<div class="e-actions">'+
        '<button class="btn" type="button" data-star="'+esc(e.n)+'" aria-pressed="'+starred+'">'+ic(starred?"starOn":"star")+'<span>'+(starred?"Saved":"Save")+'</span></button>'+
        '<button class="btn" type="button" data-share>'+ic("share")+'<span>Share link</span></button>'+
        '<button class="btn" type="button" data-print>'+ic("print")+'<span>Print</span></button>'+
      '</div>'+
      '<nav class="track parts" aria-label="On this page"><span class="ind" aria-hidden="true"></span>'+PARTS.map((p,n)=>'<a href="#'+p[0]+'" data-part="'+p[0]+'"><span class="tn">0'+(n+1)+'</span><span>'+p[1]+'</span></a>').join("")+'</nav>'+
    '</aside>';
  const right='<section class="pane-r scroll" aria-label="'+esc(e.n)+'">'+
    '<nav class="chipbar" aria-label="Jump to a part">'+PARTS.map(p=>'<a class="chip" href="#'+p[0]+'" data-part="'+p[0]+'">'+p[1]+'</a>').join("")+'</nav>'+
    sec("short","In short",(e.abs&&e.abs.length?'Also called '+e.abs.map(H).join(", "):''),
      tile("",'<p class="sum">'+H(f.plain_language_summary)+'</p>',6,"hero")+
      (e.sens?'<article class="tile s6 safe" role="note"><h3>'+ic("shield")+'Your safety comes first</h3>'+prose(f.safety_note)+'<p class="small"><a href="'+href("about")+'">How to use this guide safely</a></p></article>':'')+
      tile("It can sound like",says.length?'<ul class="says">'+says.slice(0,3).map(x=>'<li>'+H(x)+'</li>').join("")+'</ul>':'',notIt.length?4:6,"quote")+
      tile("It may be something else if",bl(notIt.slice(0,2),"away"),2,"")
    )+
    sec("understand","Understand it","What it is, why it matters, and how it shows up",
      tile("What it is",'<div class="text">'+prose(f.expanded_definition)+'</div>',4,"tall")+
      tile("Why it matters",'<div class="text">'+prose(f.why_this_matters)+'</div>',2,"")+
      tile("How it shows up",bl(f.what_it_is),says.length>3?3:6,"")+
      (says.length>3?tile("More things people say",'<ul class="says">'+says.slice(3).map(x=>'<li>'+H(x)+'</li>').join("")+'</ul>',3,"quote"):"")
    )+
    sec("fit","Is this it?","One moment proves very little. Weigh it honestly, in both directions.",
      tile("Signs it might be this",bl(f.this_may_be_it_when),3,"tw")+
      tile("Signs it is probably something else",bl(notIt.slice(2).concat(f.less_concerning_if||[])),3,"aw")+
      tile("Questions to ask yourself",bl(f.discernment_questions,"qs"),2,"tall")+
      tile("More worrying if",bl(f.more_concerning_if),2,"")+
      tile("What shows up over time",bl(f.pattern_over_time_signs),2,"")+
      tile("What it is not",bl(f.what_it_is_not),3,"")+
      tile("Ordinary explanations",bl(f.innocent_or_ordinary_possibilities),3,"")+
      tile("Often mistaken for this",bl(f.common_false_positives),6,"")
    )+
    sec("do","What you can do",e.sens?'Read the safety note first. If speaking up could make things worse, skip the wording below and talk to someone you trust or a local support service.':'Pick what fits. You do not owe anyone a confrontation.',
      '<article class="tile s4 script"><h3>'+({verify:"A check to run before you share or act",self:"Words to say to yourself",say:"Words you could use"}[e.kind])+'</h3><blockquote id="bs">'+H(f.boundary_script.replace(/^Verification script[^:]*:\s*/i,""))+'</blockquote><div class="row-act"><button class="btn" type="button" data-copy="bs">'+ic("copy")+'<span>Copy</span></button></div></article>'+
      tile("Is it changing?",'<div class="text">'+prose(f.boundary_respect_check)+prose(f.repair_check)+'</div>',2,"")+
      tile("Ways to respond",'<div class="resp">'+RESP.map(r=>f.response_options&&f.response_options[r[0]]?'<div><h4>'+r[1]+'</h4><p>'+H(f.response_options[r[0]])+'</p></div>':'').join("")+'</div>',6,"")+
      (!e.sens?tile("When to take it more seriously",'<div class="text">'+prose(f.safety_note)+'</div>',6,"note"):"")
    )+
    sec("deeper","Go deeper","How it works, its effects, and its close relatives",
      tile("How it works",'<div class="text">'+prose(f.psychological_mechanism)+'</div>',3,"")+
      tile("How it can affect you",'<div class="text">'+prose(f.possible_impact_on_receiver)+'</div>',3,"")+
      tile("Telling it apart from its neighbours",'<div class="text">'+prose(f.how_to_distinguish_from_related)+'</div>'+(e.rel&&e.rel.length?'<div class="related">'+e.rel.map(n=>BY[n]?'<a class="chip" href="'+entryHref(BY[n])+'" style="--c:'+GROUP[BY[n].g].c+'"><i class="gd" aria-hidden="true"></i>'+H(n)+'</a>':'').join("")+'</div>':''),4,"")+
      tile("Using this label fairly",bl(f.misuse_warning),2,"")+
      (pats.length?tile("Patterns it is part of",'<div class="pats">'+pats.slice(0,6).map(r=>'<a href="'+href("patterns/"+slugify(r.n))+'"><b>'+H(r.n)+'</b><span>'+r.c.length+' tactics in sequence</span></a>').join("")+'</div>',6,""):"")
    )+
    '<nav class="pn" aria-label="More in '+esc(g.label)+'">'+
      '<a class="tile" href="'+entryHref(prev)+'" data-vt="'+prev.i+'"><span class="k">Previous in '+H(g.label)+'</span><span class="t" data-vtn="'+prev.i+'">'+H(prev.n)+'</span></a>'+
      '<a class="tile nx" href="'+entryHref(next)+'" data-vt="'+next.i+'"><span class="k">Next</span><span class="t" data-vtn="'+next.i+'">'+H(next.n)+'</span></a>'+
    '</nav>'+foot()+
  '</section>';
  return gloss('<div class="split entry">'+left+right+'</div>');
}
function foot(){
  return '<footer class="foot"><p>A free guide by Noble Father Creations. It is a reading aid, not a diagnosis, a legal opinion or therapy. If you are in danger, contact emergency services.</p>'+
    '<p class="foot-links"><a href="'+href("about")+'">Use this safely</a><a href="'+href("all")+'">A–Z</a><a href="'+href("patterns")+'">How tactics combine</a><a href="'+href("saved")+'">Saved and recent</a><a href="'+href("about")+'#updates">What changed</a></p></footer>';
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
    return '<div class="sky-window" aria-hidden="true"></div><p class="eyebrow"><a href="'+href("patterns")+'">How tactics combine</a></p><h1 class="h1">'+H(r.n)+'</h1><p class="lede">'+H(r.d)+'</p>'+
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
    '<div class="callout" style="margin-top:32px"><h2 class="ch">'+ic("shield")+'If you are not safe</h2><p>If any of this involves threats, being watched or tracked, being cut off from people or money, housing or immigration status, sex, pressure toward self-harm, or fear for your safety, reach a real person: someone you trust, a local support service, a legal or workplace resource, or emergency services if you are in immediate danger. Entries marked Safety-sensitive say more about what to watch for.</p></div>'+
    h("What this guide is")+p("A reading aid. It helps you put a name to something that happened, see what else it could be, and decide what to do next. Some entries are about everyday relationships; others are about workplaces, online life, and influence on a whole society.")+
    h("What it is not")+p("It is not a diagnosis, a legal opinion, or therapy. It cannot tell you what another person meant, what they are like, or whether you are in danger. Only you, and the people you trust, can weigh that.")+
    h("A signal, not a verdict")+p("One example of a pattern is a reason to look more closely, not proof of motive or character. Every entry says what its tactic is not, because most of these behaviors also have ordinary explanations. Please do not use a label from this guide to attack, shame, threaten, expose or get back at someone.")+
    h("The search box")+p("Pasting in something that was said to you finds entries whose wording is close to it. That is a pointer to read further, never a finding. It cannot see the tone, the history, or whether the words were meant seriously. What you type is never added to the address bar or your history.")+
    h("Your privacy")+p("There is no account. Your saved and recent entries stay on this device. The page counts anonymous visits, and nothing you type, paste or save is sent anywhere.")+
    p("If someone else uses this device, turn on Private. Then what you read, save and search is kept only until you close the tab, and anything saved earlier is removed from this device.")+
    '<div class="chips" style="margin:8px 0 12px"><button class="btn" type="button" data-private aria-pressed="'+store.private+'">'+(store.private?"Private reading is on":"Turn on private reading")+'</button>'+
    (store.get("breath",true)===false?'<button class="btn ghost" type="button" data-breath="on">Turn reading pauses back on</button>':'')+'</div>'+
    h("Taking a pause")+p("After about twenty minutes of steady reading, the guide dims and suggests a short pause. You can keep reading straight away, or switch the reminder off.")+
    '<h2 class="h2" id="updates" style="margin:48px 0 16px">What changed</h2>'+'<p class="small muted">'+esc(D.version)+'</p><ul class="updates">'+D.updates.map(u=>'<li>'+u+'</li>').join("")+'</ul>'+
  '</div>';
}

/* ---------- the sky: an explorable map of every tactic ---------- */
let SKY_PICK=-1;
function viewSky(){
  return '<div class="sky-ui">'+
    '<div class="sky-top"><h1 class="sky-h">The sky</h1><p class="small muted">Every tactic is a star. Drag to move, pinch or scroll to zoom, tap a star to read about it.</p></div>'+
    '<div class="sky-groups" role="group" aria-label="Fly to a constellation">'+D.groups.map(g=>'<button class="chip" type="button" data-skygroup="'+g.k+'" style="--c:'+g.c+'"><i class="gd" aria-hidden="true"></i>'+H(g.label)+'</button>').join("")+'</div>'+
    '<div class="sky-tools" role="group" aria-label="Zoom"><button class="icon-btn solid" type="button" data-zoom="1" aria-label="Zoom in">'+ic("plus")+'</button><button class="icon-btn solid" type="button" data-zoom="-1" aria-label="Zoom out">'+ic("minus")+'</button><button class="icon-btn solid" type="button" data-zoom="0" aria-label="Show everything">'+ic("reset")+'</button></div>'+
    '<aside class="sheet" id="sheet" hidden aria-live="polite"></aside>'+
    '<p class="sr-only">This map is visual. To browse the same tactics as lists, use Browse or A to Z.</p>'+
  '</div>';
}
function sheetHTML(i){
  const e=E[i]; const g=GROUP[e.g];
  return '<button class="sheet-x" type="button" data-sheetclose aria-label="Close">'+ic("close")+'</button>'+
    '<p class="eyebrow" style="color:'+g.c+'">'+H(g.label)+'</p><h2 class="sheet-t" data-vtn="'+e.i+'">'+H(e.n)+'</h2>'+(e.sub?'<p class="e-sub" style="font-size:17px;margin:4px 0 0">'+H(e.sub)+'</p>':'')+
    '<p class="sheet-s">'+H(e.f.plain_language_summary)+'</p>'+
    (e.sens?'<p class="small" style="color:var(--ember);margin:0 0 12px">'+ic("shield")+' Safety-sensitive</p>':'')+
    '<div class="chips"><a class="btn primary" href="'+entryHref(e)+'" data-vt="'+e.i+'">Read this entry</a>'+(e.rel&&e.rel.length?'<button class="btn" type="button" data-skylink="'+i+'">Show its neighbours</button>':'')+'</div>';
}
function pickStar(i){
  const sh=$("#sheet"); if(!sh) return;
  SKY_PICK=i;
  if(i<0){ sh.hidden=true; Sky.set({ring:-1,link:false,focus:null}); Sky.lit([]); return; }
  sh.innerHTML=sheetHTML(i); sh.hidden=false; fitText(sh.querySelector(".sheet-t"));
  Sky.set({ring:i,link:false,focus:null}); Sky.lit([]);
  const k=Math.max(Sky.cam.k,Sky.fitK()*2.6), st=Sky.st; 
  Sky.flyTo(Sky.stars[i].x,Sky.stars[i].y,k,700,0,innerWidth<700?-innerHeight*.18:0);
}
function notFound(){
  return '<h1 class="sr-only">Page not found</h1><div class="empty" style="margin-top:40px"><p><strong>That page is not here.</strong></p><p class="small muted">The link may be out of date or cut short.</p><div class="chips" style="justify-content:center"><a class="btn primary" href="'+href("")+'">Go home</a><a class="btn" href="'+href("search")+'">Search</a></div></div>';
}

/* ---------- router ---------- */
function parse(){
  const raw=(location.hash||"").replace(/^#\/?/,"");
  const parts=raw.split("/").map(safeDecode);
  return {view:parts[0]||"", arg:parts.slice(1).join("/")};
}
/* Old v9 routes keep working. */
const LEGACY={core:"common",trail:"saved",narrow:"guide",index:"all",constellation:"browse",category:"browse",feeling:"guide"};
const ROUTES={"":viewHome,sky:viewSky,search:viewSearch,browse:a=>a?viewGroup(a):viewBrowse(),where:viewWhere,common:viewCommon,all:viewAll,
  entry:viewEntry,guide:viewGuide,patterns:viewPatterns,saved:viewSaved,about:viewAbout};
const SCROLL = {};

/* ---------- where the camera goes on each page ---------- */
let HOME_SCROLL=false, ROUTE_G=null, ROUTE_DIM=1, WIN_OY=null;
function skyRoute(r,first){
  const phone=innerWidth<760, fk=Sky.fitK(), S=Sky.S;
  const fly=(x,y,k,ms,ox,oy)=>Sky.flyTo(x,y,k,first?0:ms,ox||0,oy||0);
  Sky.st.interactive=false; Sky.st.chain=null; Sky.set({ring:-1,link:false,focus:null,groupFocus:null,labels:false,names:false,hover:-1,hoverable:r.view==="",magnet:r.view===""||r.view==="sky"});
  Sky.lit([]); HOME_SCROLL=false; document.body.dataset.sky=r.view;
  const rg=r.view==="browse"&&GROUP[r.arg]?r.arg:(r.view==="entry"?((BY_SLUG[r.arg]||BY[ALIAS_SLUG[r.arg]]||{}).g):null);
  ROUTE_G=rg||null; if(rg){ document.body.style.setProperty("--g",GROUP[rg].c); document.body.dataset.g=rg; } else { document.body.style.removeProperty("--g"); delete document.body.dataset.g; }
  document.querySelectorAll("#rail a").forEach(a=>{ if(a.dataset.rail===rg) a.setAttribute("aria-current","true"); else a.removeAttribute("aria-current"); });
  const win=(()=>{const w=$(".sky-window"); if(!w) return null; const b=w.getBoundingClientRect(); return {ox:b.left+b.width/2-innerWidth/2,oy:b.top+scrollY+b.height/2-innerHeight/2,h:b.height,w:b.width,bottom:b.bottom+scrollY};})();
  let dim=.28;
  if(r.view===""){
    Sky.set({names:false}); dim=1; HOME_SCROLL=true; storySetup(); { const cp=$(".stage-copy"); if(cp&&STORY){ const b=cp.getBoundingClientRect(); STORY.avoid={x0:b.left-20,x1:b.right+20,y0:b.top-20,y1:b.bottom+20}; } }
    fly(S.w/2,S.h/2,fk*(phone?1.0:.95),1400,0,0);
  }else if(r.view==="sky"){
    Sky.st.interactive=true; Sky.set({names:true,labels:false}); dim=1;
    fly(S.w/2,S.h/2,fk,1100,0,phone?40:0);
  }else if(r.view==="browse"&&r.arg&&GROUP[r.arg]&&win){
    const G=S.groups[r.arg];
    Sky.set({groupFocus:r.arg,labels:true,names:true}); dim=1;
    fly(G.x,G.y,Math.min(win.h*.46/G.r,win.w*.4/G.r),1200,win.ox,win.oy);
  }else if(r.view==="entry"&&win){
    const e=BY_SLUG[r.arg]||BY[ALIAS_SLUG[r.arg]]; if(e){
      const set=[e.i].concat((e.rel||[]).map(n=>BY[n]&&BY[n].i).filter(x=>x!=null));
      let RX=60,RY=60; set.forEach(i=>{RX=Math.max(RX,Math.abs(Sky.stars[i].x-Sky.stars[e.i].x));RY=Math.max(RY,Math.abs(Sky.stars[i].y-Sky.stars[e.i].y));});
      const k=Math.min(win.h*.38/RY,win.w*(phone?.36:.3)/RX,fk*7);
      Sky.set({ring:e.i,link:true,focus:set,labels:true}); dim=1;
      fly(Sky.stars[e.i].x,Sky.stars[e.i].y,Math.max(k,fk*1.2),1300,win.ox,win.oy);
    }
  }else if(r.view==="patterns"&&r.arg&&win){
    const rc=Sky.S.seq[D.recipes.findIndex(x=>slugify(x.n)===r.arg)];
    if(rc&&rc.length){ Sky.st.chain=rc; Sky.lit(rc,true); dim=1;
      let x0=1e9,x1=-1e9,y0=1e9,y1=-1e9; rc.forEach(i=>{const p=Sky.stars[i];x0=Math.min(x0,p.x);x1=Math.max(x1,p.x);y0=Math.min(y0,p.y);y1=Math.max(y1,p.y);});
      const k=Math.min(win.w*.8/Math.max(160,x1-x0),win.h*.7/Math.max(160,y1-y0));
      fly((x0+x1)/2,(y0+y1)/2,Math.max(fk*.28,Math.min(k,fk*4)),1200,win.ox,win.oy); }
  }else if(r.view==="search"&&win){
    dim=1; Sky.set({names:false}); fly(S.w/2,S.h/2,Math.max(fk*.55,Math.min(win.w/S.w,win.h*1.9/S.h)),1000,0,win.oy);
  }else{
    fly(S.w/2,S.h/2,fk*(phone?1.1:1),1000,0,0); dim=.24;
  }
  const cp=$(".stage-copy")||$(".sky-top"); if(cp){ const b=cp.getBoundingClientRect(); Sky.set({avoid:{x0:b.left-20,x1:b.right+20,y0:b.top-20,y1:b.bottom+20}}); } else Sky.set({avoid:null});
  if(!first&&typeof Sky.ripple==="function"){ const focusStar=r.view==="entry"?(BY_SLUG[r.arg]||BY[ALIAS_SLUG[r.arg]]||{}).i:null; const G=r.view==="browse"&&GROUP[r.arg]?S.groups[r.arg]:null;
    if(focusStar!=null) Sky.ripple(Sky.stars[focusStar].x,Sky.stars[focusStar].y); else if(G) Sky.ripple(G.x,G.y); else if(r.view===""||r.view==="sky") Sky.ripple(S.w/2,S.h/2); }
  ROUTE_DIM=dim; WIN_OY=win?win.oy:null; Sky.set({dim,clipY:win?win.bottom:null}); cvPointer(r.view==="sky"||r.view==="");
  if(r.view===""){ if(STORY) STORY.step=-2; storyUpdate(); }
}
function cvPointer(on){ const c=$("#sky"), sky=parse().view==="sky"; c.style.pointerEvents=on?"auto":"none"; c.style.cursor=sky?"grab":"default"; c.tabIndex=sky?0:-1; }
function winScroll(){ const w=$(".sky-window"); if(!w||!Sky.st.clipY&&Sky.st.clipY!==0) return; Sky.set({clipY:w.getBoundingClientRect().bottom}); }
let STORY=null;
function storySetup(){ const el=$(".story"); STORY=el?{el,n:+el.dataset.n,step:-2}:null; }
function headerState(){ const t=$(".top"); if(t) t.classList.toggle("solid",scrollTop()>12||scrollY>12); }
function storyUpdate(){
  if(!STORY||!HOME_SCROLL) return;
  const calm=Sky.calm||matchMedia("(prefers-reduced-motion: reduce)").matches;
  const r=STORY.el.getBoundingClientRect(), total=Math.max(1,r.height-innerHeight);
  const phone=innerWidth<760, fk=Sky.fitK(), S=Sky.S;
  let step=r.top>innerHeight*.45?-1:(r.bottom<innerHeight*.6?STORY.n:Math.min(STORY.n-1,Math.max(0,Math.floor(Math.max(0,-r.top)/total*STORY.n))));
  if(step===STORY.step) return; STORY.step=step; Sky.set({avoid:step<0?STORY.avoid:(step===1?{x0:0,x1:innerWidth,y0:innerHeight*.34,y1:innerHeight*.68}:null)});
  document.querySelectorAll(".beat").forEach(b=>b.classList.toggle("on",+b.dataset.beat===step));
  document.querySelectorAll(".story-dots i").forEach((d,i)=>d.classList.toggle("on",i===step));
  if(calm) return;
  const groups=["truth","hook","people"], gi=step-2;
  const wide=(names,dim)=>{ Sky.set({groupFocus:null,names,labels:false,dim}); Sky.flyTo(S.w/2,S.h/2,fk*(phone?1.0:.95),1300,0,0); };
  if(step<=0) wide(false,1);
  else if(step===1) wide(true,1);
  else if(gi>=0&&gi<groups.length){ const G=S.groups[groups[gi]]; Sky.set({groupFocus:groups[gi],names:true,labels:false,dim:1});
    Sky.flyTo(G.x,G.y,Math.min(innerWidth,innerHeight)*(phone?.36:.3)/G.r,1400,0,phone?-innerHeight*.08:0); }
  else if(step===STORY.n-1) wide(false,.9);
  else wide(false,.26);
}
addEventListener("resize",debounce(fitAll,150));
addEventListener("scroll",()=>{ headerState(); if(HOME_SCROLL) requestAnimationFrame(storyUpdate); else if(Sky.st.clipY!=null) requestAnimationFrame(winScroll); },{passive:true});
let INTRO_PLAYED=false, MOVED_FOCUS = false, FRESH = false, LAST_KEY = null, PENDING_VT = null;
function key(){return location.hash||"#/";}
/* On wide screens the guide is one locked viewport and the reading pane scrolls by itself;
   on a phone the page scrolls as usual. Everything that reads or sets a scroll position asks here. */
function scroller(){ const sc=document.querySelector("#main .scroll"); return sc&&/(auto|scroll)/.test(getComputedStyle(sc).overflowY)?sc:(document.scrollingElement||document.documentElement); }
function scrollTop(v){ const sc=scroller(); if(v==null) return sc.scrollTop; sc.scrollTop=v; }
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
    const full=/^<(div class="split|section class="stage|div class="sky-ui)/.test(html);
    main.innerHTML=full?'<div class="view full">'+html+'</div>':'<div class="view sheet"><div class="panel scroll"><div class="wrap">'+html+'</div>'+foot()+'</div></div>';
    setNav(r.view);
    document.title=titleFor(r);
    const k=key();
    window.scrollTo(0,0);
    if(!FRESH&&SCROLL[k]!=null) scrollTop(SCROLL[k]); else scrollTop(0);
    FRESH=false; LAST_KEY=k;
    afterRender(r); skyRoute(r,LAST_KEY===null&&!INTRO_PLAYED);
    INTRO_PLAYED=true;
  };
  const vt=PENDING_VT; PENDING_VT=null;
  if(!INTRO_PLAYED||!document.startViewTransition||!motionOn()){ go(); splitHeads(); return; }
  if(vt!=null){ const src=document.querySelector('#main [data-vtn="'+vt+'"]'); if(src) src.style.viewTransitionName="title"; }
  document.documentElement.classList.toggle("vt-title",vt!=null);
  let t; try{ t=document.startViewTransition(()=>{ go(); if(vt!=null){ const h=document.querySelector('#main h1[data-vtn="'+vt+'"]'); if(h) h.style.viewTransitionName="title"; } splitHeads(vt!=null); }); }catch(e){ go(); splitHeads(); return; }
  t.finished.finally(()=>{ document.querySelectorAll('[style*="view-transition-name"]').forEach(x=>x.style.viewTransitionName=""); document.documentElement.classList.remove("vt-title"); });
}
function motionOn(){ return !Sky.calm&&!matchMedia("(prefers-reduced-motion: reduce)").matches; }
/* Headlines rise into place word by word, each behind its own mask. */
function splitHeads(skipTitle){
  document.querySelectorAll("#main .h1,#main .stage-h,#main .sky-h,#main [data-reveal]").forEach(el=>{
    if(el.dataset.split||el.children.length) return; el.dataset.split="1";
    if(skipTitle&&el.dataset.vtn!=null){ el.classList.add("in"); return; }
    const words=el.textContent.trim().split(/\s+/);
    el.setAttribute("aria-label",el.textContent.trim());
    el.innerHTML=words.map(w=>'<span class="wd" aria-hidden="true"><span>'+esc(w)+'</span></span>').join(" ");
  });
  fitAll();
  /* one delay per line, not per word: each line rises as a single strip of glass */
  document.querySelectorAll("#main [data-split]").forEach(el=>{ let top=null, line=-1;
    el.querySelectorAll(".wd").forEach(w=>{ const t=w.offsetTop; if(top===null||Math.abs(t-top)>4){ top=t; line++; } w.firstChild.style.setProperty("--i",line); });
    if(!el.hasAttribute("data-reveal")) el.classList.add("in"); });
}
function titleFor(r){
  const base="The Pattern Decoder";
  if(r.view==="entry"){const e=BY_SLUG[r.arg]||BY[ALIAS_SLUG[r.arg]]; return e?curly(e.n)+" — "+base:base;}
  if(r.view==="browse"&&r.arg&&GROUP[r.arg]) return GROUP[r.arg].label+" — "+base;
  const t={sky:"The sky",search:"Search",browse:"Browse",where:"Where it happens",common:"The most common",all:"A–Z",guide:"Help me figure it out",patterns:"How tactics combine",saved:"Saved and recent",about:"Use this safely"}[r.view];
  return t?t+" — "+base:base+" — "+E.length+" manipulation and control tactics, explained";
}
function setNav(view){
  const map={"":"home",sky:"sky",search:"search",browse:"browse",where:"browse",all:"browse",common:"browse",entry:"browse",guide:"guide",patterns:"browse",saved:"saved",about:"about"};
  const cur=map[view];
  document.querySelectorAll("[data-nav]").forEach(a=>{ if(a.dataset.nav===cur) a.setAttribute("aria-current","page"); else a.removeAttribute("aria-current"); });
}
function lightResults(list){ if(typeof Sky==="undefined") return; Sky.lit(list.slice(0,16).map(e=>e.i),list.length<=12); Sky.set({ring:list.length===1?list[0].i:-1}); const w=$(".sky-window"); if(w&&list.length&&list.length<=40){ const b=w.getBoundingClientRect(), pts=list.slice(0,16).map(e=>Sky.stars[e.i]); let x0=1e9,x1=-1e9,y0=1e9,y1=-1e9; pts.forEach(p=>{x0=Math.min(x0,p.x);x1=Math.max(x1,p.x);y0=Math.min(y0,p.y);y1=Math.max(y1,p.y);}); const k=Math.min(b.width*.8/Math.max(260,x1-x0),b.height*.8/Math.max(260,y1-y0)); Sky.flyTo((x0+x1)/2,(y0+y1)/2,Math.max(Sky.fitK()*.55,Math.min(k,Sky.fitK()*2.5)),900,0,b.top+scrollY+b.height/2-innerHeight/2); } else if(w&&!list.length){ const b=w.getBoundingClientRect(); Sky.flyTo(Sky.S.w/2,Sky.S.h/2,Math.max(Sky.fitK()*.55,Math.min(b.width/Sky.S.w,b.height*1.9/Sky.S.h)),700,0,b.top+scrollY+b.height/2-innerHeight/2); } }
function calmUI(){ const on=Sky.calm||matchMedia("(prefers-reduced-motion: reduce)").matches; document.documentElement.dataset.calm=on?"1":"0"; document.querySelectorAll("[data-calm]").forEach(b=>{b.setAttribute("aria-pressed",on); b.setAttribute("aria-label",on?"Calm mode is on. Turn motion back on":"Turn on calm mode: stops all motion");}); }
function debounce(fn,ms){let t;return function(){clearTimeout(t);t=setTimeout(fn,ms);};}
/* Display type is wide: if one word is wider than its box (Compartmentalization), shrink the headline just enough. */
function fitText(el){
  /* no transition while measuring: Calm and reduced motion give every property a 1ms one, which hides the new size */
  if(!el) return; el.classList.add("measuring"); el.style.transition="none"; el.style.fontSize=""; el.style.overflowWrap="normal"; let fs=parseFloat(getComputedStyle(el).fontSize);
  /* masked words clip their own overflow, so measure them unmasked, as plain text */
  const need=()=>el.scrollWidth;
  for(let i=0,w=need();i<14&&w>el.clientWidth+1&&fs>22;i++,w=need()){ fs=Math.max(22,fs*Math.min(.95,el.clientWidth/w)); el.style.fontSize=fs+"px"; }
  el.style.overflowWrap=need()>el.clientWidth+1?"break-word":"normal"; el.classList.remove("measuring"); el.style.transition="";
}
function fitAll(){ document.querySelectorAll("#main .h1,#main .stage-h,#main .beat-h,#main .gt,#main .sheet-t,#main .sky-h,#main .way h2,#main .pn .t").forEach(fitText); }
let RV=null;
function reveals(){
  if(RV) RV.disconnect();
  const items=document.querySelectorAll(".ways .way,.groups .group,.sect-head,.rows .row:nth-child(-n+9),#main .tile,#main .sec-h");
  if(!("IntersectionObserver" in window)||Sky.calm||matchMedia("(prefers-reduced-motion: reduce)").matches){ document.documentElement.classList.add("no-io"); return; }
  document.documentElement.classList.remove("no-io");
  RV=new IntersectionObserver(es=>es.forEach((x,n)=>{ if(x.isIntersecting){ x.target.style.transitionDelay=(n*70)+"ms"; x.target.classList.add("in"); RV.unobserve(x.target); } }),{rootMargin:"0px 0px -8% 0px"});
  items.forEach(el=>{ el.classList.add("rv"); RV.observe(el); });
}
/* the last two words of a paragraph never part: no single word left alone on the final line */
function noWidows(root){ root.querySelectorAll("p,li,blockquote,.df,.sum,.lede").forEach(el=>{
  const w=document.createTreeWalker(el,NodeFilter.SHOW_TEXT); let last=null; while(w.nextNode()) if(/\S/.test(w.currentNode.nodeValue)) last=w.currentNode;
  if(!last) return; const v=last.nodeValue, i=v.trimEnd().lastIndexOf(" "); if(i<1) return;
  const tail=v.slice(i+1).trim(); if(tail.length>16||tail.length<1) return; last.nodeValue=v.slice(0,i)+"\u00a0"+v.slice(i+1); }); }
function afterRender(r){ if(typeof kbLabels==="function") kbLabels(); noWidows($("#main")); reveals(); headerState(); fitAll(); if(document.fonts) document.fonts.ready.then(fitAll);
  const live=$("#q-page");
  if(!live&&MOVED_FOCUS){ const h=$("#main h1:not(.sr-only)")||$("#main h1"); if(h){ h.setAttribute("tabindex","-1"); h.focus({preventScroll:true}); } }
  MOVED_FOCUS=true;
  if(live){ live.focus({preventScroll:true}); const v=live.value; live.setSelectionRange(v.length,v.length); }
  if(r.view==="entry"){ watchParts(); requestAnimationFrame(()=>trackTo("short")); }
  if(r.view==="browse"&&r.arg) requestAnimationFrame(()=>trackTo(r.arg));
  if(r.view==="search") lightResults(search(SEARCH_Q).list);
  if(r.view==="guide"&&GUIDE.step===2) lightResults(guideList());
  if(r.view==="saved"||r.view==="") refreshMarks();
}
function trackTo(id){ const t=$("#main .track"); if(!t) return; const a=t.querySelector('[data-part="'+id+'"],[data-track="'+id+'"]'), ind=t.querySelector(".ind"); if(!a||!ind) return;
  t.querySelectorAll("a").forEach(x=>x.classList.toggle("on",x===a)); ind.style.transform="translateY("+a.offsetTop+"px)"; ind.style.height=a.offsetHeight+"px"; ind.style.opacity=1; }
let PART_OBS=null;
function watchParts(){
  if(PART_OBS) PART_OBS.disconnect();
  if(!("IntersectionObserver" in window)) return;
  PART_OBS=new IntersectionObserver(es=>{
    es.forEach(x=>{ if(x.isIntersecting){ const id=x.target.id; trackTo(id);
      document.querySelectorAll(".chipbar [data-part]").forEach(a=>a.classList.toggle("on",a.dataset.part===id));
      const chip=$('.chipbar [data-part="'+id+'"]'); if(chip&&chip.scrollIntoView&&window.innerWidth<1040){ const bar=chip.parentNode; bar.scrollTo({left:chip.offsetLeft-16,behavior:"smooth"}); } } });
  },{rootMargin:"-30% 0px -60% 0px"});
  document.querySelectorAll(".part").forEach(p=>PART_OBS.observe(p));
}

/* ---------- events (one delegated listener) ---------- */
window.addEventListener("hashchange",()=>{ render(); });
document.addEventListener("scroll",ev=>{ const t=ev.target;
  if(t&&t.classList&&t.classList.contains("pane-l")){ const w=t.querySelector(".sky-window"); if(w&&WIN_OY!=null){ Sky.set({offY:WIN_OY-t.scrollTop,clipY:Math.max(0,w.getBoundingClientRect().bottom)}); } return; }
  if(LAST_KEY) SCROLL[LAST_KEY]=scrollTop(); headerState(); },{passive:true,capture:true});
document.addEventListener("click",ev=>{
  const a=ev.target.closest("a[href^='#/']");
  if(a){ if(LAST_KEY) SCROLL[LAST_KEY]=scrollTop(); FRESH=true; delete SCROLL[a.getAttribute("href")]; const vt=a.dataset.vt; PENDING_VT=vt!=null?vt:null; return; }
  const t=ev.target.closest("[data-try],[data-clear],[data-star],[data-share],[data-print],[data-copy],[data-where],[data-feel],[data-gstep],[data-greset],[data-setfilter],[data-jump],[data-part],[data-clearsaved],[data-theme-toggle],[data-openall],[data-term],[data-skygroup],[data-zoom],[data-sheetclose],[data-skylink],[data-calm],[data-skygroup],[data-zoom],[data-sheetclose],[data-skylink],[data-calm]");
  if(!t) return;
  const d=t.dataset;
  if(d.try!==undefined){ SEARCH_Q=d.try; if(parse().view==="search"){ const i=$("#q-page"); i.value=SEARCH_Q; updateResults(); } else palOpen(d.try); return; }
  if(d.clear!==undefined){ const f=t.closest("form"), i=f.querySelector("input"); i.value=""; f.classList.remove("has"); if(i.id==="q-page"){SEARCH_Q="";updateResults();} i.focus(); return; }
  if(d.star!==undefined){ const on=toggleStar(d.star); t.setAttribute("aria-pressed",on); t.innerHTML=ic(on?"starOn":"star")+'<span>'+(on?"Saved":"Save")+'</span>'; toast(on?"Saved on this device":"Removed from saved"); return; }
  if(d.share!==undefined){ const url=location.href; if(navigator.share){ navigator.share({title:document.title,url}).catch(()=>{}); } else copyText(url,"Link copied"); return; }
  if(d.print!==undefined){ document.querySelectorAll("details.more").forEach(x=>x.open=true); window.print(); return; }
  if(d.copy!==undefined){ copyText($("#"+d.copy).textContent,"Copied"); return; }
  if(d.where!==undefined){ GUIDE.where=d.where||null; GUIDE.feels=[]; GUIDE.step=1; render(); return; }
  if(d.feel!==undefined){ const k=d.feel; GUIDE.feels=GUIDE.feels.includes(k)?GUIDE.feels.filter(x=>x!==k):GUIDE.feels.concat(k);
    t.setAttribute("aria-pressed",GUIDE.feels.includes(k)); const bar=$(".guide-bar"); if(bar){ bar.children[1].textContent=GUIDE.feels.length?GUIDE.feels.length+" picked":"Pick at least one"; bar.children[2].disabled=!GUIDE.feels.length; } return; }
  if(d.gstep!==undefined){ GUIDE.step=+d.gstep; render(); scrollTop(0); return; }
  if(d.greset!==undefined){ GUIDE={step:0,where:null,feels:[]}; render(); return; }
  if(d.setfilter!==undefined){ FILTER_SET=d.setfilter; const y=scrollTop(); render(); scrollTop(y); return; }
  if(d.jump!==undefined){ ev.preventDefault(); const el=document.getElementById(d.jump); if(el) el.scrollIntoView({behavior:matchMedia("(prefers-reduced-motion: reduce)").matches?"auto":"smooth"}); return; }
  if(d.part!==undefined){ ev.preventDefault(); const el=document.getElementById(d.part); if(el){ trackTo(d.part); el.scrollIntoView({behavior:motionOn()?"smooth":"auto",block:"start"}); const h=el.querySelector("h2"); if(h){h.setAttribute("tabindex","-1");h.focus({preventScroll:true});} } return; }
  if(d.skygroup!==undefined){ const G=Sky.S.groups[d.skygroup]; Sky.set({groupFocus:d.skygroup}); pickStar(-1); Sky.set({groupFocus:d.skygroup});
    Sky.flyTo(G.x,G.y,Math.min(innerWidth,innerHeight)*(innerWidth<760?.36:.3)/G.r,1000,0,innerWidth<760?-innerHeight*.12:0); Sky.st.labels=true; return; }
  if(d.zoom!==undefined){ if(d.zoom==="0"){ Sky.set({groupFocus:null,labels:false}); pickStar(-1); Sky.flyTo(Sky.S.w/2,Sky.S.h/2,Sky.fitK(),900,0,0); } else { Sky.setK(Sky.cam.k*(d.zoom==="1"?1.5:1/1.5)); Sky.invalidate(); } return; }
  if(d.sheetclose!==undefined){ pickStar(-1); return; }
  if(d.skylink!==undefined){ const i=+d.skylink, e=E[i]; const set=[i].concat((e.rel||[]).map(n=>BY[n]&&BY[n].i).filter(x=>x!=null));
    Sky.set({focus:set,link:true,groupFocus:null,labels:true}); Sky.lit([]); let R=60; set.forEach(j=>{R=Math.max(R,Math.hypot(Sky.stars[j].x-Sky.stars[i].x,Sky.stars[j].y-Sky.stars[i].y));});
    Sky.flyTo(Sky.stars[i].x,Sky.stars[i].y,Math.min(Sky.fitK()*6,Math.min(innerWidth,innerHeight)*.3/R),900,0,innerWidth<760?-innerHeight*.2:0); return; }
  if(d.calm!==undefined){ Sky.setCalm(!Sky.calm); calmUI(); return; }
  if(d.term!==undefined){ const def=document.getElementById(d.term); if(def){ def.hidden=!def.hidden; t.setAttribute("aria-expanded",!def.hidden); } return; }
  if(d.clearsaved!==undefined){ if(confirm("Clear your saved and recent entries on this device?")){ store.set("starred",[]); store.set("trail",[]); render(); } return; }
  if(d.themeToggle!==undefined){ setSkin(document.documentElement.getAttribute("data-theme")==="light"?"midnight":"daylight"); return; }
});
document.addEventListener("submit",ev=>{
  const f=ev.target.closest("[data-search]"); if(!f) return; ev.preventDefault();
  const i=f.querySelector("input"); SEARCH_Q=i.value;
  if(parse().view!=="search"){ FRESH=true; location.hash="#/search"; } else { updateResults(); i.blur(); }
});
const updateResults=(()=>{let t; return ()=>{clearTimeout(t); t=setTimeout(()=>{ const r=$("#results"); if(r){ const x=search(SEARCH_Q); lightResults(x.list); r.innerHTML=resultsHTML(x); const c=$("#rcount"); if(c) c.textContent=x.n?(x.list.length?x.list.length+" matches":"No matches"):""; } },120);};})();
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
    ev.preventDefault(); const h=$("#q-home")||$("#q-page"); if(h) h.focus(); else palOpen(); }
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
  b.innerHTML=ic(light?"moon":"sun"); b.setAttribute("aria-label",light?"Switch to Midnight":"Switch to Daylight"); }
themeIcon(); calmUI(); refreshMarks();
/* ---------- private reading ---------- */
function privUI(){ const on=store.private; document.documentElement.dataset.priv=on?"1":"0";
  document.querySelectorAll("[data-private]").forEach(b=>{ b.setAttribute("aria-pressed",on); b.setAttribute("aria-label",on?"Private reading is on. Turn it off":"Turn on private reading"); }); }
document.addEventListener("click",ev=>{ const b=ev.target.closest("[data-private]"); if(!b) return;
  const on=!store.private; store.setPrivate(on); privUI(); if(typeof Sky!=="undefined") refreshMarks();
  toast(on?"Private: nothing is kept after you close this tab":"Private off: saved and recent are kept on this device");
  if(parse().view==="saved"||parse().view==="about") render(); });
privUI();

/* ---------- a pause, after a long stretch of reading (optional) ---------- */
const BREATH_AFTER=20*60*1000; let READ_MS=0, LAST_ACT=Date.now(), BREATH_RET=null;
["pointerdown","keydown","wheel","touchstart","scroll"].forEach(t=>addEventListener(t,()=>{ LAST_ACT=Date.now(); },{passive:true,capture:true}));
setInterval(()=>{ if(document.hidden||store.get("breath",true)===false||!$("#breath").hidden) return; if(Date.now()-LAST_ACT<120000) READ_MS+=15000; if(READ_MS>=BREATH_AFTER) breathShow(); },15000);
function breathShow(){ const b=$("#breath"); if(!b||!b.hidden) return; BREATH_RET=document.activeElement; b.hidden=false; document.documentElement.classList.add("breathing");
  if(typeof Sky!=="undefined") Sky.set({dim:Math.min(Sky.st.dim,.35)}); const k=b.querySelector('[data-breath="go"]'); if(k) k.focus({preventScroll:true}); }
function breathHide(){ const b=$("#breath"); if(!b||b.hidden) return; b.hidden=true; document.documentElement.classList.remove("breathing"); READ_MS=0;
  if(typeof Sky!=="undefined") Sky.set({dim:ROUTE_DIM}); if(BREATH_RET&&BREATH_RET.focus) BREATH_RET.focus({preventScroll:true}); }
document.addEventListener("click",ev=>{ const b=ev.target.closest("[data-breath]"); if(!b) return; const v=b.dataset.breath;
  if(v==="off"){ store.set("breath",false); toast("Reminders off. Turn them back on in Use this safely"); }
  if(v==="on"){ store.set("breath",true); toast("Reminders on"); render(); return; }
  breathHide(); });
document.addEventListener("keydown",ev=>{ if(ev.key==="Escape"&&!$("#breath").hidden) breathHide(); });

/* ---------- a soft light that follows the pointer, behind the panels ---------- */
(function lumen(){ const el=$(".lumen i"); if(!el||!matchMedia("(pointer: fine)").matches) return; let x=innerWidth/2,y=innerHeight/2,tx=x,ty=y,raf=0;
  const step=()=>{ raf=0; x+=(tx-x)*.14; y+=(ty-y)*.14; el.style.transform="translate3d("+(x-450)+"px,"+(y-450)+"px,0)"; if(Math.abs(tx-x)+Math.abs(ty-y)>.5) raf=requestAnimationFrame(step); };
  addEventListener("pointermove",e=>{ tx=e.clientX; ty=e.clientY; if(!raf) raf=requestAnimationFrame(step); document.documentElement.classList.add("lumen-on"); },{passive:true});
  document.addEventListener("pointerleave",()=>document.documentElement.classList.remove("lumen-on")); step(); })();

Sky.onPick=i=>{ if(parse().view===""){ if(i>=0){ PENDING_VT=null; FRESH=true; location.hash=entryHref(E[i]); } return; } pickStar(i); };

/* ---------- the rail: ten marks, one per constellation (after Stripe Press's spine index) ---------- */
(function rail(){ const r=$("#rail"); if(!r) return;
  r.innerHTML=D.groups.map(g=>'<a href="'+href("browse/"+g.k)+'" data-rail="'+g.k+'" data-preview="'+g.k+'" style="--c:'+g.c+'"><i aria-hidden="true"></i><span>'+H(g.label)+'</span></a>').join(""); })();
/* hovering a constellation anywhere lights it up in the sky, without moving the camera */
let PREV_T;
function preview(k){ clearTimeout(PREV_T); if(typeof Sky==="undefined"||document.body.dataset.sky==="sky"||document.body.dataset.sky==="entry") return;
  PREV_T=setTimeout(()=>{ if(k) Sky.set({groupFocus:k,dim:Math.max(ROUTE_DIM,.85)}); else Sky.set({groupFocus:ROUTE_G,dim:ROUTE_DIM}); },k?60:120); }
document.addEventListener("pointerover",ev=>{ if(ev.pointerType!=="mouse") return;
  const p=ev.target.closest("[data-preview]"); if(p){ preview(p.dataset.preview); return; }
  const row=ev.target.closest(".row[data-i]"); const w=$(".sky-window");
  if(row&&w&&w.getBoundingClientRect().bottom>80){ Sky.set({hover:+row.dataset.i}); } });
document.addEventListener("pointerout",ev=>{ if(ev.pointerType!=="mouse") return;
  const p=ev.target.closest("[data-preview]"); if(p&&!p.contains(ev.relatedTarget)) preview(null);
  const row=ev.target.closest(".row[data-i]"); if(row&&!row.contains(ev.relatedTarget)&&!Sky.st.interactive) Sky.set({hover:-1}); });
document.addEventListener("focusin",ev=>{ const p=ev.target.closest&&ev.target.closest("[data-preview]"); if(p) preview(p.dataset.preview); });
document.addEventListener("focusout",ev=>{ const p=ev.target.closest&&ev.target.closest("[data-preview]"); if(p) preview(null); });

/* ---------- two atmospheres: Midnight (ink black) and Daylight (gallery white) ---------- */
function setSkin(k){ const html=document.documentElement; html.setAttribute("data-skin",k); html.setAttribute("data-theme",k==="daylight"?"light":"dark"); store.set("skin",k); store.set("theme",k==="daylight"?"light":"dark"); themeIcon(); }
if(!/^(midnight|daylight)$/.test(store.get("skin","midnight"))) store.set("skin","midnight");
/* a soft aura follows the pointer beneath each button's edge */
document.addEventListener("pointermove",ev=>{ const b=ev.target.closest&&ev.target.closest(".btn,.pill,.chip,.pg,.tile.tac"); if(!b) return; const r=b.getBoundingClientRect(); b.style.setProperty("--mx",(ev.clientX-r.left)+"px"); b.style.setProperty("--my",(ev.clientY-r.top)+"px"); },{passive:true});
Sky.onCluster=g=>{ if(parse().view==="sky"){ const G=Sky.S.groups[g]; pickStar(-1); Sky.set({groupFocus:g,labels:true}); Sky.flyTo(G.x,G.y,Math.min(innerWidth,innerHeight)*(innerWidth<760?.36:.3)/G.r,1100,0,innerWidth<760?-innerHeight*.12:0); } else { FRESH=true; location.hash=href("browse/"+g); } };

/* ---------- go to anything: a command menu (after Linear) ---------- */
const PAGES=[["guide","Help me figure it out","Two short questions"],["sky","The sky","Every tactic as a star"],["common","The most common","Where to begin"],["browse","Browse by what it does","Ten constellations"],["all","A–Z","All "+E.length+" tactics"],["patterns","How tactics combine","Patterns, step by step"],["saved","Saved and recent","On this device"],["about","Use this guide safely","Read this first if you are unsure"]];
const PAL={sel:0,items:[],ret:null};
function palItems(q){
  const n=norm(q), out=[];
  if(!n){
    store.get("trail",[]).slice(0,3).map(t=>BY[t.name]).filter(Boolean).forEach(e=>out.push({h:"Recently read",href:entryHref(e),t:e.n,s:GROUP[e.g].label,c:GROUP[e.g].c,vt:e.i}));
    PAGES.forEach(p=>out.push({h:"Go to",href:href(p[0]),t:p[1],s:p[2]}));
    D.groups.forEach(g=>out.push({h:"Constellations",href:href("browse/"+g.k),t:g.label,s:IN_GROUP[g.k].length+" tactics",c:g.c,g:g.k}));
    return out;
  }
  search(q).list.slice(0,7).forEach(e=>out.push({h:"Tactics",href:entryHref(e),t:e.n,s:e.f.short_definition,c:GROUP[e.g].c,vt:e.i}));
  D.groups.filter(g=>norm(g.label+" "+g.blurb).includes(n)).forEach(g=>out.push({h:"Constellations",href:href("browse/"+g.k),t:g.label,s:IN_GROUP[g.k].length+" tactics",c:g.c,g:g.k}));
  PAGES.filter(p=>norm(p[1]+" "+p[2]).includes(n)).forEach(p=>out.push({h:"Go to",href:href(p[0]),t:p[1],s:p[2]}));
  out.push({h:"Search",href:href("search"),t:"Search every entry for “"+q+"”",s:"Full results, with the matching stars lit",q});
  return out;
}
function palDraw(){
  const box=$("#pal .pal-box"), list=$("#pal-list"), q=$("#pal-q").value; PAL.items=palItems(q); PAL.sel=Math.min(PAL.sel,PAL.items.length-1);
  let h="", last=null;
  PAL.items.forEach((it,i)=>{ if(it.h!==last){ h+='<li class="pal-h" role="presentation">'+it.h+'</li>'; last=it.h; }
    h+='<li role="option" id="pi-'+i+'" class="pal-it" data-pi="'+i+'" aria-selected="'+(i===PAL.sel)+'"'+(it.c?' style="--c:'+it.c+'"':'')+'><i class="'+(it.c?'gd':'gd none')+'" aria-hidden="true"></i><span class="pt"><b>'+H(it.t)+'</b><span>'+H(it.s||"")+'</span></span><span class="pk" aria-hidden="true">'+ic("enter")+'</span></li>'; });
  list.innerHTML=h||'<li class="pal-h">Nothing here</li>';
  $("#pal-q").setAttribute("aria-activedescendant",PAL.items.length?"pi-"+PAL.sel:"");
  const sel=$("#pi-"+PAL.sel); if(sel) sel.scrollIntoView({block:"nearest"});
  const it=PAL.items[PAL.sel]; if(it&&typeof Sky!=="undefined"&&ROUTE_DIM>=.6){ if(it.vt!=null) Sky.set({hover:it.vt}); else Sky.set({hover:-1}); }
}
function palOpen(q){
  const p=$("#pal"); if(!p||!p.hidden) return; PAL.ret=document.activeElement; PAL.sel=0;
  p.querySelector(".pal-box").innerHTML='<div class="pal-in">'+ic("search")+'<label class="sr-only" for="pal-q">Go to a tactic, group or page</label><input id="pal-q" role="combobox" aria-expanded="true" aria-controls="pal-list" aria-autocomplete="list" autocomplete="off" spellcheck="false" placeholder="Go to a tactic, a group or a page"><kbd class="kb">esc</kbd></div><ul class="pal-list" id="pal-list" role="listbox" aria-label="Results"></ul><p class="pal-foot" aria-hidden="true"><span><kbd>↑</kbd><kbd>↓</kbd> move</span><span><kbd>↵</kbd> open</span><span><kbd>esc</kbd> close</span></p>';
  p.hidden=false; document.documentElement.classList.add("pal-on"); if(q) $("#pal-q").value=q; palDraw(); $("#pal-q").focus();
}
function palClose(go){
  const p=$("#pal"); if(!p||p.hidden) return; p.hidden=true; document.documentElement.classList.remove("pal-on"); if(!go&&typeof Sky!=="undefined"&&!Sky.st.interactive) Sky.set({hover:-1});
  if(!go&&PAL.ret&&PAL.ret.focus) PAL.ret.focus({preventScroll:true});
}
function palGo(i){ const it=PAL.items[i]; if(!it) return; palClose(true); if(it.q!=null) SEARCH_Q=it.q; if(LAST_KEY) SCROLL[LAST_KEY]=scrollTop(); FRESH=true; delete SCROLL[it.href]; PENDING_VT=null; location.hash=it.href; }
document.addEventListener("input",ev=>{ if(ev.target.id==="pal-q"){ PAL.sel=0; palDraw(); } });
document.addEventListener("click",ev=>{
  if(ev.target.closest("[data-palclose]")){ palClose(); return; }
  const it=ev.target.closest("[data-pi]"); if(it){ palGo(+it.dataset.pi); return; }
  const f=ev.target.closest("[data-palette]"); if(f){ ev.preventDefault(); ev.stopPropagation(); palOpen(); }
},true);
document.addEventListener("pointermove",ev=>{ const it=ev.target.closest&&ev.target.closest("[data-pi]"); if(it&&+it.dataset.pi!==PAL.sel){ PAL.sel=+it.dataset.pi; document.querySelectorAll(".pal-it").forEach(x=>x.setAttribute("aria-selected",x===it)); $("#pal-q").setAttribute("aria-activedescendant",it.id); } },{passive:true});
document.addEventListener("keydown",ev=>{
  const typing=/INPUT|TEXTAREA|SELECT/.test((document.activeElement||{}).tagName||"");
  if((ev.metaKey||ev.ctrlKey)&&(ev.key==="k"||ev.key==="K")){ ev.preventDefault(); $("#pal").hidden?palOpen():palClose(); return; }
  if(!$("#pal").hidden){
    if(ev.key==="Escape"){ ev.preventDefault(); palClose(); }
    else if(ev.key==="ArrowDown"||ev.key==="ArrowUp"){ ev.preventDefault(); const n=PAL.items.length; if(n){ PAL.sel=(PAL.sel+(ev.key==="ArrowDown"?1:-1)+n)%n; palDraw(); } }
    else if(ev.key==="Enter"){ ev.preventDefault(); palGo(PAL.sel); }
    else if(ev.key==="Tab"){ ev.preventDefault(); $("#pal-q").focus(); }
    return;
  }
  if(typing||ev.metaKey||ev.ctrlKey||ev.altKey) return;
  if(parse().view==="entry"&&(ev.key==="j"||ev.key==="k")){ const a=$('[data-pg="'+(ev.key==="j"?"next":"prev")+'"]'); if(a){ ev.preventDefault(); FRESH=true; location.hash=a.getAttribute("href"); } }
},true);
const KB_MAC=/Mac|iPhone|iPad/.test(navigator.platform||navigator.userAgent); function kbLabels(){ if(!KB_MAC) document.querySelectorAll(".pill .kb").forEach(k=>k.textContent="Ctrl K"); } kbLabels();
document.getElementById("sky").addEventListener("keydown",ev=>{
  if(Sky.st.interactive===false) return; const k=ev.key;
  const dirs={ArrowLeft:[-1,0],ArrowRight:[1,0],ArrowUp:[0,-1],ArrowDown:[0,1]};
  if(dirs[k]){ ev.preventDefault(); const from=SKY_PICK>=0?SKY_PICK:Sky.nearest(innerWidth/2,innerHeight/2,9999); if(SKY_PICK<0){ pickStar(from); return; }
    const [dx,dy]=dirs[k], p=Sky.stars[SKY_PICK]; let best=-1,bs=1e12;
    Sky.stars.forEach((q,i)=>{ if(i===SKY_PICK) return; const vx=q.x-p.x, vy=q.y-p.y, d=Math.hypot(vx,vy); const dot=(vx*dx+vy*dy)/d; if(dot<.5) return; const sc=d*(2-dot); if(sc<bs){bs=sc;best=i;} });
    if(best>=0) pickStar(best); }
  else if(k==="Enter"&&SKY_PICK>=0){ location.hash=entryHref(E[SKY_PICK]); }
  else if(k==="Escape"){ pickStar(-1); }
  else if(k==="+"||k==="="){ Sky.setK(Sky.cam.k*1.4); Sky.invalidate(); } else if(k==="-"){ Sky.setK(Sky.cam.k/1.4); Sky.invalidate(); }
});
render();
