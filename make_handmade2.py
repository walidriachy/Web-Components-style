#!/usr/bin/env python3
"""Hand-written terminal-idiom components, one per tradition."""
import io, json

C = []
def comp(cid, name, cat, tags, note, html, css, js=""):
    C.append(dict(id=cid, name=name, cat=cat, tags=tags, note=note,
                  html=html.strip(), css=css.strip(), js=js.strip()))

MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

# ───────── 1 · Bloomberg function keys + monitor ─────────
comp("hbb-fkey-monitor", "Function Keys + Monitor", "Terminal · Bloomberg",
 "bloomberg amber function keys monitor quotes terminal finance",
 "Bloomberg idiom — amber on pure black with a live function-key row; pressing F1–F6 or clicking swaps the monitor panel, and quotes repaint cyan or red per tick.",
"""
<div class="hbb-fkey-monitor">
  <div class="hbb-fkey-monitor-keys" role="tablist" aria-label="Function keys"></div>
  <div class="hbb-fkey-monitor-body">
    <div class="hbb-fkey-monitor-title"></div>
    <div class="hbb-fkey-monitor-grid"></div>
  </div>
  <div class="hbb-fkey-monitor-cmd"><span class="hbb-fkey-monitor-caret">&gt;</span><span class="hbb-fkey-monitor-typed"></span><span class="hbb-fkey-monitor-cur">&#9608;</span></div>
</div>
""",
""".hbb-fkey-monitor{--hbb-a:#FFB000;--hbb-c:#3FD8E8;--hbb-r:#FF4B4B;--hbb-g:#33E07A;--hbb-d:#7A5A12;
 width:100%;max-width:300px;background:#000;border:1px solid #2A1F05;padding:0;
 font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace;
 font-size:9.5px;line-height:1.35;color:var(--hbb-a);font-variant-numeric:tabular-nums}
.hbb-fkey-monitor-keys{display:grid;grid-template-columns:repeat(6,1fr);border-bottom:1px solid #2A1F05}
.hbb-fkey-monitor-k{all:unset;box-sizing:border-box;cursor:pointer;text-align:center;padding:4px 0;
 font-size:8px;letter-spacing:.04em;color:var(--hbb-d);border-right:1px solid #2A1F05}
.hbb-fkey-monitor-k:last-child{border-right:0}
.hbb-fkey-monitor-k:hover{color:var(--hbb-a)}
.hbb-fkey-monitor-k[aria-selected="true"]{background:var(--hbb-a);color:#000;font-weight:700}
.hbb-fkey-monitor-k:focus-visible{outline:1px solid var(--hbb-c);outline-offset:-1px}
.hbb-fkey-monitor-body{padding:5px 6px;min-height:86px}
.hbb-fkey-monitor-title{color:var(--hbb-c);font-size:8.5px;letter-spacing:.14em;margin-bottom:4px}
.hbb-fkey-monitor-row{display:grid;grid-template-columns:1fr 1fr 1fr;gap:4px;padding:1px 0}
.hbb-fkey-monitor-row span:nth-child(n+2){text-align:right}
.hbb-fkey-monitor-up{color:var(--hbb-g)}
.hbb-fkey-monitor-dn{color:var(--hbb-r)}
.hbb-fkey-monitor-fl{animation:hbb-fkey-monitor-f .45s ease-out}
@keyframes hbb-fkey-monitor-f{0%{background:var(--hbb-a);color:#000}100%{background:transparent}}
.hbb-fkey-monitor-cmd{display:flex;align-items:center;gap:4px;border-top:1px solid #2A1F05;padding:3px 6px;font-size:9px}
.hbb-fkey-monitor-caret{color:var(--hbb-c)}
.hbb-fkey-monitor-cur{animation:hbb-fkey-monitor-b 1s step-end infinite}
@keyframes hbb-fkey-monitor-b{50%{opacity:0}}
@media (prefers-reduced-motion:reduce){.hbb-fkey-monitor-cur,.hbb-fkey-monitor-fl{animation:none}}""",
"""var KEYS=[['F1','EQUITY'],['F2','GOVT'],['F3','FX'],['F4','CMDTY'],['F5','INDEX'],['F6','NEWS']];
var SET={
 'F1':[['AAPL',224.18,1],['MSFT',418.42,1],['NVDA',121.55,-1],['AMZN',186.30,1]],
 'F2':[['US10Y',4.281,-1],['US2Y',4.612,-1],['BUND10',2.344,1],['JGB10',0.982,1]],
 'F3':[['EURUSD',1.0842,1],['GBPUSD',1.2714,-1],['USDJPY',149.32,1],['AUDUSD',0.6631,-1]],
 'F4':[['CL1',78.42,-1],['GC1',2412.8,1],['NG1',2.914,-1],['HG1',4.182,1]],
 'F5':[['SPX',5482.2,1],['NDX',19340.5,1],['DAX',18442,1],['UKX',8214,-1]],
 'F6':[['TOP',0,0],['ECB rate hold',0,0],['CPI beats',0,0],['Fed minutes',0,0]]
};
var keys=root.querySelector('.hbb-fkey-monitor-keys');
var title=root.querySelector('.hbb-fkey-monitor-title');
var grid=root.querySelector('.hbb-fkey-monitor-grid');
var typed=root.querySelector('.hbb-fkey-monitor-typed');
var cur='F1';
KEYS.forEach(function(k){
  var b=document.createElement('button');
  b.type='button';b.className='hbb-fkey-monitor-k';b.textContent=k[0];
  b.setAttribute('role','tab');b.setAttribute('aria-selected',k[0]===cur?'true':'false');
  b.addEventListener('click',function(){pick(k[0]);});
  keys.appendChild(b);
});
function pick(k){
  cur=k;
  var lbl=KEYS.filter(function(x){return x[0]===k;})[0][1];
  title.textContent=k+' \\u2014 '+lbl+' MONITOR';
  typed.textContent=lbl+' <GO>';
  keys.querySelectorAll('.hbb-fkey-monitor-k').forEach(function(b){
    b.setAttribute('aria-selected',b.textContent===k?'true':'false');
  });
  grid.innerHTML='';
  SET[k].forEach(function(r){
    var d=document.createElement('div');d.className='hbb-fkey-monitor-row';
    if(r[2]===0){d.innerHTML='<span></span><span></span><span></span>';d.children[0].textContent=r[0];}
    else{
      d.innerHTML='<span></span><span class="hbb-fkey-monitor-px"></span><span></span>';
      d.children[0].textContent=r[0];
      d.children[1].textContent=r[1].toFixed(r[1]<10?4:2);
      d.children[2].textContent=(r[2]>0?'+':'-')+(Math.random()*1.4).toFixed(2)+'%';
      d.children[2].className=r[2]>0?'hbb-fkey-monitor-up':'hbb-fkey-monitor-dn';
    }
    grid.appendChild(d);
  });
}
pick('F1');
setInterval(function(){
  var cells=grid.querySelectorAll('.hbb-fkey-monitor-px');
  if(!cells.length)return;
  var c=cells[Math.floor(Math.random()*cells.length)];
  var v=parseFloat(c.textContent);
  var dec=(c.textContent.split('.')[1]||'').length;
  c.textContent=(v*(1+(Math.random()-0.5)*0.0012)).toFixed(dec);
  c.classList.remove('hbb-fkey-monitor-fl');void c.offsetWidth;c.classList.add('hbb-fkey-monitor-fl');
},1100);""")

