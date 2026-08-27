#!/usr/bin/env python3
"""Hand-written market-data and trading components.
Each is {id, name, cat, tags, note, html, css, js} — same contract as the
generated ones: every selector scoped to the id, keyframes prefixed, no deps."""
import io, json

C = []
def comp(cid, name, cat, tags, note, html, css, js=""):
    C.append(dict(id=cid, name=name, cat=cat, tags=tags, note=note,
                  html=html.strip(), css=css.strip(), js=js.strip()))

# ───────────────────────── 1 · terminal quote grid ─────────────────────────
comp("tmx-quote-grid", "Terminal Quote Grid", "Terminal Style",
 "bloomberg terminal amber monospace grid flash tick dense",
 "Amber-on-black monospace grid where each tick repaints a single cell and flashes it, using a class swapped off on animationend rather than a timer.",
"""
<div class="tmx-quote-grid">
  <div class="tmx-quote-grid-hd"><span>SYM</span><span>LAST</span><span>CHG</span><span>VOL</span></div>
  <div class="tmx-quote-grid-body"></div>
  <div class="tmx-quote-grid-ft"><span class="tmx-quote-grid-live"></span>REALTIME · CQS</div>
</div>
""",
""".tmx-quote-grid{--tmx-a:#FFB000;--tmx-dim:#7A5A12;--tmx-up:#25E07A;--tmx-dn:#FF4D4D;width:100%;max-width:300px;background:#000;border:1px solid #2A1F05;padding:6px;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:10.5px;color:var(--tmx-a);font-variant-numeric:tabular-nums}
.tmx-quote-grid-hd,.tmx-quote-grid-row{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:4px}
.tmx-quote-grid-hd{color:var(--tmx-dim);border-bottom:1px solid #2A1F05;padding-bottom:3px;margin-bottom:3px;letter-spacing:.1em}
.tmx-quote-grid-hd span:not(:first-child),.tmx-quote-grid-row span:not(:first-child){text-align:right}
.tmx-quote-grid-row{padding:2px 0}
.tmx-quote-grid-cell{transition:background .18s}
.tmx-quote-grid-up{color:var(--tmx-up)}
.tmx-quote-grid-dn{color:var(--tmx-dn)}
.tmx-quote-grid-flash{animation:tmx-quote-grid-fl .5s ease-out}
@keyframes tmx-quote-grid-fl{0%{background:rgba(255,176,0,.5);color:#000}100%{background:transparent}}
.tmx-quote-grid-ft{display:flex;align-items:center;gap:5px;margin-top:4px;padding-top:3px;border-top:1px solid #2A1F05;color:var(--tmx-dim);font-size:8.5px;letter-spacing:.12em}
.tmx-quote-grid-live{width:5px;height:5px;background:var(--tmx-up);display:block;animation:tmx-quote-grid-pulse 1.6s infinite}
@keyframes tmx-quote-grid-pulse{0%,100%{opacity:1}50%{opacity:.2}}
@media (prefers-reduced-motion:reduce){.tmx-quote-grid-flash,.tmx-quote-grid-live{animation:none}}""",
"""var SYMS=[['ESU5',5482.25],['NQU5',19340.5],['CLV5',78.42],['GCZ5',2412.8],['ZNU5',110.09]];
var body=root.querySelector('.tmx-quote-grid-body');
var rows=SYMS.map(function(s){
  var r=document.createElement('div');r.className='tmx-quote-grid-row';
  r.innerHTML='<span></span><span class="tmx-quote-grid-cell"></span><span class="tmx-quote-grid-cell"></span><span></span>';
  r.children[0].textContent=s[0];
  body.appendChild(r);
  return {el:r,px:s[1],base:s[1],vol:40+Math.floor(Math.random()*900)};
});
function paint(o,flash){
  var chg=o.px-o.base, pct=chg/o.base*100;
  o.el.children[1].textContent=o.px.toFixed(2);
  var c=o.el.children[2];
  c.textContent=(chg>=0?'+':'')+pct.toFixed(2)+'%';
  c.className='tmx-quote-grid-cell '+(chg>=0?'tmx-quote-grid-up':'tmx-quote-grid-dn');
  o.el.children[3].textContent=o.vol+'K';
  if(flash){var t=o.el.children[1];t.classList.remove('tmx-quote-grid-flash');void t.offsetWidth;t.classList.add('tmx-quote-grid-flash');}
}
rows.forEach(function(o){paint(o,false);});
var iv=setInterval(function(){
  var o=rows[Math.floor(Math.random()*rows.length)];
  o.px=+(o.px*(1+(Math.random()-0.5)*0.0016)).toFixed(2);
  o.vol+=Math.floor(Math.random()*12);
  paint(o,true);
},900);
root.addEventListener('DOMNodeRemovedFromDocument',function(){clearInterval(iv);});""")

