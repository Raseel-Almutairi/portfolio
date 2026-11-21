import json, sys; sys.path.insert(0,'.')
from model import TODAY as _TD
from model import build, SH, CRIT, CSRC, TABLE1
subs,ccs,gaps,docs=build()
css=open('web.css').read()
lv=[dict(n=n,en=en,dc=dc,ex=ex) for n,en,dc,ex in TABLE1]
from official import DOMS as FULL
doms=[dict(id=k,name=v,full=FULL[k]) for k,v in SH.items()]
crit=[dict(id=c[0],lv=c[1],t=c[2],src=CSRC[c[0]]) for c in CRIT]
body=r'''<main class="wrap">
<header>
  <div class="eyebrow">Personal GRC Project · Raseel Almutairi</div>
  <h1>SAMA Cyber Security Framework Maturity Self-Assessment (Demo)</h1>
  <p class="sub">A self-assessment of the 32 subdomains of the SAMA Cyber Security Framework v1.0, using SAMA's own maturity model: each subdomain gets a level from 0 to 5, the minimum required is level 3, and every unmet criterion becomes an action.</p>
  <div class="note">Personal initiative · demo with sample data · assessment date (as of): <b>%ASOF_TXT%</b></div>
</header>
<nav class="tabs" aria-label="Views">
  <a href="#framework">1. SAMA Framework</a><a href="#controls">2. Controls &amp; Evidence</a><a href="#assessment">3. Assessment</a><a href="#plan">4. Action Plan</a><a href="#summary">5. Summary</a>
</nav>

<section class="view" id="v-framework">
  <div class="panel"><div class="ph"><h2>What is the SAMA Cyber Security Framework?</h2><p>Version 1.0 · May 2017</p></div>
    <ul class="list">
      <li><b>Issued by</b> the Saudi Central Bank (SAMA) for the organizations it regulates (Member Organizations).</li>
      <li><b>Principle-based (2.2):</b> SAMA sets principles and objectives, and lists control considerations to achieve them. If a control consideration cannot be implemented, the organization applies compensating controls, accepts the risk internally and requests a formal waiver from SAMA.</li>
      <li><b>Self-assessment (2.3):</b> the organization assesses itself with a questionnaire, and SAMA reviews and audits the result to determine compliance and maturity.</li>
      <li><b>Maturity, not pass/fail (2.4):</b> each subdomain gets a maturity level from 0 to 5. The minimum required is <b>level 3</b>.</li>
    </ul></div>
  <div class="panel"><div class="ph"><h2>Structure: 4 domains, 32 subdomains</h2><p>Each subdomain = Principle → Objective → Control considerations</p></div><div class="dgrid" id="dgrid"></div></div>
  <div class="panel"><div class="ph"><h2>Maturity Model (Table 1)</h2><p>Levels are cumulative: a level is reached only when all criteria of the lower levels are met</p></div>
    <div class="tw" style="max-height:none"><table><thead><tr><th>Level</th><th>Name</th><th>Definition and Criteria</th><th>Explanation</th></tr></thead><tbody id="levels"></tbody></table></div></div>
  <div class="panel"><div class="ph"><h2>What level 3 needs (2.4.1)</h2><p>The documentation pyramid</p></div>
    <div class="pyr">
      <div><b>Policy</b><span class="m">Why / What</span><p>Endorsed by the board. Why cyber security matters, which assets to protect, and the principles and objectives.</p></div>
      <div><b>Standards</b><span class="m">What</span><p>Which controls must be implemented (baselines), e.g. parameters, password rules, segregation of duties, back-up.</p></div>
      <div><b>Procedures</b><span class="m">How</span><p>Step-by-step how the controls are executed by staff, third parties or customers.</p></div>
      <div><b>Plus</b><span class="m">Prove · Monitor · Measure</span><p>Implementation can be demonstrated, compliance is monitored (preferably with a GRC tool), and KPIs are reported.</p></div>
    </div>
    <p style="margin:12px 0 0;color:var(--muted)"><b style="color:var(--ink)">Level 4</b> adds KRIs with thresholds and effectiveness measurement (2.4.2). <b style="color:var(--ink)">Level 5</b> adds continuous improvement, integration with enterprise risk management and comparison with peer and sector data (2.4.3).</p></div>
  <div class="panel"><div class="ph"><h2>How this tool assesses</h2></div>
    <ol class="steps">
      <li><b>Controls &amp; Evidence:</b> read what SAMA requires and the evidence needed, to support each Yes / No answer.</li>
      <li><b>Assessment:</b> answer the 14 maturity criteria (taken from Table 1 and section 2.4) with Yes or No for each subdomain.</li>
      <li>The level is the highest level whose criteria, and all lower ones, are Yes. No averaging.</li>
      <li>Every unmet criterion up to level 3 becomes an action in the Action Plan.</li>
      <li>A subdomain is <b>Not assessed</b> until all 14 criteria are answered; it is not counted as level 0.</li>
      <li>All dates (overdue, escalation, due in 30 days) are calculated from one assessment date (as of date).</li>
    </ol>
    <p style="margin:10px 0 0;color:var(--muted)">Sources: <a href="https://rulebook.sama.gov.sa/en/entiresection/3850">SAMA Rulebook - Cyber Security Framework</a> · official framework document v1.0 (May 2017).</p></div>
</section>

<section class="view" id="v-controls">
  <div class="panel"><div class="ph"><h2>Controls &amp; Evidence</h2><p>SAMA's principle, objective and control considerations (official text)</p></div>
    <p style="margin:0 0 10px;color:var(--muted);max-width:85ch">What SAMA requires in each subdomain, and the evidence that proves it. This tab is for reference only: read it first, then answer Yes / No in tab 3 (Assessment).</p>
    <div class="filters" id="cd" role="group" aria-label="Filter by domain"></div>
    <div class="qa" id="cq"></div></div>
</section>

<section class="view" id="v-assessment">
  <div class="panel"><div class="ph"><h2>Maturity Assessment by Subdomain</h2><p>Open a subdomain to see the 14 criteria (Yes / No) and why it got its level</p></div>
    <div class="filters" id="md" role="group" aria-label="Filter by domain"></div>
    <div class="filters" id="ml" role="group" aria-label="Filter by level"></div>
    <div class="qa" id="qa"></div></div>
</section>

<section class="view" id="v-plan">
  <div class="panel"><div class="ph"><h2>Action Plan to Level 3</h2><p id="gcount"></p></div>
    <p style="margin:0 0 10px;color:var(--muted);max-width:85ch">Generated automatically from the assessment: every criterion up to level 3 answered No becomes an action. Closing an action does not change the answer or the level: the criterion stays No until it is re-assessed with evidence in the Assessment. Closed actions are flagged <b>Re-assess</b>. Risk accepted actions stay unmet; their target date is the acceptance expiry date.</p>
    <div class="escm"><div class="e2"><b>1st Escalation</b><span>To: Control owner<br>CC: GRC Manager, Line Manager</span></div><div class="e3"><b>2nd Escalation</b><span>To: Line Manager<br>CC: GRC Manager, Head of Department</span></div><div class="e4"><b>3rd Escalation</b><span>To: Head of Department<br>CC: GRC Manager, CISO</span></div><div class="ra"><b>Risk accepted</b><span>Risk owner sign-off (3.2.1.3); SAMA waiver if needed (2.2)</span></div></div>
    <p style="margin:0 0 12px;color:var(--muted);font-size:12.5px">The GRC team decides when to escalate and to which stage; the next escalation is due 3 days after each escalation is sent. If an action is still open after the 3rd escalation, it is reported to the Cyber Security Committee, which monitors cyber security risks (SAMA CSF 3.1.4).</p>
    <div class="filters" id="gp" role="group" aria-label="Filter by priority"></div>
    <div class="filters" id="gs" role="group" aria-label="Filter by status"></div>
    <div class="tw"><table><thead><tr><th>ID</th><th>Subdomain</th><th>Missing criterion</th><th>Action</th><th>Owner</th><th>Priority</th><th>Target date</th><th>Status</th><th>Escalation</th><th>Email</th></tr></thead><tbody id="gt"></tbody></table></div></div>
</section>

<section class="view" id="v-summary">
  <div class="k1" id="k1"></div>
  <div class="panel"><div class="ph"><h2>Average Maturity by Domain</h2><p>Green line = target level 3</p></div><div class="hb" id="hmat"></div><div class="ax"><span></span><div><span>0</span><span>1</span><span>2</span><span>3</span><span>4</span><span>5</span></div><span></span></div></div>
  <div class="panel"><div class="ph"><h2>Domain Summary</h2><p>Target: level 3</p></div>
    <div class="tw" style="max-height:none"><table><thead><tr><th>Domain</th><th>Subdomains</th><th>Average maturity</th><th>At level 3+</th><th>Open actions</th></tr></thead><tbody id="cmp"></tbody></table></div></div>
</section>

<footer>
  <div>All answers, levels, actions, owners and dates are sample data and do not represent any organization. Principles, objectives, control considerations and Table 1 are taken verbatim from the official SAMA Cyber Security Framework v1.0; the 14 criteria are the statements of Table 1 and section 2.4. Required evidence is derived by the author from the wording of each control consideration.</div>
  <div><b style="color:var(--ink)">This tool is a personal initiative and does not replace SAMA's assessment.</b></div>
</footer>
</main>'''
js=r'''<script>
const SUBS=__SUBS__, CCS=__CCS__, GAPS=__GAPS__, CRIT=__CRIT__, LV=__LV__, DOMS=__DOMS__, T=3;
const $=s=>document.querySelector(s), esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const pct=(a,b)=>b?Math.round(a/b*1000)/10:0, avg=a=>a.length?a.reduce((x,y)=>x+y,0)/a.length:0;
const LN=LV.map(l=>l.en);
const open=GAPS.filter(g=>g.fstatus!=="Closed"&&g.fstatus!=="Risk Accepted");
const l3=CRIT.filter(c=>c.lv<=3);
const SHORT={L1a:"Controls performed",L2a:"Standardized practice",L3a:"Approved policy (why / what)",L3b:"Standards (what)",L3c:"Procedures (how)",L3d:"Implementation demonstrated",L3e:"Compliance monitored (GRC)",L3f:"KPIs reported"};
const k1=[["Average maturity",avg(SUBS.map(s=>s.level)).toFixed(1),"c-acc","of 5 · target 3"],
 ["Subdomains at level 3+",SUBS.filter(s=>s.level>=T).length+" / "+SUBS.length,"c-good",pct(SUBS.filter(s=>s.level>=T).length,SUBS.length)+"%"],
 ["Open actions",open.length,"","unmet level 3 criteria"],
 ["Overdue",open.filter(g=>g.overdue).length,"c-bad","past target date"],
 ["Closed · re-assess",GAPS.filter(g=>g.reassess).length,"","criterion still No"],
 ["Risk accepted",GAPS.filter(g=>g.fstatus==="Risk Accepted").length,"","criterion still unmet"+(GAPS.some(g=>g.ra_expired)?" · "+GAPS.filter(g=>g.ra_expired).length+" expired":"")]
];
$("#k1").innerHTML=k1.map(k=>`<div class="kpi"><span>${k[0]}</span><b class="${k[2]}">${k[1]}</b><small>${k[3]}</small></div>`).join("");
$("#hmat").innerHTML=DOMS.map(d=>{const v=avg(SUBS.filter(s=>s.dom===d.id).map(s=>s.level));return `<div class="hr"><div>${d.name}</div><div class="tr"><div class="fl" style="width:${v/5*100}%;background:${v>=T?'var(--accent)':'var(--warn)'}"></div><div class="tg" style="left:${T/5*100}%"></div></div><div class="v">${v.toFixed(1)}</div></div>`}).join("");
const cmpRow=(name,x,c,g)=>`<tr><td>${name}</td><td class="m">${x.length}</td><td class="m">${avg(x.map(y=>y.level)).toFixed(1)}</td><td class="m">${x.filter(y=>y.level>=T).length} / ${x.length}</td><td class="m">${g.length}</td></tr>`;
$("#cmp").innerHTML=DOMS.map(d=>cmpRow(d.name,SUBS.filter(s=>s.dom===d.id),CCS.filter(c=>c.dom===d.id),open.filter(g=>g.dom===d.id))).join("")+cmpRow("<b>Total</b>",SUBS,CCS,open);
function chips(el,items,get,set,cb){el.innerHTML=items.map(([v,t])=>`<button class="chip" type="button" id="${el.id}-${String(v).replace(/\s/g,'')}" data-v="${v}" aria-pressed="${get()===v}">${t}</button>`).join("");el.onclick=e=>{const b=e.target.closest("button");if(!b)return;set(b.dataset.v);el.querySelectorAll("button").forEach(x=>x.setAttribute("aria-pressed",x.dataset.v===b.dataset.v));cb()}}
const domChips=[["all","All domains"],...DOMS.map(d=>[d.id,d.name])];
let md="all",mlv="all";
chips($("#md"),domChips,()=>md,v=>md=v,rq);
chips($("#ml"),[["all","All levels"],["below","Below target"],["at","At target"],["0","L0"],["1","L1"],["2","L2"],["3","L3"],["4","L4"],["5","L5"]],()=>mlv,v=>mlv=v,rq);
function explain(s){const L=s.level, nxt=CRIT.filter(c=>c.lv===L+1&&s.ans[c.id]!=="Yes");
 if(L>=5) return "All criteria up to level 5 are met.";
 return `Level ${L} (${LN[L]}) because all criteria up to level ${L} are met. Level ${L+1} is not reached because ${nxt.length} of its criteria ${nxt.length===1?"is":"are"} not met: ${nxt.map(c=>c.id).join(", ")}.`+(L<T?` Closing the gaps up to level 3 is the remediation plan.`:"")}
const ccOf=s=>CCS.filter(c=>c.sid===s.sid);
function grpRow(s,c,p,n){if(!c.grp||(p&&p.grp===c.grp))return "";const g=s.subsec.find(x=>x.id===c.grp);
 return `<tr class="sg"><td colspan="${n}"><b><span class="dn">${g.id}</span> ${esc(g.name)}</b><div><i>Principle:</i> ${esc(g.pr)}</div><div><i>Objective:</i> ${esc(g.ob)}</div></td></tr>`}
const stc=s=>s==="N/A"?"NA":s.split(" ")[0];
function rq(){const a=SUBS.filter(s=>(md==="all"||s.dom===md)&&(mlv==="all"||(mlv==="below"?s.level<T:mlv==="at"?s.level>=T:s.level===+mlv)));
 $("#qa").innerHTML=a.map(s=>{const g=open.filter(x=>x.sid===s.sid).length;
  const groups=[1,2,3,4,5].map(L=>{const cs=CRIT.filter(c=>c.lv===L);const got=cs.every(c=>s.ans[c.id]==="Yes")&&L<=s.level;
   return `<div class="lvg"><div class="h${got?' got':''}">Level ${L}${got?' ✓':''}</div><div>${cs.map(c=>`<div class="cr"><span><span class="dn">${c.id}</span> ${esc(c.t)}<span class="evr">${s.ans[c.id]==="Yes"?"Evidence":"Justification"}: ${s.ev[c.id]?esc(s.ev[c.id]):"—"}</span></span><span class="yn ${s.ans[c.id]}">${s.ans[c.id]}</span></div>`).join("")}</div></div>`}).join("");
  return `<details class="qs"><summary><span class="sid">${s.sid}</span><span class="nm"><b>${esc(s.sub)}</b><small>${esc(s.domain)} · ${esc(s.owner)} · 14 maturity criteria</small></span><span class="gp" style="color:var(--muted);font-size:12.5px">${g?g+' open action'+(g>1?'s':''):''}</span><span class="lvbadge ${s.level>=T?'ok':'low'}">Level ${s.level} · ${LN[s.level]}</span></summary>
  <div class="qb">
   <div class="sh">Maturity assessment</div>
   <div class="res">${explain(s)}</div>${groups}${acts(s)}</div></details>`}).join("")}
function acts(s){const a=GAPS.filter(g=>g.sid===s.sid);if(!a.length)return `<div class="sh" style="margin-top:14px">Actions</div><p style="margin:0;color:var(--muted)">No actions: this subdomain meets level 3.</p>`;
 return `<div class="sh" style="margin-top:14px">Actions generated from the No answers (${a.length})</div><div class="tw" style="max-height:none"><table><thead><tr><th>ID</th><th>Missing criterion</th><th>Action</th><th>Closure evidence</th><th>Priority</th><th>Target date</th><th>Status</th></tr></thead><tbody>${a.map(g=>`<tr><td class="m">${g.gid}</td><td title="${esc(g.ctext)}"><span class="dn">${g.crit}</span> ${SHORT[g.crit]}</td><td>${esc(g.action)}</td><td>${esc(g.closure)}</td><td><span class="st ${g.priority}">${g.priority}</span></td><td class="m">${g.due}</td><td><span class="st ${g.fstatus.replace(' ','')}">${g.fstatus}</span>${flags(g)}</td></tr>`).join("")}</tbody></table></div><p style="margin:6px 0 0;color:var(--muted);font-size:12.5px">All actions are also listed in tab 4 (Action Plan).</p>`}
rq();
let cdm="all";
chips($("#cd"),domChips,()=>cdm,v=>cdm=v,rcc);
function rcc(){const a=SUBS.filter(s=>cdm==="all"||s.dom===cdm);
 $("#cq").innerHTML=a.map(s=>{const c=ccOf(s);
  return `<details class="qs"><summary><span class="sid">${s.sid}</span><span class="nm"><b>${esc(s.sub)}</b><small>${esc(s.domain)} · ${c.length} control considerations${s.subsec.length?' · '+s.subsec.length+' sub-sections':''}</small></span><span></span><span></span></summary>
  <div class="qb"><div class="ctl"><div class="cl"><b>Principle</b>${esc(s.pr)}</div><div class="cl"><b>Objective</b>${esc(s.ob)}</div></div>
  <div class="tw" style="max-height:none"><table><thead><tr><th>No.</th><th>Control consideration</th><th>Required evidence</th></tr></thead><tbody>${c.map((x,i,arr)=>grpRow(s,x,arr[i-1],3)+`<tr><td class="m">${x.ccid}</td><td class="ft">${esc(x.text)}</td><td style="color:var(--muted)">${esc(x.ev)}</td></tr>`).join("")}</tbody></table></div></div></details>`}).join("")}
rcc();
let gp="all",gs="all";
chips($("#gp"),[["all","All priorities"],["High","High"],["Medium","Medium"]],()=>gp,v=>gp=v,rg);
chips($("#gs"),[["all","All statuses"],["Open","Open"],["In Progress","In progress"],["Closed","Closed"],["Risk Accepted","Risk accepted"],["overdue","Overdue"],["reassess","Re-assess"]],()=>gs,v=>gs=v,rg);
const TODAY="%TODAY%";
function flags(g){return (g.overdue?'<span class="st od">Overdue '+g.days+'d</span>':'')+(g.reassess?'<span class="st rs">Re-assess</span>':'')+(g.ra_expired?'<span class="st od">Acceptance expired</span>':'')}
const TO={"1st Escalation":["[Control owner email]","[GRC Manager]; [Line Manager]"],"2nd Escalation":["[Line Manager email]","[GRC Manager]; [Head of Department]"],"3rd Escalation":["[Head of Department email]","[GRC Manager]; [CISO]"],"":["[Control owner email]","-"]};
function mail(g){const e=g.esc||"",t=TO[e];
 const greet=e==="2nd Escalation"?" Line Manager":e==="3rd Escalation"?" Head of Department":" team";
 return ["To: "+t[0],"CC: "+t[1],"Subject: SAMA CSF Action "+g.gid+" - "+(e||"Reminder"),"",
 "Dear "+g.owner+greet+",","",
 (e?"This action has been escalated ("+e+")":"This is a reminder about the following action")+" from the SAMA Cyber Security Framework self-assessment:","",
 "- Action ID: "+g.gid,"- Subdomain: "+g.sid+" "+g.sub,"- Missing criterion: "+g.crit+" - "+g.ctext,"- Required action: "+g.action,"- Closure evidence: "+g.closure,
 "- Action owner: "+g.owner,"- Target date: "+g.due,"- Current status: "+g.fstatus+(g.overdue?" ("+g.days+" days overdue)":""),
 ...(e&&e!=="3rd Escalation"?["- Next escalation: "+g.nextd+" if there is no update"]:[]),...(e==="3rd Escalation"?["- Next step: the action will be reported to the Cyber Security Committee"]:[]),"",
 "Please share an update on the progress, or send the closure evidence if the action is completed. If the action cannot be completed, please let us know so the risk can be formally accepted by the risk owner.","","Thank you,","[Your name]","GRC"].join("\n")}
function mailBox(g){return (g.fstatus==="Closed"||g.fstatus==="Risk Accepted")?'—':'<details class="em"><summary>View email</summary><pre>'+esc(mail(g))+'</pre></details>'}
const escc=e=>e.startsWith("3rd")?"e4":e.startsWith("2nd")?"e3":e.startsWith("1st")?"e2":"e0";
const ESCR={"1st Escalation":"To: Control owner · CC: GRC Manager, Line Manager","2nd Escalation":"To: Line Manager · CC: GRC Manager, Head of Department","3rd Escalation":"To: Head of Department · CC: GRC Manager, CISO"};
function rg(){const a=GAPS.filter(g=>(gp==="all"||g.priority===gp)&&(gs==="all"||(gs==="overdue"?g.overdue:gs==="reassess"?g.reassess:g.fstatus===gs)));
 $("#gt").innerHTML=a.map(g=>`<tr><td class="m">${g.gid}</td><td><span class="dn">${g.sid}</span> ${esc(g.sub)}</td><td title="${esc(g.ctext)}"><span class="dn">${g.crit}</span> ${SHORT[g.crit]}</td><td>${esc(g.action)}</td><td>${esc(g.owner)}</td><td><span class="st ${g.priority}">${g.priority}</span></td><td class="m">${g.due}</td><td><span class="st ${g.fstatus.replace(' ','')}">${g.fstatus}</span>${flags(g)}</td><td class="esc ${escc(g.esc)}">${g.esc?esc(g.esc)+'<small>'+ESCR[g.esc].replace(' · ','<br>')+'<br>Sent: '+g.escd+'<br>Next: '+(g.nextd==="Report to Committee"?"Report to Committee":g.nextd+(g.nextd<=TODAY?' (due now)':''))+'</small>':(g.fstatus==="Risk Accepted"?'Risk accepted<small>'+esc(g.ra)+'</small>':'—')}</td><td>${mailBox(g)}</td></tr>`).join("");
 $("#gcount").textContent=`${a.length} of ${GAPS.length} actions`}
rg();
$("#dgrid").innerHTML=DOMS.map(d=>{const x=SUBS.filter(s=>s.dom===d.id);return `<div class="dc"><div class="dh"><span class="dn">${d.id}</span> ${esc(d.full)} <small>${x.length} subdomains</small></div><ul>${x.map(s=>`<li><span class="dn">${s.sid}</span> ${esc(s.sub)}</li>`).join("")}</ul></div>`}).join("");
$("#levels").innerHTML=LV.map(l=>`<tr class="${l.n===T?'min':''}"><td class="m" style="font-size:18px;color:var(--accent)">${l.n}</td><td><b>${l.en}</b></td><td><ul class="bl">${l.dc.map(x=>`<li>${esc(x)}</li>`).join("")}</ul></td><td><ul class="bl">${l.ex.map(x=>`<li>${esc(x)}</li>`).join("")}</ul></td></tr>`).join("");
const V=["framework","controls","assessment","plan","summary"];
function show(){const h=location.hash.replace("#","");const v=V.includes(h)?h:"framework";V.forEach(x=>$("#v-"+x).classList.toggle("on",x===v));document.querySelectorAll(".tabs a").forEach(a=>a.setAttribute("aria-current",a.getAttribute("href")==="#"+v?"page":"false"))}
window.addEventListener("hashchange",show);show();
</script>'''
html='<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>SAMA CSF Maturity Self-Assessment Tool</title>\n<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; script-src \'unsafe-inline\'; img-src data:; base-uri \'none\'; form-action \'none\'">\n'+css+'\n</head>\n<body>\n'+body+'\n'+js+'\n</body>\n</html>'
for k,v in {"__SUBS__":subs,"__CCS__":ccs,"__GAPS__":gaps,"__CRIT__":crit,"__LV__":lv,"__DOMS__":doms}.items():
    html=html.replace(k,json.dumps(v,ensure_ascii=False))
html=html.replace("%TODAY%",_TD.isoformat()).replace("%ASOF_TXT%",_TD.strftime("%d %B %Y").lstrip("0")); open("../index.html","w").write(html); print(len(html))