# ───────── 2 · CRT boot sequence ─────────
comp("hcrt-boot-seq", "CRT Boot Sequence", "Terminal · CRT",
 "crt phosphor green boot scanlines typewriter retro vt100",
 "Green phosphor with a repeating-gradient scanline overlay and a text-shadow bloom; lines type out on a character timer and the block cursor parks at the prompt.",
"""
<div class="hcrt-boot-seq">
  <div class="hcrt-boot-seq-screen"><div class="hcrt-boot-seq-out"></div><span class="hcrt-boot-seq-cur">&#9608;</span></div>
  <div class="hcrt-boot-seq-scan" aria-hidden="true"></div>
</div>
""",
""".hcrt-boot-seq{--hcrt-g:#33FF66;position:relative;width:100%;max-width:300px;height:150px;overflow:hidden;
 background:radial-gradient(120% 130% at 50% 40%,#04140A 0%,#010603 78%);border:1px solid #0C2A14;border-radius:4px;
 font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace;
 font-size:9.5px;line-height:1.45;color:var(--hcrt-g);text-shadow:0 0 5px rgba(51,255,102,.55)}
.hcrt-boot-seq-screen{position:absolute;inset:0;padding:7px 8px;overflow:hidden}
.hcrt-boot-seq-out{white-space:pre-wrap}
.hcrt-boot-seq-ok{color:#8CFFB0}
.hcrt-boot-seq-warn{color:#FFD24A;text-shadow:0 0 5px rgba(255,210,74,.5)}
.hcrt-boot-seq-cur{display:inline-block;animation:hcrt-boot-seq-bl 1s step-end infinite}
@keyframes hcrt-boot-seq-bl{50%{opacity:0}}
.hcrt-boot-seq-scan{position:absolute;inset:0;pointer-events:none;
 background:repeating-linear-gradient(180deg,rgba(0,0,0,.34) 0 1px,transparent 1px 3px);
 animation:hcrt-boot-seq-drift 7s linear infinite}
@keyframes hcrt-boot-seq-drift{to{background-position:0 -60px}}
@media (prefers-reduced-motion:reduce){.hcrt-boot-seq-cur,.hcrt-boot-seq-scan{animation:none}}""",
"""var out=root.querySelector('.hcrt-boot-seq-out');
var LINES=[
 ['MERIDIAN BIOS v2.14',''],
 ['CPU ... 68040 @ 33MHz','ok'],
 ['RAM ... 16384K','ok'],
 ['FPU ... present','ok'],
 ['DISK 0 ... 240MB','ok'],
 ['NET  ... link down','warn'],
 ['',''],
 ['booting kernel...','']
];
var li=0,ci=0,buf='';
function step(){
  if(li>=LINES.length){return;}
  var L=LINES[li][0];
  if(ci<L.length){buf+=L[ci++];render();setTimeout(step,16);}
  else{
    var cls=LINES[li][1];
    if(cls)buf=buf+'  ['+(cls==='ok'?'OK':'!!')+']';
    buf+='\\n';li++;ci=0;render();
    setTimeout(step,LINES[li-1][0]?150:60);
  }
}
function render(){
  var html='';
  buf.split('\\n').forEach(function(l,i){
    var c='';
    if(l.indexOf('[OK]')>-1)c=' class="hcrt-boot-seq-ok"';
    if(l.indexOf('[!!]')>-1)c=' class="hcrt-boot-seq-warn"';
    html+='<span'+c+'>'+l.replace(/&/g,'&amp;').replace(/</g,'&lt;')+'</span>\\n';
  });
  out.innerHTML=html;
}
setTimeout(step,320);""")