# ───────────────────────── 2 · DOM ladder ─────────────────────────
comp("dom-click-ladder", "Click-Trade DOM", "Depth & Book",
 "dom ladder depth click trade bid ask working order price",
 "A price ladder where clicking the bid or ask column stages a working order at that level, drawn with a background-size bar so depth needs no extra element.",
"""
<div class="dom-click-ladder">
  <div class="dom-click-ladder-hd"><span>BID</span><span>PRICE</span><span>ASK</span></div>
  <div class="dom-click-ladder-rows"></div>
  <div class="dom-click-ladder-ft">Click a size cell to work an order</div>
</div>
""",
""".dom-click-ladder{--dcl-up:#25E07A;--dcl-dn:#FF5C6C;--dcl-line:#1C2432;width:100%;max-width:300px;background:#0B0F17;border:1px solid var(--dcl-line);border-radius:9px;padding:7px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:10.5px;color:#C9D3E4;font-variant-numeric:tabular-nums}
.dom-click-ladder-hd{display:grid;grid-template-columns:1fr 74px 1fr;gap:3px;color:#5B6883;font-size:8.5px;letter-spacing:.12em;padding-bottom:4px;border-bottom:1px solid var(--dcl-line);margin-bottom:3px}
.dom-click-ladder-hd span:nth-child(2){text-align:center}
.dom-click-ladder-hd span:nth-child(3){text-align:right}
.dom-click-ladder-row{display:grid;grid-template-columns:1fr 74px 1fr;gap:3px;align-items:stretch}
.dom-click-ladder-sz{border:0;background:transparent;color:inherit;font:inherit;padding:2px 5px;cursor:pointer;text-align:left;border-radius:3px;background-repeat:no-repeat;background-size:var(--dcl-w,0%) 100%;transition:filter .15s}
.dom-click-ladder-sz:hover{filter:brightness(1.5)}
.dom-click-ladder-sz:focus-visible{outline:1px solid #6EA8FF;outline-offset:-1px}
.dom-click-ladder-bid{background-image:linear-gradient(90deg,rgba(37,224,122,.22),rgba(37,224,122,.22));background-position:right center;color:var(--dcl-up)}
.dom-click-ladder-ask{background-image:linear-gradient(90deg,rgba(255,92,108,.22),rgba(255,92,108,.22));background-position:left center;color:var(--dcl-dn);text-align:right}
.dom-click-ladder-px{text-align:center;color:#93A2BC;padding:2px 0;border-radius:3px}
.dom-click-ladder-mid .dom-click-ladder-px{background:#1A2333;color:#fff;font-weight:700}
.dom-click-ladder-work{box-shadow:inset 0 0 0 1px #FFB000}
.dom-click-ladder-ft{margin-top:5px;padding-top:4px;border-top:1px solid var(--dcl-line);color:#5B6883;font-size:8.5px;letter-spacing:.06em}""",
"""var rows=root.querySelector('.dom-click-ladder-rows'),ft=root.querySelector('.dom-click-ladder-ft');
var mid=418.55;
for(var i=4;i>=-4;i--){
  var px=+(mid+i*0.05).toFixed(2);
  var r=document.createElement('div');
  r.className='dom-click-ladder-row'+(i===0?' dom-click-ladder-mid':'');
  var bs=i<=0?Math.floor(20+Math.random()*180):0;
  var as=i>=0?Math.floor(20+Math.random()*180):0;
  r.innerHTML='<button class="dom-click-ladder-sz dom-click-ladder-bid" type="button"></button>'+
              '<span class="dom-click-ladder-px"></span>'+
              '<button class="dom-click-ladder-sz dom-click-ladder-ask" type="button"></button>';
  r.children[0].textContent=bs?bs:'';
  r.children[0].style.setProperty('--dcl-w',(bs/2)+'%');
  r.children[1].textContent=px.toFixed(2);
  r.children[2].textContent=as?as:'';
  r.children[2].style.setProperty('--dcl-w',(as/2)+'%');
  rows.appendChild(r);
}
rows.addEventListener('click',function(e){
  var b=e.target.closest('.dom-click-ladder-sz');if(!b||!b.textContent)return;
  root.querySelectorAll('.dom-click-ladder-work').forEach(function(x){x.classList.remove('dom-click-ladder-work');});
  b.classList.add('dom-click-ladder-work');
  var side=b.classList.contains('dom-click-ladder-bid')?'BUY':'SELL';
  var px=b.parentNode.querySelector('.dom-click-ladder-px').textContent;
  ft.textContent='WORKING · '+side+' 25 @ '+px;
});""")

# ───────────────────────── 3 · odometer price ─────────────────────────
comp("odo-hero-price", "Odometer Hero Price", "Price Display",
 "hero price odometer rolling digits ticker large flash",
 "Each digit is a vertical strip translated by digit height, so only changed digits roll — the rest stay perfectly still.",
"""
<div class="odo-hero-price">
  <div class="odo-hero-price-sym">BTC<span class="odo-hero-price-cur">/USD</span></div>
  <div class="odo-hero-price-val"></div>
  <div class="odo-hero-price-chg"><span class="odo-hero-price-arrow">▲</span><span class="odo-hero-price-pct">+1.84%</span><span class="odo-hero-price-abs">+1,052</span></div>
</div>
""",
""".odo-hero-price{--odo-up:#25E07A;--odo-dn:#FF5C6C;width:100%;max-width:300px;padding:14px;background:linear-gradient(160deg,#101724,#0A0E16);border:1px solid #1C2432;border-radius:12px;font-family:ui-sans-serif,-apple-system,'Segoe UI',Roboto,sans-serif;color:#E8EDF6;font-variant-numeric:tabular-nums}
.odo-hero-price-sym{font-size:11px;letter-spacing:.14em;color:#8494AE;font-weight:700}
.odo-hero-price-cur{color:#4E5C76}
.odo-hero-price-val{display:flex;align-items:flex-end;margin:6px 0 4px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:33px;font-weight:600;line-height:1}
.odo-hero-price-d{width:.62em;height:1em;overflow:hidden;position:relative}
.odo-hero-price-strip{position:absolute;left:0;right:0;top:0;display:flex;flex-direction:column;align-items:center;transition:transform .5s cubic-bezier(.22,1,.36,1)}
.odo-hero-price-strip span{height:1em;line-height:1}
.odo-hero-price-sep{width:.34em;text-align:center;color:#4E5C76}
.odo-hero-price-chg{display:flex;align-items:center;gap:7px;font-size:12px;color:var(--odo-up);font-weight:600}
.odo-hero-price-abs{color:#6B7B96;font-weight:400}
.odo-hero-price-down{color:var(--odo-dn)}
@media (prefers-reduced-motion:reduce){.odo-hero-price-strip{transition:none}}""",
"""var val=root.querySelector('.odo-hero-price-val');
var arrow=root.querySelector('.odo-hero-price-arrow'),pct=root.querySelector('.odo-hero-price-pct'),abs=root.querySelector('.odo-hero-price-abs');
var chg=root.querySelector('.odo-hero-price-chg');
var price=58204,base=57152,cells=[];
function build(s){
  val.innerHTML='';cells=[];
  for(var i=0;i<s.length;i++){
    if(s[i]===','||s[i]==='.'){var sp=document.createElement('span');sp.className='odo-hero-price-sep';sp.textContent=s[i];val.appendChild(sp);cells.push(null);continue;}
    var d=document.createElement('span');d.className='odo-hero-price-d';
    var st=document.createElement('span');st.className='odo-hero-price-strip';
    for(var n=0;n<10;n++){var x=document.createElement('span');x.textContent=n;st.appendChild(x);}
    d.appendChild(st);val.appendChild(d);cells.push(st);
  }
}
function show(v){
  var s=Math.round(v).toLocaleString('en-US');
  if(cells.length!==s.length)build(s);
  for(var i=0;i<s.length;i++){if(!cells[i])continue;cells[i].style.transform='translateY(-'+(+s[i])+'em)';}
  var d=v-base,p=d/base*100;
  arrow.textContent=d>=0?'▲':'▼';
  pct.textContent=(d>=0?'+':'')+p.toFixed(2)+'%';
  abs.textContent=(d>=0?'+':'')+Math.round(d).toLocaleString('en-US');
  chg.classList.toggle('odo-hero-price-down',d<0);
}
show(price);
setInterval(function(){price=price*(1+(Math.random()-0.48)*0.004);show(price);},1500);""")

