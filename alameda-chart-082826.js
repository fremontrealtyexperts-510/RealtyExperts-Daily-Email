var data = [{"name":"Fremont","x":["CO","DE","TH","Active All","New","CS","PEND"],"y":[85,130,35,250,22,41,99]},{"name":"Union City","x":["CO","DE","TH","Active All","New","CS","PEND"],"y":[12,37,4,53,3,5,18]},{"name":"Castro Valley","x":["CO","DE","TH","Active All","New","CS","PEND"],"y":[6,40,7,53,6,8,34]},{"name":"Danville","x":["CO","DE","TH","Active All","New","CS","PEND"],"y":[16,102,14,132,17,10,46]},{"name":"Hayward","x":["CO","DE","TH","Active All","New","CS","PEND"],"y":[53,107,25,185,17,15,71]},{"name":"Livermore","x":["CO","DE","TH","Active All","New","CS","PEND"],"y":[38,108,12,158,17,11,58]},{"name":"Newark","x":["CO","DE","TH","Active All","New","CS","PEND"],"y":[16,45,11,72,10,8,39]},{"name":"Pleasanton","x":["CO","DE","TH","Active All","New","CS","PEND"],"y":[19,68,20,107,10,6,41]},{"name":"San Ramon","x":["CO","DE","TH","Active All","New","CS","PEND"],"y":[44,82,19,145,10,9,45]},{"name":"Dublin","x":["CO","DE","TH","Active All","New","CS","PEND"],"y":[52,73,14,139,10,21,49]},{"name":"San Leandro","x":["CO","DE","TH","Active All","New","CS","PEND"],"y":[8,55,6,69,16,6,27]},{"name":"Milpitas","x":["CO","DE","TH","Active All","New","CS","PEND"],"y":[32,19,34,85,2,27,31]}];
var baseLayout = {};
var chartMeta = {"dateLabel":"August 28, 2026"};
(function(){
var root=document.getElementById('chart');
if(!root)return;
var LABEL={'Active All':'Active All','New':'New','CS':'Coming Soon','PEND':'Pending','DE':'Detached','CO':'Condo','TH':'Townhouse'};
var SUB={'Active All':'total active listings','New':'new listings','CS':'coming soon listings','PEND':'pending sales','DE':'active detached homes','CO':'active condos','TH':'active townhouses'};
var GROUPS=[{label:'Market status',cats:['Active All','New','CS','PEND']},{label:'Active by home type',cats:['DE','CO','TH']}];
var FLAGSHIP='Fremont';
var css=''+
'#chart .rr-wrap{max-width:640px;margin:0 auto;}'+
'#chart .rr-title{font-family:var(--serif,Georgia,serif);font-size:19px;font-weight:700;color:var(--ink,#2E2E2E);text-align:center;margin:8px 0 2px;letter-spacing:-0.01em;}'+
'#chart .rr-sub{font-family:var(--sans,Arial,sans-serif);font-size:12.5px;color:var(--muted,#6B6459);text-align:center;margin:0 0 14px;}'+
'#chart .rr-groups{display:flex;flex-wrap:wrap;gap:10px 26px;justify-content:center;margin:0 0 16px;}'+
'#chart .rr-group-label{font-family:var(--sans,Arial,sans-serif);font-size:10px;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;color:var(--muted,#6B6459);margin:0 0 6px;}'+
'#chart .rr-chips{display:flex;flex-wrap:wrap;gap:8px;}'+
'#chart .rr-chip{min-height:44px;padding:10px 14px;border-radius:9px;border:1px solid var(--hairline,#E8E4DA);background:#FFFFFF;color:var(--ink-soft,#4A4640);font-family:var(--sans,Arial,sans-serif);font-size:13px;font-weight:600;line-height:1.15;cursor:pointer;}'+
'#chart .rr-chip[aria-pressed="true"]{background:var(--gold,#D4AF37);border-color:var(--gold-dark,#B08C1E);color:#2E2E2E;font-weight:700;}'+
'#chart .rr-chip:focus-visible{outline:2px solid var(--gold-dark,#B08C1E);outline-offset:2px;}'+
'#chart .rr-rows{list-style:none;margin:0;padding:0;}'+
'#chart .rr-rows li{display:grid;grid-template-columns:100px 1fr 46px;gap:8px;align-items:center;min-height:29px;padding:0;margin:0;}'+
'#chart .rr-city{font-family:var(--sans,Arial,sans-serif);font-size:12px;color:var(--ink-soft,#4A4640);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;text-align:left;}'+
'#chart li.rr-flag .rr-city{font-weight:700;color:var(--ink,#2E2E2E);}'+
'#chart .rr-track{height:16px;background:var(--track,#F2EFE7);border-radius:3px;overflow:hidden;}'+
'#chart .rr-fill{display:block;height:100%;width:0;background:var(--gold-dark,#B08C1E);border-radius:3px;transition:width 0.32s cubic-bezier(0.22,1,0.36,1);}'+
'#chart li.rr-flag .rr-fill{background:var(--gold,#D4AF37);box-shadow:inset 0 0 0 1px var(--gold-dark,#B08C1E);}'+
'#chart .rr-val{font-family:var(--serif,Georgia,serif);font-size:14px;font-weight:600;color:var(--ink,#2E2E2E);text-align:right;font-variant-numeric:tabular-nums;}'+
'#chart .rr-note{font-family:var(--sans,Arial,sans-serif);font-size:11.5px;color:var(--muted,#6B6459);line-height:1.55;margin:16px auto 4px;max-width:560px;text-align:center;}'+
'@media (max-width:599px){#chart .rr-rows li{grid-template-columns:88px 1fr 40px;}#chart .rr-groups{justify-content:flex-start;gap:12px 18px;}}'+
'@media (prefers-reduced-motion:reduce){#chart .rr-fill{transition:none;}}';
function el(tag,cls){var n=document.createElement(tag);if(cls)n.className=cls;return n;}
function valueOf(series,cat){var i=series.x.indexOf(cat);return i>=0?(Number(series.y[i])||0):0;}
while(root.firstChild){root.removeChild(root.firstChild);}
var style=document.createElement('style');
style.textContent=css;
var wrap=el('div','rr-wrap');
var title=el('div','rr-title');
title.textContent='Real Estate Inventory by City';
var sub=el('p','rr-sub');
sub.setAttribute('aria-live','polite');
var groups=el('div','rr-groups');
var buttons=[];
GROUPS.forEach(function(g){
var box=el('div','rr-group');
var lab=el('div','rr-group-label');
lab.textContent=g.label;
var chips=el('div','rr-chips');
g.cats.forEach(function(cat){
var b=el('button','rr-chip');
b.type='button';
b.textContent=LABEL[cat];
b.setAttribute('data-cat',cat);
b.setAttribute('aria-pressed','false');
b.addEventListener('click',function(){update(cat);});
chips.appendChild(b);
buttons.push(b);
});
box.appendChild(lab);
box.appendChild(chips);
groups.appendChild(box);
});
var rows=document.createElement('ol');
rows.className='rr-rows';
var rowByCity={};
data.forEach(function(d){
var li=document.createElement('li');
if(d.name===FLAGSHIP)li.className='rr-flag';
var c=el('span','rr-city');
c.textContent=d.name;
var t=el('span','rr-track');
t.setAttribute('aria-hidden','true');
var f=el('span','rr-fill');
t.appendChild(f);
var v=el('span','rr-val');
li.appendChild(c);li.appendChild(t);li.appendChild(v);
rows.appendChild(li);
rowByCity[d.name]={li:li,fill:f,val:v};
});
var note=el('p','rr-note');
note.textContent='Active All is Detached plus Condo plus Townhouse. Pending and Coming Soon are counted separately. Source: REALTY EXPERTS\u00AE MLS export, '+(chartMeta.dateLabel||'')+'.';
wrap.appendChild(title);wrap.appendChild(sub);wrap.appendChild(groups);wrap.appendChild(rows);wrap.appendChild(note);
root.appendChild(style);root.appendChild(wrap);
function update(cat){
buttons.forEach(function(b){b.setAttribute('aria-pressed',String(b.getAttribute('data-cat')===cat));});
var list=data.map(function(d,i){return {city:d.name,v:valueOf(d,cat),i:i};}).sort(function(a,b){return b.v-a.v||a.i-b.i;});
var max=1;
list.forEach(function(r){if(r.v>max)max=r.v;});
sub.textContent='All 12 cities, ranked by '+SUB[cat]+'. Tap a category to re-rank.';
rows.setAttribute('aria-label','Cities ranked by '+LABEL[cat]+' count, highest first');
list.forEach(function(r){
var n=rowByCity[r.city];
n.val.textContent=String(r.v);
n.fill.style.width=(r.v/max*100).toFixed(1)+'%';
rows.appendChild(n.li);
});
}
update('Active All');
})();
(function(){
var open=null;
function close(){if(open){if(open.parentNode){open.parentNode.removeChild(open);}open=null;document.body.style.overflow='';}}
function show(src,alt){close();var o=document.createElement('div');o.className='re-lightbox';o.setAttribute('role','dialog');o.setAttribute('aria-modal','true');o.setAttribute('aria-label',alt||'Enlarged image');var im=document.createElement('img');im.src=src;im.alt=alt||'';var x=document.createElement('span');x.className='re-lightbox-close';x.setAttribute('aria-hidden','true');x.textContent='\u00D7';o.appendChild(im);o.appendChild(x);document.body.appendChild(o);document.body.style.overflow='hidden';open=o;}
document.addEventListener('click',function(e){if(open){var t=e.target;if(t===open||(t&&t.className&&String(t.className).indexOf('re-lightbox-close')>-1)){close();}return;}var t2=e.target;if(t2&&t2.tagName==='IMG'&&t2.closest&&t2.closest('.newsletter-container')){e.preventDefault();show(t2.currentSrc||t2.src,t2.alt);}});
document.addEventListener('keydown',function(e){if(e.key==='Escape'||e.keyCode===27){close();}});
})();