# ───────── 3 · TUI window ─────────
comp("htui-window", "Box-Drawing Window", "Terminal · TUI",
 "tui ncurses box drawing window menu list reverse video keyboard",
 "Real box-drawing characters compose the frame; the list uses reverse-video selection and responds to arrow keys with a roving tabindex.",
"""
<div class="htui-window" tabindex="0" role="listbox" aria-label="Sessions">
  <div class="htui-window-top"></div>
  <div class="htui-window-rows"></div>
  <div class="htui-window-bot"></div>
  <div class="htui-window-status"><span class="htui-window-hint">&#8593;&#8595; move</span><span class="htui-window-sel">1/5</span></div>
</div>
""",
""".htui-window{--htui-fg:#C8D6C0;--htui-dim:#5E7358;--htui-hl:#0B1F0E;
 width:100%;max-width:300px;background:#060B07;border:1px solid #16301A;padding:6px 7px;outline:none;
 font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace;
 font-size:10px;line-height:1.3;color:var(--htui-fg);white-space:pre}
.htui-window:focus-visible{box-shadow:0 0 0 1px #4ADE80}
.htui-window-top,.htui-window-bot{color:var(--htui-dim)}
.htui-window-row{display:block;padding:0 1px}
.htui-window-row[aria-selected="true"]{background:var(--htui-fg);color:var(--htui-hl)}
.htui-window-status{display:flex;justify-content:space-between;margin-top:3px;color:var(--htui-dim);font-size:8.5px}
.htui-window-hint{letter-spacing:.06em}""",
"""var ITEMS=[['prod-api','running','4d 02h'],['prod-web','running','4d 02h'],['staging','stopped','—'],['worker-01','running','11h'],['cron','degraded','2d 19h']];
var W=34;
function pad(s,n){s=String(s);return s.length>=n?s.slice(0,n):s+Array(n-s.length+1).join(' ');}
function rpad(s,n){s=String(s);return s.length>=n?s.slice(0,n):Array(n-s.length+1).join(' ')+s;}
var title=' SESSIONS ';
var left=Math.floor((W-2-title.length)/2);
root.querySelector('.htui-window-top').textContent='┌'+Array(left+1).join('─')+title+Array(W-2-left-title.length+1).join('─')+'┐';
root.querySelector('.htui-window-bot').textContent='└'+Array(W-1).join('─')+'┘';
var rows=root.querySelector('.htui-window-rows');
ITEMS.forEach(function(it,i){
  var s=document.createElement('span');
  s.className='htui-window-row';s.setAttribute('role','option');
  s.setAttribute('aria-selected',i===0?'true':'false');
  s.textContent='│ '+pad(it[0],11)+pad(it[1],10)+rpad(it[2],8)+' │';
  s.addEventListener('click',function(){pick(i);});
  rows.appendChild(s);
});
var all=rows.querySelectorAll('.htui-window-row'),cur=0;
var sel=root.querySelector('.htui-window-sel');
function pick(i){
  cur=(i+all.length)%all.length;
  all.forEach(function(e,n){e.setAttribute('aria-selected',n===cur?'true':'false');});
  sel.textContent=(cur+1)+'/'+all.length;
}
root.addEventListener('keydown',function(e){
  if(e.key==='ArrowDown'){pick(cur+1);e.preventDefault();}
  if(e.key==='ArrowUp'){pick(cur-1);e.preventDefault();}
});""")