# ───────────────────────── 4 · candlestick + volume ─────────────────────────
comp("cnv-candle-vol", "Candlestick + Volume", "Trade Charts",
 "candlestick ohlc volume canvas chart price wick",
 "Canvas-drawn candles with a volume subplot sharing the horizontal scale; the series is generated as a random walk so every mount differs.",
"""
<div class="cnv-candle-vol">
  <div class="cnv-candle-vol-hd"><span class="cnv-candle-vol-sym">EURUSD · 1H</span><span class="cnv-candle-vol-last"></span></div>
  <canvas class="cnv-candle-vol-cv"></canvas>
</div>
""",
""".cnv-candle-vol{--ccv-up:#25E07A;--ccv-dn:#FF5C6C;width:100%;max-width:300px;background:#0B0F17;border:1px solid #1C2432;border-radius:10px;padding:9px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-variant-numeric:tabular-nums}
.cnv-candle-vol-hd{display:flex;justify-content:space-between;align-items:baseline;font-size:9.5px;color:#5B6883;letter-spacing:.08em;margin-bottom:6px}
.cnv-candle-vol-last{font-size:12px;color:#E8EDF6;font-weight:600}
.cnv-candle-vol-cv{width:100%;height:118px;display:block}""",
"""var cv=root.querySelector('.cnv-candle-vol-cv'),ctx=cv.getContext('2d');
var last=root.querySelector('.cnv-candle-vol-last');
var N=34,data=[],p=1.0842;
for(var i=0;i<N;i++){
  var o=p,c=o*(1+(Math.random()-0.5)*0.0026);
  var h=Math.max(o,c)*(1+Math.random()*0.0009),l=Math.min(o,c)*(1-Math.random()*0.0009);
  data.push({o:o,h:h,l:l,c:c,v:0.3+Math.random()});p=c;
}
last.textContent=data[N-1].c.toFixed(5);
function draw(){
  var dpr=Math.min(window.devicePixelRatio||1,2),r=cv.getBoundingClientRect();
  cv.width=r.width*dpr;cv.height=r.height*dpr;
  var W=cv.width,H=cv.height,PH=H*0.72,VH=H*0.22,gap=H*0.06;
  ctx.clearRect(0,0,W,H);
  var hi=Math.max.apply(null,data.map(function(d){return d.h;}));
  var lo=Math.min.apply(null,data.map(function(d){return d.l;}));
  var pad=(hi-lo)*0.12;hi+=pad;lo-=pad;
  var bw=W/N,cw=bw*0.6;
  ctx.strokeStyle='rgba(255,255,255,.05)';ctx.lineWidth=1*dpr;
  for(var g=1;g<4;g++){var y=PH*g/4;ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(W,y);ctx.stroke();}
  function Y(v){return PH-(v-lo)/(hi-lo)*PH;}
  var mv=Math.max.apply(null,data.map(function(d){return d.v;}));
  data.forEach(function(d,i){
    var x=i*bw+bw/2,up=d.c>=d.o,col=up?'#25E07A':'#FF5C6C';
    ctx.strokeStyle=col;ctx.fillStyle=col;ctx.lineWidth=1*dpr;
    ctx.beginPath();ctx.moveTo(x,Y(d.h));ctx.lineTo(x,Y(d.l));ctx.stroke();
    var yo=Y(d.o),yc=Y(d.c),top=Math.min(yo,yc),hgt=Math.max(1.5*dpr,Math.abs(yc-yo));
    ctx.fillRect(x-cw/2,top,cw,hgt);
    ctx.globalAlpha=.42;
    var vh=d.v/mv*VH;
    ctx.fillRect(x-cw/2,PH+gap+(VH-vh),cw,vh);
    ctx.globalAlpha=1;
  });
}
draw();
if(window.ResizeObserver){new ResizeObserver(draw).observe(cv);}""")

# ───────────────────────── 5 · depth curve ─────────────────────────
comp("dep-cum-curve", "Cumulative Depth", "Depth & Book",
 "depth curve cumulative liquidity bid ask svg area mid",
 "Two mirrored cumulative-sum area paths built in SVG from the book, with the mid marked by a dashed rule and hover reading out size at price.",
"""
<div class="dep-cum-curve">
  <div class="dep-cum-curve-hd"><span>DEPTH</span><span class="dep-cum-curve-read">hover the curve</span></div>
  <svg class="dep-cum-curve-svg" viewBox="0 0 280 96" preserveAspectRatio="none">
    <path class="dep-cum-curve-bidf"></path><path class="dep-cum-curve-askf"></path>
    <path class="dep-cum-curve-bidl"></path><path class="dep-cum-curve-askl"></path>
    <line class="dep-cum-curve-mid" x1="140" y1="0" x2="140" y2="96"></line>
  </svg>
  <div class="dep-cum-curve-ax"><span>418.20</span><span class="dep-cum-curve-midlab">418.55</span><span>418.90</span></div>
</div>
""",
""".dep-cum-curve{width:100%;max-width:300px;background:#0B0F17;border:1px solid #1C2432;border-radius:10px;padding:9px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:9px;color:#5B6883;font-variant-numeric:tabular-nums}
.dep-cum-curve-hd{display:flex;justify-content:space-between;letter-spacing:.12em;margin-bottom:5px}
.dep-cum-curve-read{color:#93A2BC}
.dep-cum-curve-svg{width:100%;height:96px;display:block;cursor:crosshair}
.dep-cum-curve-bidf{fill:rgba(37,224,122,.18)}
.dep-cum-curve-askf{fill:rgba(255,92,108,.18)}
.dep-cum-curve-bidl{fill:none;stroke:#25E07A;stroke-width:1.6}
.dep-cum-curve-askl{fill:none;stroke:#FF5C6C;stroke-width:1.6}
.dep-cum-curve-mid{stroke:#4E5C76;stroke-width:1;stroke-dasharray:3 3}
.dep-cum-curve-ax{display:flex;justify-content:space-between;margin-top:4px}
.dep-cum-curve-midlab{color:#93A2BC}""",
"""var svg=root.querySelector('.dep-cum-curve-svg'),read=root.querySelector('.dep-cum-curve-read');
var bids=[],asks=[],cb=0,ca=0;
for(var i=0;i<24;i++){cb+=20+Math.random()*90;bids.push(cb);ca+=20+Math.random()*90;asks.push(ca);}
var maxv=Math.max(cb,ca);
function pts(arr,fromMid){
  var out=[];
  for(var i=0;i<arr.length;i++){
    var x=fromMid?140-(i+1)/arr.length*140:140+(i+1)/arr.length*140;
    out.push([x,96-arr[i]/maxv*88]);
  }
  return out;
}
function d(p,close){
  var s='M140,96 ';
  p.forEach(function(q){s+='L'+q[0].toFixed(1)+','+q[1].toFixed(1)+' ';});
  if(close)s+='L'+p[p.length-1][0].toFixed(1)+',96 Z';
  return s;
}
var bp=pts(bids,true),ap=pts(asks,false);
root.querySelector('.dep-cum-curve-bidf').setAttribute('d',d(bp,true));
root.querySelector('.dep-cum-curve-askf').setAttribute('d',d(ap,true));
root.querySelector('.dep-cum-curve-bidl').setAttribute('d',d(bp,false));
root.querySelector('.dep-cum-curve-askl').setAttribute('d',d(ap,false));
svg.addEventListener('pointermove',function(e){
  var r=svg.getBoundingClientRect();
  var x=(e.clientX-r.left)/r.width*280;
  var side=x<140?'BID':'ASK';
  var frac=Math.abs(x-140)/140;
  var arr=x<140?bids:asks;
  var v=arr[Math.min(arr.length-1,Math.floor(frac*arr.length))]||0;
  var px=(418.55+(x-140)/140*0.35).toFixed(2);
  read.textContent=side+' '+Math.round(v)+' @ '+px;
});
svg.addEventListener('pointerleave',function(){read.textContent='hover the curve';});""")

# ───────────────────────── 6 · liquidation distance ─────────────────────────
comp("liq-distance-bar", "Liquidation Distance", "Positions",
 "liquidation margin leverage risk position distance warning",
 "A single track carrying entry, mark and liquidation as positioned markers; the fill colour crosses to amber then red as the mark approaches liquidation.",
"""
<div class="liq-distance-bar">
  <div class="liq-distance-bar-hd"><span class="liq-distance-bar-sym">BTC-PERP <span class="liq-distance-bar-lev">20×</span></span><span class="liq-distance-bar-state">SAFE</span></div>
  <div class="liq-distance-bar-track">
    <div class="liq-distance-bar-fill"></div>
    <div class="liq-distance-bar-mark liq-distance-bar-entry"><span>entry</span></div>
    <div class="liq-distance-bar-mark liq-distance-bar-liq"><span>liq</span></div>
    <div class="liq-distance-bar-now"></div>
  </div>
  <div class="liq-distance-bar-ft"><span class="liq-distance-bar-px"></span><span class="liq-distance-bar-pct"></span></div>
</div>
""",
""".liq-distance-bar{--lq-ok:#25E07A;--lq-warn:#FFB000;--lq-bad:#FF5C6C;width:100%;max-width:300px;background:#0B0F17;border:1px solid #1C2432;border-radius:10px;padding:11px;font-family:ui-sans-serif,-apple-system,'Segoe UI',Roboto,sans-serif;font-size:11px;color:#C9D3E4;font-variant-numeric:tabular-nums}
.liq-distance-bar-hd{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px}
.liq-distance-bar-sym{font-weight:700;letter-spacing:.03em}
.liq-distance-bar-lev{color:#8494AE;font-weight:400;font-size:10px}
.liq-distance-bar-state{font-family:ui-monospace,Menlo,monospace;font-size:9px;letter-spacing:.12em;padding:2px 6px;border-radius:4px;background:rgba(37,224,122,.14);color:var(--lq-ok)}
.liq-distance-bar-state.liq-distance-bar-w{background:rgba(255,176,0,.14);color:var(--lq-warn)}
.liq-distance-bar-state.liq-distance-bar-b{background:rgba(255,92,108,.16);color:var(--lq-bad)}
.liq-distance-bar-track{position:relative;height:6px;border-radius:99px;background:#18202E;margin:0 0 16px}
.liq-distance-bar-fill{position:absolute;left:0;top:0;bottom:0;border-radius:99px;background:var(--lq-ok);transition:width .5s cubic-bezier(.22,1,.36,1),background .5s}
.liq-distance-bar-mark{position:absolute;top:-4px;width:2px;height:14px;background:#4E5C76}
.liq-distance-bar-mark span{position:absolute;top:16px;left:50%;transform:translateX(-50%);font-family:ui-monospace,Menlo,monospace;font-size:8px;color:#5B6883;letter-spacing:.08em}
.liq-distance-bar-entry{left:22%}
.liq-distance-bar-liq{left:88%;background:var(--lq-bad)}
.liq-distance-bar-liq span{color:var(--lq-bad)}
.liq-distance-bar-now{position:absolute;top:-5px;width:10px;height:16px;margin-left:-5px;border-radius:3px;background:#fff;box-shadow:0 2px 8px rgba(0,0,0,.7);transition:left .5s cubic-bezier(.22,1,.36,1)}
.liq-distance-bar-ft{display:flex;justify-content:space-between;font-family:ui-monospace,Menlo,monospace;font-size:11px}
.liq-distance-bar-pct{font-weight:700}
@media (prefers-reduced-motion:reduce){.liq-distance-bar-fill,.liq-distance-bar-now{transition:none}}""",
"""var fill=root.querySelector('.liq-distance-bar-fill'),now=root.querySelector('.liq-distance-bar-now');
var st=root.querySelector('.liq-distance-bar-state'),pxE=root.querySelector('.liq-distance-bar-px'),pcE=root.querySelector('.liq-distance-bar-pct');
var entry=58200,liq=52400,px=57900;
function paint(){
  var span=entry-liq;
  var prog=Math.max(0,Math.min(1,(entry-px)/span));
  var pos=22+prog*66;
  now.style.left=pos+'%';fill.style.width=pos+'%';
  var col=prog<0.4?'var(--lq-ok)':prog<0.72?'var(--lq-warn)':'var(--lq-bad)';
  fill.style.background=col;
  st.className='liq-distance-bar-state'+(prog<0.4?'':prog<0.72?' liq-distance-bar-w':' liq-distance-bar-b');
  st.textContent=prog<0.4?'SAFE':prog<0.72?'WATCH':'AT RISK';
  pxE.textContent='mark '+Math.round(px).toLocaleString('en-US');
  var d=(px-liq)/px*100;
  pcE.textContent=d.toFixed(1)+'% to liq';
  pcE.style.color=prog<0.4?'var(--lq-ok)':prog<0.72?'var(--lq-warn)':'var(--lq-bad)';
}
paint();
setInterval(function(){px+=(Math.random()-0.52)*420;px=Math.max(53000,Math.min(59500,px));paint();},1800);""")