# ───────── 4 · DOS dialog ─────────
comp("hdos-dialog", "DOS Panel Dialog", "Terminal · DOS",
 "dos ansi cp437 blue dialog shadow retro 16 color bbs",
 "The 16-colour DOS idiom — bright cyan on blue with a hard offset shadow, double-line border characters and a highlighted default button.",
"""
<div class="hdos-dialog">
  <div class="hdos-dialog-panel">
    <div class="hdos-dialog-bar">&#9552;&#9552;[ CONFIRM ]&#9552;&#9552;&#9552;&#9552;&#9552;&#9552;&#9552;&#9552;&#9552;&#9552;&#9552;&#9552;</div>
    <div class="hdos-dialog-body">
      <p class="hdos-dialog-msg">Format volume C:\\ ?</p>
      <p class="hdos-dialog-sub">All data will be lost.</p>
    </div>
    <div class="hdos-dialog-btns">
      <button type="button" class="hdos-dialog-b" data-v="ok">&lt; OK &gt;</button>
      <button type="button" class="hdos-dialog-b" data-v="cancel">&lt; Cancel &gt;</button>
    </div>
  </div>
  <div class="hdos-dialog-shadow" aria-hidden="true"></div>
  <div class="hdos-dialog-out"></div>
</div>
""",
""".hdos-dialog{--hd-blue:#0000AA;--hd-cyan:#55FFFF;--hd-white:#FFFFFF;--hd-grey:#AAAAAA;--hd-red:#FF5555;
 position:relative;width:100%;max-width:300px;padding:6px 10px 10px 6px;background:#0A0A0A;
 font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace;font-size:10px;line-height:1.35}
.hdos-dialog-panel{position:relative;z-index:1;background:var(--hd-blue);border:1px solid #3333CC;padding:0 0 6px}
.hdos-dialog-shadow{position:absolute;left:10px;top:10px;right:6px;bottom:6px;background:#000;z-index:0}
.hdos-dialog-bar{background:var(--hd-cyan);color:var(--hd-blue);font-weight:700;padding:1px 4px;letter-spacing:-.02em;overflow:hidden;white-space:nowrap}
.hdos-dialog-body{padding:7px 8px 5px;color:var(--hd-white)}
.hdos-dialog-msg{margin:0 0 3px;font-weight:700}
.hdos-dialog-sub{margin:0;color:var(--hd-grey)}
.hdos-dialog-btns{display:flex;gap:8px;justify-content:center;padding-top:3px}
.hdos-dialog-b{all:unset;cursor:pointer;color:var(--hd-white);padding:0 2px}
.hdos-dialog-b:hover{color:var(--hd-cyan)}
.hdos-dialog-b:focus-visible,.hdos-dialog-b[data-on="1"]{background:var(--hd-white);color:var(--hd-blue)}
.hdos-dialog-out{position:relative;z-index:1;margin-top:6px;color:#55FF55;min-height:13px}
.hdos-dialog-out[data-k="no"]{color:var(--hd-red)}""",
"""var bs=root.querySelectorAll('.hdos-dialog-b'),out=root.querySelector('.hdos-dialog-out'),i=0;
function mark(){bs.forEach(function(b,n){b.setAttribute('data-on',n===i?'1':'0');});}
mark();
bs.forEach(function(b,n){
  b.addEventListener('mouseenter',function(){i=n;mark();});
  b.addEventListener('click',function(){
    var ok=b.getAttribute('data-v')==='ok';
    out.setAttribute('data-k',ok?'yes':'no');
    out.textContent=ok?'C:\\\\> Formatting... aborted (demo)':'C:\\\\> Operation cancelled.';
  });
});
root.addEventListener('keydown',function(e){
  if(e.key==='ArrowLeft'){i=0;mark();e.preventDefault();}
  if(e.key==='ArrowRight'){i=1;mark();e.preventDefault();}
  if(e.key==='Enter'){bs[i].click();}
});""")