# ───────────────────────── 7 · sector heatmap ─────────────────────────
comp("shm-sector-heat", "Sector Heat Map", "Market Overview",
 "sector heatmap treemap market performance grid tiles",
 "A weighted grid where tile area comes from market cap and colour from performance, with a diverging red-to-green scale anchored at zero.",
"""
<div class="shm-sector-heat">
  <div class="shm-sector-heat-hd"><span>SECTORS · 1D</span><span class="shm-sector-heat-legend"><i class="shm-sector-heat-l1"></i><i class="shm-sector-heat-l2"></i><i class="shm-sector-heat-l3"></i><i class="shm-sector-heat-l4"></i><i class="shm-sector-heat-l5"></i></span></div>
  <div class="shm-sector-heat-grid"></div>
</div>
""",
""".shm-sector-heat{width:100%;max-width:300px;background:#0B0F17;border:1px solid #1C2432;border-radius:10px;padding:9px;font-family:ui-sans-serif,-apple-system,'Segoe UI',Roboto,sans-serif;font-variant-numeric:tabular-nums}
.shm-sector-heat-hd{display:flex;justify-content:space-between;align-items:center;font-family:ui-monospace,Menlo,monospace;font-size:8.5px;letter-spacing:.12em;color:#5B6883;margin-bottom:6px}
.shm-sector-heat-legend{display:flex;gap:2px}
.shm-sector-heat-legend i{width:11px;height:6px;display:block;border-radius:1px}
.shm-sector-heat-l1{background:#B3323C}.shm-sector-heat-l2{background:#6E2A33}.shm-sector-heat-l3{background:#2A3140}.shm-sector-heat-l4{background:#1E6B47}.shm-sector-heat-l5{background:#22A163}
.shm-sector-heat-grid{display:grid;grid-template-columns:repeat(6,1fr);grid-auto-rows:31px;gap:3px}
.shm-sector-heat-tile{border-radius:4px;padding:4px 5px;display:flex;flex-direction:column;justify-content:space-between;overflow:hidden;cursor:default;transition:transform .16s cubic-bezier(.22,1,.36,1),filter .16s}
.shm-sector-heat-tile:hover{transform:scale(1.06);filter:brightness(1.25);z-index:2}
.shm-sector-heat-n{font-size:8.5px;font-weight:700;letter-spacing:.02em;color:rgba(255,255,255,.94);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.shm-sector-heat-v{font-family:ui-monospace,Menlo,monospace;font-size:8.5px;color:rgba(255,255,255,.82)}
@media (prefers-reduced-motion:reduce){.shm-sector-heat-tile{transition:none}}""",
"""var D=[['Tech',2.41,6,2],['Financials',0.82,3,1],['Health',-0.64,3,1],['Energy',-1.92,2,1],['Cons Disc',1.15,2,1],['Industrials',0.31,2,1],['Utilities',-0.22,2,1],['Materials',-1.10,2,1],['Staples',0.44,2,1],['Real Est',-2.35,2,1]];
var g=root.querySelector('.shm-sector-heat-grid');
function col(v){
  var t=Math.max(-1,Math.min(1,v/2.5));
  if(t>=0){var a=t;return 'rgb('+Math.round(42+(34-42)*a)+','+Math.round(49+(161-49)*a)+','+Math.round(64+(99-64)*a)+')';}
  var b=-t;return 'rgb('+Math.round(42+(179-42)*b)+','+Math.round(49+(50-49)*b)+','+Math.round(64+(60-64)*b)+')';
}
D.forEach(function(d){
  var t=document.createElement('div');
  t.className='shm-sector-heat-tile';
  t.style.gridColumn='span '+d[2];t.style.gridRow='span '+d[3];
  t.style.background=col(d[1]);
  t.innerHTML='<span class="shm-sector-heat-n"></span><span class="shm-sector-heat-v"></span>';
  t.children[0].textContent=d[0];
  t.children[1].textContent=(d[1]>=0?'+':'')+d[1].toFixed(2)+'%';
  t.title=d[0]+' '+(d[1]>=0?'+':'')+d[1].toFixed(2)+'%';
  g.appendChild(t);
});""")

# ───────────────────────── 8 · time & sales ─────────────────────────
comp("tns-tape", "Time & Sales Tape", "Market Data",
 "time sales tape prints trades feed aggressor block",
 "New prints unshift into the list with a height-and-opacity entry animation, aggressor side driving colour and block trades getting a bolder weight.",
"""
<div class="tns-tape">
  <div class="tns-tape-hd"><span>TIME</span><span>PRICE</span><span>SIZE</span></div>
  <div class="tns-tape-rows"></div>
</div>
""",
""".tns-tape{--tns-up:#25E07A;--tns-dn:#FF5C6C;width:100%;max-width:300px;height:150px;background:#0B0F17;border:1px solid #1C2432;border-radius:10px;padding:8px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:10px;color:#C9D3E4;font-variant-numeric:tabular-nums;display:flex;flex-direction:column;overflow:hidden}
.tns-tape-hd{display:grid;grid-template-columns:1fr 1fr 1fr;color:#5B6883;font-size:8.5px;letter-spacing:.12em;padding-bottom:4px;border-bottom:1px solid #1C2432;flex:none}
.tns-tape-hd span:nth-child(2),.tns-tape-hd span:nth-child(3){text-align:right}
.tns-tape-rows{flex:1;overflow:hidden}
.tns-tape-row{display:grid;grid-template-columns:1fr 1fr 1fr;padding:1.5px 0;animation:tns-tape-in .32s cubic-bezier(.22,1,.36,1)}
.tns-tape-row span:nth-child(2),.tns-tape-row span:nth-child(3){text-align:right}
.tns-tape-t{color:#5B6883}
.tns-tape-buy{color:var(--tns-up)}
.tns-tape-sell{color:var(--tns-dn)}
.tns-tape-blk{font-weight:700;text-shadow:0 0 8px currentColor}
@keyframes tns-tape-in{from{opacity:0;transform:translateY(-6px)}}
@media (prefers-reduced-motion:reduce){.tns-tape-row{animation:none}}""",
"""var rows=root.querySelector('.tns-tape-rows'),px=418.55;
function tick(){
  px+=(Math.random()-0.5)*0.06;
  var buy=Math.random()>0.48;
  var sz=Math.random()>0.9?Math.floor(2000+Math.random()*8000):Math.floor(10+Math.random()*400);
  var blk=sz>=2000;
  var d=new Date();
  var t=('0'+d.getHours()).slice(-2)+':'+('0'+d.getMinutes()).slice(-2)+':'+('0'+d.getSeconds()).slice(-2);
  var r=document.createElement('div');
  r.className='tns-tape-row';
  r.innerHTML='<span class="tns-tape-t"></span><span></span><span></span>';
  r.children[0].textContent=t;
  r.children[1].textContent=px.toFixed(2);
  r.children[1].className=buy?'tns-tape-buy':'tns-tape-sell';
  r.children[2].textContent=sz.toLocaleString('en-US');
  if(blk){r.children[1].className+=' tns-tape-blk';r.children[2].className='tns-tape-blk';}
  rows.insertBefore(r,rows.firstChild);
  while(rows.children.length>9)rows.removeChild(rows.lastChild);
}
for(var i=0;i<9;i++)tick();
setInterval(tick,760);""")

# ───────────────────────── 9 · retail portfolio hero ─────────────────────────
comp("rtl-portfolio-hero", "Retail Portfolio Hero", "Retail Style",
 "retail consumer portfolio hero balance period toggle friendly gradient",
 "Consumer-investing treatment — oversized balance, a segmented period toggle with a sliding pill, and a chart that redraws with a stroke-dash sweep on each change.",
"""
<div class="rtl-portfolio-hero">
  <span class="rtl-portfolio-hero-lab">Portfolio value</span>
  <div class="rtl-portfolio-hero-val">$48,120<span class="rtl-portfolio-hero-c">.44</span></div>
  <div class="rtl-portfolio-hero-chg"><span class="rtl-portfolio-hero-pill">▲ 12.4%</span><span class="rtl-portfolio-hero-abs">+$5,304 this month</span></div>
  <svg class="rtl-portfolio-hero-svg" viewBox="0 0 260 44" preserveAspectRatio="none">
    <defs><linearGradient class="rtl-portfolio-hero-g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#25E07A" stop-opacity=".38"/><stop offset="1" stop-color="#25E07A" stop-opacity="0"/></linearGradient></defs>
    <path class="rtl-portfolio-hero-area"></path><path class="rtl-portfolio-hero-line"></path>
  </svg>
  <div class="rtl-portfolio-hero-seg"><span class="rtl-portfolio-hero-thumb"></span><button type="button" class="rtl-portfolio-hero-b" aria-pressed="true">1W</button><button type="button" class="rtl-portfolio-hero-b" aria-pressed="false">1M</button><button type="button" class="rtl-portfolio-hero-b" aria-pressed="false">1Y</button><button type="button" class="rtl-portfolio-hero-b" aria-pressed="false">ALL</button></div>
</div>
""",
""".rtl-portfolio-hero{width:100%;max-width:300px;background:linear-gradient(165deg,#132018,#0B0F17 62%);border:1px solid #1C2432;border-radius:16px;padding:14px;font-family:ui-sans-serif,-apple-system,'Segoe UI',Roboto,sans-serif;color:#E8EDF6;font-variant-numeric:tabular-nums}
.rtl-portfolio-hero-lab{font-size:11px;color:#7E8FA8}
.rtl-portfolio-hero-val{font-size:29px;font-weight:750;letter-spacing:-.02em;margin:2px 0 5px}
.rtl-portfolio-hero-c{font-size:17px;color:#7E8FA8;font-weight:600}
.rtl-portfolio-hero-chg{display:flex;align-items:center;gap:8px;margin-bottom:6px}
.rtl-portfolio-hero-pill{background:rgba(37,224,122,.16);color:#25E07A;font-size:11px;font-weight:700;padding:3px 8px;border-radius:99px}
.rtl-portfolio-hero-abs{font-size:10.5px;color:#7E8FA8}
.rtl-portfolio-hero-svg{width:100%;height:44px;display:block;margin-bottom:9px}
.rtl-portfolio-hero-area{fill:url(#none)}
.rtl-portfolio-hero-line{fill:none;stroke:#25E07A;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.rtl-portfolio-hero-seg{position:relative;display:grid;grid-template-columns:repeat(4,1fr);background:#141C28;border-radius:99px;padding:3px}
.rtl-portfolio-hero-thumb{position:absolute;top:3px;left:3px;width:calc(25% - 1.5px);height:calc(100% - 6px);border-radius:99px;background:#25E07A;transition:transform .34s cubic-bezier(.34,1.4,.4,1)}
.rtl-portfolio-hero-b{position:relative;z-index:1;border:0;background:transparent;color:#7E8FA8;font-family:inherit;font-size:10.5px;font-weight:700;padding:6px 0;cursor:pointer;border-radius:99px;transition:color .22s}
.rtl-portfolio-hero-b[aria-pressed="true"]{color:#04231F}
.rtl-portfolio-hero-b:focus-visible{outline:2px solid #6EA8FF;outline-offset:2px}
@media (prefers-reduced-motion:reduce){.rtl-portfolio-hero-thumb{transition:none}}""",
"""var area=root.querySelector('.rtl-portfolio-hero-area'),line=root.querySelector('.rtl-portfolio-hero-line');
var grad=root.querySelector('.rtl-portfolio-hero-g');
var uid='rtl-portfolio-hero-grad-'+Math.random().toString(36).slice(2,8);
grad.setAttribute('id',uid);area.setAttribute('fill','url(#'+uid+')');
var btns=root.querySelectorAll('.rtl-portfolio-hero-b'),thumb=root.querySelector('.rtl-portfolio-hero-thumb');
function series(n,seed){
  var p=[],v=20;
  for(var i=0;i<n;i++){v+=Math.sin(i*seed)*3+(Math.random()-0.45)*4;v=Math.max(6,Math.min(38,v));p.push(v);}
  return p;
}
function draw(n,seed){
  var p=series(n,seed),d='';
  p.forEach(function(v,i){d+=(i?'L':'M')+(i/(n-1)*260).toFixed(1)+','+(44-v).toFixed(1)+' ';});
  line.setAttribute('d',d);
  area.setAttribute('d',d+'L260,44 L0,44 Z');
  var len=line.getTotalLength?line.getTotalLength():600;
  line.style.transition='none';line.style.strokeDasharray=len;line.style.strokeDashoffset=len;
  void line.getBoundingClientRect();
  line.style.transition='stroke-dashoffset .7s cubic-bezier(.22,1,.36,1)';
  line.style.strokeDashoffset=0;
}
draw(30,0.5);
btns.forEach(function(b,i){
  b.addEventListener('click',function(){
    btns.forEach(function(x){x.setAttribute('aria-pressed','false');});
    b.setAttribute('aria-pressed','true');
    thumb.style.transform='translateX('+(i*100)+'%)';
    draw(20+i*14,0.3+i*0.25);
  });
});""")