# ───────── 5 · htop process monitor ─────────
comp("hsys-htop", "Process Monitor", "Terminal · System",
 "htop top process monitor cpu cores memory bars system linux",
 "A top-style monitor with per-core meters drawn entirely from block characters, colour-graded by load, plus a process table that reorders itself as usage drifts.",
"""
<div class="hsys-htop">
  <div class="hsys-htop-cores"></div>
  <div class="hsys-htop-mem"></div>
  <div class="hsys-htop-hd"><span>PID</span><span>USER</span><span class="hsys-htop-r">CPU%</span><span class="hsys-htop-r">MEM%</span><span>CMD</span></div>
  <div class="hsys-htop-procs"></div>
</div>
""",
""".hsys-htop{--hs-g:#8CE99A;--hs-y:#FFD43B;--hs-r:#FF6B6B;--hs-dim:#4C5A50;--hs-fg:#C9D6CC;
 width:100%;max-width:300px;background:#050806;border:1px solid #14231A;padding:6px 7px;
 font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace;
 font-size:9px;line-height:1.35;color:var(--hs-fg);font-variant-numeric:tabular-nums}
.hsys-htop-core,.hsys-htop-mem{display:grid;grid-template-columns:20px 1fr 30px;gap:4px;align-items:center;white-space:pre}
.hsys-htop-lab{color:var(--hs-dim)}
.hsys-htop-bar{letter-spacing:-.5px}
.hsys-htop-pct{text-align:right;color:var(--hs-dim)}
.hsys-htop-lo{color:var(--hs-g)}.hsys-htop-mid{color:var(--hs-y)}.hsys-htop-hi{color:var(--hs-r)}
.hsys-htop-mem{margin:2px 0 4px}
.hsys-htop-hd{display:grid;grid-template-columns:34px 40px 34px 34px 1fr;gap:4px;color:var(--hs-dim);
 background:#0E1A12;padding:1px 2px;font-size:8px;letter-spacing:.06em}
.hsys-htop-r{text-align:right}
.hsys-htop-row{display:grid;grid-template-columns:34px 40px 34px 34px 1fr;gap:4px;padding:1px 2px;
 transition:background .3s}
.hsys-htop-row span:nth-child(3),.hsys-htop-row span:nth-child(4){text-align:right}
.hsys-htop-cmd{color:var(--hs-fg);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
@media (prefers-reduced-motion:reduce){.hsys-htop-row{transition:none}}""",
"""var W=22;
function bar(p){
  var n=Math.round(p/100*W);
  return Array(n+1).join('|')+Array(W-n+1).join(' ');
}
function cls(p){return p<50?'hsys-htop-lo':p<80?'hsys-htop-mid':'hsys-htop-hi';}
var cores=root.querySelector('.hsys-htop-cores'),memEl=root.querySelector('.hsys-htop-mem');
var C=[38,64,22,81];
C.forEach(function(v,i){
  var d=document.createElement('div');d.className='hsys-htop-core';
  d.innerHTML='<span class="hsys-htop-lab"></span><span class="hsys-htop-bar"></span><span class="hsys-htop-pct"></span>';
  d.children[0].textContent=i+'[';
  cores.appendChild(d);
});
memEl.innerHTML='<span class="hsys-htop-lab">Mem</span><span class="hsys-htop-bar"></span><span class="hsys-htop-pct"></span>';
var mem=58;
var PROCS=[[1842,'walid',24.1,6.2,'node server.js'],[913,'root',11.4,2.1,'systemd'],[2201,'walid',8.8,14.7,'chrome --type=gpu'],[664,'postgres',5.2,9.4,'postgres: writer'],[77,'root',1.1,0.4,'kworker/2:1']];
var procs=root.querySelector('.hsys-htop-procs');
function paint(){
  cores.querySelectorAll('.hsys-htop-core').forEach(function(d,i){
    C[i]=Math.max(2,Math.min(99,C[i]+(Math.random()-0.5)*18));
    var b=d.children[1];b.textContent=bar(C[i]);b.className='hsys-htop-bar '+cls(C[i]);
    d.children[2].textContent=Math.round(C[i])+'%]';
  });
  mem=Math.max(20,Math.min(95,mem+(Math.random()-0.5)*6));
  var mb=memEl.children[1];mb.textContent=bar(mem);mb.className='hsys-htop-bar '+cls(mem);
  memEl.children[2].textContent=Math.round(mem)+'%';
  PROCS.forEach(function(p){p[2]=Math.max(0.1,p[2]+(Math.random()-0.5)*4);});
  PROCS.sort(function(a,b){return b[2]-a[2];});
  procs.innerHTML='';
  PROCS.forEach(function(p){
    var r=document.createElement('div');r.className='hsys-htop-row';
    r.innerHTML='<span></span><span></span><span></span><span></span><span class="hsys-htop-cmd"></span>';
    r.children[0].textContent=p[0];
    r.children[1].textContent=p[1];
    r.children[2].textContent=p[2].toFixed(1);
    r.children[2].className=cls(p[2]*3);
    r.children[3].textContent=p[3].toFixed(1);
    r.children[4].textContent=p[4];
    procs.appendChild(r);
  });
}
paint();
setInterval(paint,1400);""")