# ───────────────────────── 10 · funding rate ─────────────────────────
comp("fnd-funding-ticker", "Funding Rate Ticker", "Crypto Trading",
 "perpetual funding rate countdown crypto perp basis long short",
 "Perpetual funding shown as a signed bar either side of a zero axis, with a live countdown to the next settlement and the payer side named explicitly.",
"""
<div class="fnd-funding-ticker">
  <div class="fnd-funding-ticker-hd"><span class="fnd-funding-ticker-sym">BTC-PERP</span><span class="fnd-funding-ticker-cd"></span></div>
  <div class="fnd-funding-ticker-rate"></div>
  <div class="fnd-funding-ticker-axis"><div class="fnd-funding-ticker-bar"></div><div class="fnd-funding-ticker-zero"></div></div>
  <div class="fnd-funding-ticker-who"></div>
</div>
""",
""".fnd-funding-ticker{--fnd-pos:#25E07A;--fnd-neg:#FF5C6C;width:100%;max-width:300px;background:#0B0F17;border:1px solid #1C2432;border-radius:10px;padding:11px;font-family:ui-sans-serif,-apple-system,'Segoe UI',Roboto,sans-serif;color:#C9D3E4;font-variant-numeric:tabular-nums}
.fnd-funding-ticker-hd{display:flex;justify-content:space-between;align-items:center;font-size:10.5px}
.fnd-funding-ticker-sym{font-weight:700;letter-spacing:.04em}
.fnd-funding-ticker-cd{font-family:ui-monospace,Menlo,monospace;font-size:10px;color:#7E8FA8}
.fnd-funding-ticker-rate{font-family:ui-monospace,Menlo,monospace;font-size:24px;font-weight:600;margin:6px 0 8px}
.fnd-funding-ticker-axis{position:relative;height:8px;background:#18202E;border-radius:3px;overflow:hidden}
.fnd-funding-ticker-bar{position:absolute;top:0;bottom:0;left:50%;width:0;background:var(--fnd-pos);transition:width .5s cubic-bezier(.22,1,.36,1),left .5s cubic-bezier(.22,1,.36,1),background .3s}
.fnd-funding-ticker-zero{position:absolute;left:50%;top:0;bottom:0;width:1px;background:#4E5C76}
.fnd-funding-ticker-who{margin-top:7px;font-size:10px;color:#7E8FA8}
@media (prefers-reduced-motion:reduce){.fnd-funding-ticker-bar{transition:none}}""",
"""var rateEl=root.querySelector('.fnd-funding-ticker-rate'),bar=root.querySelector('.fnd-funding-ticker-bar');
var who=root.querySelector('.fnd-funding-ticker-who'),cd=root.querySelector('.fnd-funding-ticker-cd');
var rate=0.0112,left=3*3600+842;
function paint(){
  var s=(rate>=0?'+':'')+rate.toFixed(4)+'%';
  rateEl.textContent=s;
  rateEl.style.color=rate>=0?'var(--fnd-pos)':'var(--fnd-neg)';
  var w=Math.min(50,Math.abs(rate)/0.05*50);
  bar.style.width=w+'%';
  bar.style.left=rate>=0?'50%':(50-w)+'%';
  bar.style.background=rate>=0?'var(--fnd-pos)':'var(--fnd-neg)';
  who.textContent=rate>=0?'Longs pay shorts · 8h interval':'Shorts pay longs · 8h interval';
}
function clock(){
  left--;if(left<0)left=8*3600;
  var h=Math.floor(left/3600),m=Math.floor(left%3600/60),s=left%60;
  cd.textContent='next in '+h+':'+('0'+m).slice(-2)+':'+('0'+s).slice(-2);
}
paint();clock();
setInterval(clock,1000);
setInterval(function(){rate+=(Math.random()-0.5)*0.006;rate=Math.max(-0.045,Math.min(0.045,rate));paint();},2600);""")