# ───────── 6 · matrix rain ─────────
comp("hmx-rain", "Character Rain", "Terminal · Text",
 "matrix rain canvas katakana green falling text effect",
 "Canvas column rain where each column keeps its own head position and speed; the head glyph is drawn brighter than the trail, and the whole field fades by overpainting rather than clearing.",
"""
<div class="hmx-rain"><canvas class="hmx-rain-cv"></canvas><span class="hmx-rain-tag">NO CARRIER</span></div>
""",
""".hmx-rain{position:relative;width:100%;max-width:300px;height:150px;background:#000;border:1px solid #0C2A14;
 border-radius:4px;overflow:hidden;
 font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace}
.hmx-rain-cv{width:100%;height:100%;display:block}
.hmx-rain-tag{position:absolute;left:8px;bottom:7px;font-size:8.5px;letter-spacing:.18em;color:#33FF66;
 text-shadow:0 0 6px rgba(51,255,102,.7);animation:hmx-rain-bl 2.4s step-end infinite}
@keyframes hmx-rain-bl{50%{opacity:.25}}
@media (prefers-reduced-motion:reduce){.hmx-rain-tag{animation:none}}""",
"""var cv=root.querySelector('.hmx-rain-cv'),ctx=cv.getContext('2d');
var GL='ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉ0123456789';
var dpr=Math.min(window.devicePixelRatio||1,2),cols=[],FS=11,raf=0,red=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
function size(){
  var r=cv.getBoundingClientRect();
  cv.width=Math.max(1,r.width*dpr);cv.height=Math.max(1,r.height*dpr);
  var n=Math.floor(cv.width/(FS*dpr));
  cols=[];
  for(var i=0;i<n;i++)cols.push({y:Math.random()*-40,v:0.4+Math.random()*0.9});
  ctx.fillStyle='#000';ctx.fillRect(0,0,cv.width,cv.height);
}
size();
if(window.ResizeObserver){new ResizeObserver(size).observe(cv);}
function frame(){
  ctx.fillStyle='rgba(0,0,0,.09)';ctx.fillRect(0,0,cv.width,cv.height);
  ctx.font=(FS*dpr)+'px ui-monospace,Menlo,monospace';
  ctx.textBaseline='top';
  for(var i=0;i<cols.length;i++){
    var c=cols[i],x=i*FS*dpr,y=c.y*FS*dpr;
    var ch=GL[Math.floor(Math.random()*GL.length)];
    ctx.fillStyle='rgba(140,255,176,.95)';
    ctx.fillText(ch,x,y);
    ctx.fillStyle='rgba(40,190,90,.55)';
    ctx.fillText(GL[Math.floor(Math.random()*GL.length)],x,y-FS*dpr);
    c.y+=c.v;
    if(y>cv.height+FS*dpr*2&&Math.random()>0.975)c.y=Math.random()*-20;
  }
  raf=requestAnimationFrame(frame);
}
if(!red)frame();else{ctx.fillStyle='#8CFFB0';ctx.font=(FS*dpr)+'px monospace';ctx.fillText('01001101',10,20);}""")

io.open("_handmade2.json","w",encoding="utf-8").write(json.dumps(C,ensure_ascii=False,indent=1))
print("wrote %d hand-written terminal components"%len(C))
for c in C: print("  %-24s %s"%(c["cat"],c["name"]))