# ───────────────────────── 11 · institutional blotter ─────────────────────────
comp("inst-blotter-grid", "Institutional Blotter", "Institutional",
 "blotter grid dense institutional keyboard rows status fills",
 "Tiny-type professional grid with hairline rules, keyboard row navigation via arrow keys and a roving tabindex, and fill progress drawn straight into the row background.",
"""
<div class="inst-blotter-grid">
  <div class="inst-blotter-grid-hd"><span>ORDER</span><span>SYM</span><span>SIDE</span><span class="inst-blotter-grid-r">FILLED</span><span class="inst-blotter-grid-r">AVG</span></div>
  <div class="inst-blotter-grid-rows" role="listbox" aria-label="Orders"></div>
  <div class="inst-blotter-grid-ft"><span class="inst-blotter-grid-sel">— no selection</span><span>↑↓ navigate</span></div>
</div>
""",
""".inst-blotter-grid{--ib-line:#161D28;width:100%;max-width:300px;background:#080B11;border:1px solid var(--ib-line);border-radius:6px;padding:6px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:9px;color:#AFBACD;font-variant-numeric:tabular-nums}
.inst-blotter-grid-hd,.inst-blotter-grid-row{display:grid;grid-template-columns:52px 44px 30px 1fr 46px;gap:4px;align-items:center}
.inst-blotter-grid-hd{color:#4A566C;font-size:7.5px;letter-spacing:.14em;padding-bottom:3px;border-bottom:1px solid var(--ib-line)}
.inst-blotter-grid-r{text-align:right}
.inst-blotter-grid-row{padding:3px 2px;border-bottom:1px solid rgba(22,29,40,.7);cursor:pointer;outline:none;background-repeat:no-repeat;background-image:linear-gradient(90deg,rgba(37,224,122,.10),rgba(37,224,122,.10));background-size:var(--ib-fill,0%) 100%}
.inst-blotter-grid-row:hover{background-color:rgba(255,255,255,.03)}
.inst-blotter-grid-row[aria-selected="true"]{background-color:rgba(110,168,255,.14);box-shadow:inset 2px 0 0 #6EA8FF}
.inst-blotter-grid-row:focus-visible{box-shadow:inset 0 0 0 1px #6EA8FF}
.inst-blotter-grid-buy{color:#25E07A}
.inst-blotter-grid-sell{color:#FF5C6C}
.inst-blotter-grid-fill{text-align:right;color:#E8EDF6}
.inst-blotter-grid-avg{text-align:right}
.inst-blotter-grid-ft{display:flex;justify-content:space-between;margin-top:5px;padding-top:4px;border-top:1px solid var(--ib-line);color:#4A566C;font-size:7.5px;letter-spacing:.1em}
.inst-blotter-grid-sel{color:#8FA3C0}""",
"""var D=[['ORD-4471','MSFT','B',2500,2500,418.42],['ORD-4470','AAPL','S',1800,900,224.18],['ORD-4468','NVDA','B',600,150,121.55],['ORD-4465','TSLA','S',1200,1200,242.90],['ORD-4461','AMD','B',3000,2100,158.04]];
var rows=root.querySelector('.inst-blotter-grid-rows'),sel=root.querySelector('.inst-blotter-grid-sel');
D.forEach(function(d,i){
  var r=document.createElement('div');
  r.className='inst-blotter-grid-row';
  r.setAttribute('role','option');r.setAttribute('aria-selected','false');
  r.tabIndex=i===0?0:-1;
  r.style.setProperty('--ib-fill',(d[4]/d[3]*100)+'%');
  r.innerHTML='<span></span><span></span><span></span><span class="inst-blotter-grid-fill"></span><span class="inst-blotter-grid-avg"></span>';
  r.children[0].textContent=d[0];
  r.children[1].textContent=d[1];
  r.children[2].textContent=d[2]==='B'?'BUY':'SEL';
  r.children[2].className=d[2]==='B'?'inst-blotter-grid-buy':'inst-blotter-grid-sell';
  r.children[3].textContent=d[4].toLocaleString('en-US')+'/'+d[3].toLocaleString('en-US');
  r.children[4].textContent=d[5].toFixed(2);
  r.addEventListener('click',function(){pick(i);});
  rows.appendChild(r);
});
var all=rows.querySelectorAll('.inst-blotter-grid-row'),cur=-1;
function pick(i){
  if(cur>-1){all[cur].setAttribute('aria-selected','false');all[cur].tabIndex=-1;}
  cur=i;all[i].setAttribute('aria-selected','true');all[i].tabIndex=0;all[i].focus();
  var d=D[i];
  sel.textContent=d[0]+' · '+(d[4]===d[3]?'FILLED':'WORKING '+Math.round(d[4]/d[3]*100)+'%');
}
rows.addEventListener('keydown',function(e){
  if(e.key==='ArrowDown'){pick(Math.min(all.length-1,(cur<0?0:cur+1)));e.preventDefault();}
  if(e.key==='ArrowUp'){pick(Math.max(0,(cur<0?0:cur-1)));e.preventDefault();}
});""")

# ───────────────────────── 12 · order flow bubbles ─────────────────────────
comp("ofl-flow-bubbles", "Order Flow Bubbles", "Order Flow",
 "order flow bubbles canvas notional aggressor buy sell stream",
 "Canvas stream where every print becomes a bubble sized by the square root of notional and drifting up the tape, so a block trade is visible instantly.",
"""
<div class="ofl-flow-bubbles">
  <div class="ofl-flow-bubbles-hd"><span>ORDER FLOW</span><span class="ofl-flow-bubbles-rat"></span></div>
  <canvas class="ofl-flow-bubbles-cv"></canvas>
</div>
""",
""".ofl-flow-bubbles{width:100%;max-width:300px;background:#0B0F17;border:1px solid #1C2432;border-radius:10px;padding:8px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:8.5px;color:#5B6883;letter-spacing:.1em;font-variant-numeric:tabular-nums}
.ofl-flow-bubbles-hd{display:flex;justify-content:space-between;margin-bottom:5px}
.ofl-flow-bubbles-rat{color:#93A2BC}
.ofl-flow-bubbles-cv{width:100%;height:118px;display:block;border-radius:6px}""",
"""var cv=root.querySelector('.ofl-flow-bubbles-cv'),ctx=cv.getContext('2d');
var rat=root.querySelector('.ofl-flow-bubbles-rat');
var dpr=Math.min(window.devicePixelRatio||1,2),bs=[],buys=0,sells=0,raf=0;
function size(){var r=cv.getBoundingClientRect();cv.width=r.width*dpr;cv.height=r.height*dpr;}
size();
if(window.ResizeObserver){new ResizeObserver(size).observe(cv);}
function spawn(){
  var buy=Math.random()>0.47;
  var notional=Math.pow(10,2+Math.random()*3.2);
  bs.push({x:Math.random()*cv.width,y:cv.height+20,r:Math.sqrt(notional)/3.4*dpr,buy:buy,a:1,v:(0.35+Math.random()*0.7)*dpr});
  buy?buys++:sells++;
  var tot=buys+sells;
  rat.textContent='BUY '+Math.round(buys/tot*100)+'% / SELL '+Math.round(sells/tot*100)+'%';
  if(bs.length>60)bs.shift();
}
function frame(){
  ctx.clearRect(0,0,cv.width,cv.height);
  for(var i=bs.length-1;i>=0;i--){
    var b=bs[i];b.y-=b.v;b.a-=0.0035;
    if(b.a<=0||b.y<-40){bs.splice(i,1);continue;}
    ctx.globalAlpha=Math.max(0,b.a)*0.8;
    ctx.fillStyle=b.buy?'#25E07A':'#FF5C6C';
    ctx.beginPath();ctx.arc(b.x,b.y,b.r,0,6.283);ctx.fill();
    ctx.globalAlpha=Math.max(0,b.a);
    ctx.strokeStyle=b.buy?'#25E07A':'#FF5C6C';ctx.lineWidth=1*dpr;
    ctx.beginPath();ctx.arc(b.x,b.y,b.r,0,6.283);ctx.stroke();
  }
  ctx.globalAlpha=1;
  raf=requestAnimationFrame(frame);
}
for(var i=0;i<14;i++)spawn();
frame();
setInterval(spawn,420);""")

io.open("_handmade.json", "w", encoding="utf-8").write(json.dumps(C, ensure_ascii=False, indent=1))
print("wrote %d hand-written components" % len(C))
for c in C: print("  %-22s %s" % (c["cat"], c["name"]))
