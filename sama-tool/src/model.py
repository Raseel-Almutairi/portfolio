import sys; sys.path.insert(0,'.')
from datetime import date, timedelta
from data import D, ROWS, LEVELS
from official import ITEMS, EV as EVCC, PO, SUBSEC, CRIT as OCRIT, TABLE1
SH={'3.1':'Leadership & Governance','3.2':'Risk Management & Compliance','3.3':'Operations & Technology','3.4':'Third Party'}
# Sample data is pinned to one assessment date (as of date) so the web and Excel show the same numbers.
AS_OF=date(2026,11,18)
TODAY=AS_OF
# Maturity criteria per level, from SAMA CSF section 2.4 (paraphrased)
CRIT=[(c,l,t) for c,l,t,_ in OCRIT]
CSRC={c:src for c,_,_,src in OCRIT}
ACT={"L1a":("Start basic control activities for this subdomain.","Records of the activities performed"),
 "L2a":("Standardize how the control is performed so it is repeated the same way.","Consistent records over at least two cycles"),
 "L3a":("Write the policy and get board or committee approval.","Approved policy with approval record"),
 "L3b":("Define the standard (baseline controls) and approve it.","Approved standard"),
 "L3c":("Document the step-by-step procedure and approve it.","Approved procedure"),
 "L3d":("Collect and keep evidence that the control is implemented.","Evidence pack (records, configurations, reports)"),
 "L3e":("Set up periodic compliance monitoring, preferably in a GRC tool.","Compliance monitoring reports"),
 "L3f":("Define KPIs, track them and report them to the committee.","KPI reports"),
 # used only when a subdomain's target is raised above the minimum level 3
 "L4a":("Assess the effectiveness of the controls periodically and improve them when needed.","Effectiveness assessment reports and improvement records"),
 "L4b":("Define KRIs with thresholds and trend reporting for the controls.","KRI reports with thresholds and trends"),
 "L4c":("Document the periodic measurements, evaluations and improvement opportunities.","Documented evaluation and improvement records"),
 "L5a":("Put the controls under a continuous improvement plan.","Approved continuous improvement plan and progress records"),
 "L5b":("Integrate the controls with the enterprise risk management framework.","Risk management records that include the cyber security controls"),
 "L5c":("Evaluate the performance of the controls against peer and sector data.","Benchmarking reports using peer or sector data")}
CRITICAL={"3.3.5","3.3.12","3.3.13","3.3.15","3.3.17","3.3.9"}
NA_SET={("3.3.10",4),("3.1.6",7),("3.4.3",4)}
def answers(sid,L,k):
    a={}
    for cid,lv,_ in CRIT:
        if lv<=L: a[cid]="Yes"
        elif lv==L+1:
            # partially toward next level: some criteria met
            idx="abcdef".index(cid[2])
            a[cid]="Yes" if (idx+k)%3==0 else "No"
        else: a[cid]="No"
    # ensure the next level is NOT fully met
    nxt=[c for c,lv,_ in CRIT if lv==L+1]
    if nxt and all(a[c]=="Yes" for c in nxt): a[nxt[-1]]="No"
    return a
def level_of(a):
    lvl=0
    for L in range(1,6):
        if all(a[c]=="Yes" for c,lv,_ in CRIT if lv==L): lvl=L
        else: break
    return lvl
ADDR={"I":"Addressed","P":"Partially addressed","N":"Not addressed"}
EVT={"L1a":"Activity records for {sub}","L2a":"Records showing the same practice repeated (last 2 cycles)",
 "L3a":"POL-{c} {sub} section of the Cyber Security Policy, board approved","L3b":"STD-{c} {sub} Standard, approved",
 "L3c":"PRC-{c} {sub} Procedure, approved","L3d":"EVD-{c} implementation evidence pack (records, configurations)",
 "L3e":"GRC compliance monitoring report, latest quarter","L3f":"KPI report to the cyber security committee, latest quarter",
 "L4a":"Annual effectiveness assessment report","L4b":"KRI report with thresholds and trend","L4c":"Improvement log with measurement results",
 "L5a":"Continuous improvement plan","L5b":"ERM risk register entries for {sub}","L5c":"Peer / sector benchmarking report"}
EVN={"L1a":"No records of control activities found","L2a":"Practice differs between teams; no consistent records",
 "L3a":"Policy section missing or not approved by the board","L3b":"No approved standard; only informal settings",
 "L3c":"Procedure not documented or not approved","L3d":"Implementation cannot be demonstrated with records",
 "L3e":"No compliance monitoring performed","L3f":"No KPIs defined or reported",
 "L4a":"No effectiveness assessment performed","L4b":"No KRIs or thresholds defined","L4c":"Measurements and improvements not documented",
 "L5a":"No continuous improvement plan","L5b":"Not integrated with the ERM framework","L5c":"No peer or sector benchmarking"}
def act_text(sub,cid):
    return sub+": "+ACT[cid][0]
def action_for(sid, sub, cid):
    """Action, closure evidence and the control considerations it covers (FIX-12).
    The assessment stays per criterion; each action is linked to the control considerations of its subdomain,
    and the 'implementation can be demonstrated' action (L3d) lists the required evidence per control consideration."""
    ids = [it["ccid"] for it in ITEMS[sid]]
    rng = ", ".join(ids) if len(ids) <= 4 else f"{ids[0]} to {ids[-1]} ({len(ids)} control considerations)"
    act = f"{sub}: {ACT[cid][0]} Covers {rng}."
    clos = ACT[cid][1]
    if cid == "L3d":
        if len(ids) <= 6:
            clos = "Evidence per control consideration: " + "; ".join(f"{i} - {e}" for i, e in zip(ids, EVCC[sid]))
        else:
            clos = f"Evidence for each control consideration {ids[0]} to {ids[-1]}, as listed in sheet 2 (Controls & Evidence)"
    return act, clos, ids
def evid(sid, sub, cid, ans):
    if ans == "Yes": return EVT[cid].format(sub=sub, c=sid.replace(".", ""))
    if ans == "No": return "Gap: " + EVN[cid]
    return ""

def build():
    subs=[]; ccs=[]; gaps=[]; docs=[]; g=0
    for k,r in enumerate(ROWS):
        sid,name,ar,L,owner=r[:5]; owner={'CISO':'Cyber Security'}.get(owner,owner); dom=sid.rsplit('.',1)[0]
        a=answers(sid,L,k); lvl=level_of(a)
        subs.append(dict(sid=sid,sub=name,dom=dom,domain=SH[dom],owner=owner,ans=a,ev={c:evid(sid,name,c,a[c]) for c in a},level=lvl,pr=PO[sid][0],ob=PO[sid][1],subsec=SUBSEC.get(sid,[])))
        # Controls are reference only (what SAMA requires + required evidence); they carry no status of their own.
        for i,it in enumerate(ITEMS[sid],1):
            ccs.append(dict(sid=sid,sub=name,dom=dom,domain=SH[dom],ccid=it["ccid"],grp=it["grp"],text=it["text"],owner=owner,ev=EVCC[sid][i-1]))
            docs.append(dict(sid=sid,sub=name,dom=dom,ccid=it["ccid"],doc=EVCC[sid][i-1]))
        if lvl<3:
            for cid,lv,txt in CRIT:
                if lv<=3 and a[cid]=="No":
                    g+=1
                    pr="High" if (lv<=2 or sid in CRITICAL) else "Medium"
                    due=TODAY+timedelta(days=((g*41)%330)-60)
                    fs="Closed" if g%10==0 else ("In Progress" if g%3==0 else "Open")
                    act,clos,ccids_=action_for(sid,name,cid)
                    gaps.append(dict(ccids=ccids_,gid=f"{sid}-{cid}",n=g,sid=sid,sub=name,dom=dom,domain=SH[dom],crit=cid,clevel=lv,ctext=txt,cur=lvl,action=act,closure=clos,owner=owner,priority=pr,due=due.isoformat(),fstatus=fs,overdue=(fs!="Closed" and due<TODAY),due30=(fs!="Closed" and TODAY<=due<=TODAY+timedelta(days=30))))
    # sample showcase: one action escalated to the committee, one risk accepted
    from datetime import date as _d
    gaps[0]["due"] = (TODAY - timedelta(days=75)).isoformat()
    ra = next(x for x in gaps if x["fstatus"] == "Open" and not x["overdue"] and x["priority"] == "Medium" and x["sid"] != gaps[0]["sid"])
    ra["fstatus"] = "Risk Accepted"; ra["ra"] = "RA-2026-004"
    for x in gaps:
        d = _d.fromisoformat(x["due"]); done = x["fstatus"] in ("Closed", "Risk Accepted")
        x["overdue"] = (not done) and d < TODAY; x["days"] = (TODAY - d).days if x["overdue"] else 0
        x["due30"] = (not done) and TODAY <= d <= TODAY + timedelta(days=30)
        x.setdefault("ra", "")
        # Closing an action does not change the answer: the criterion stays No until it is re-assessed.
        x["reassess"] = x["fstatus"] == "Closed"
        # Risk accepted: the criterion stays unmet; the target date is the acceptance expiry date.
        x["ra_expired"] = x["fstatus"] == "Risk Accepted" and d < TODAY
        # sample: the escalation stage is chosen by the GRC team; here it follows how long the action is overdue
        if x["fstatus"] in ("Closed", "Risk Accepted") or not x["overdue"]: x["esc"] = ""
        elif x["days"] > 60: x["esc"] = "3rd Escalation"
        elif x["days"] > 30: x["esc"] = "2nd Escalation"
        else: x["esc"] = "1st Escalation"
        # sample escalation dates: stages sent every 3 days after the target date was missed
        n_ = {"1st Escalation": 1, "2nd Escalation": 2, "3rd Escalation": 3}.get(x["esc"], 0)
        x["escd"] = (TODAY - timedelta(days=(x["n"] % 5))).isoformat() if n_ else ""
        x["nextd"] = ("Report to Committee" if n_ == 3 else (_d.fromisoformat(x["escd"]) + timedelta(days=3)).isoformat()) if n_ else ""
    return subs,ccs,gaps,docs
if __name__=="__main__":
    s,c,g,d=build()
    from collections import Counter
    print(Counter(x['level'] for x in s),[ (x['sid'],x['level']) for x in s if x['level']!=dict((r[0],r[3]) for r in ROWS)[x['sid']]])
    print(len(c),len(g),sum(x['fstatus']!='Closed' for x in g),sum(x['overdue'] for x in g),Counter(x['priority'] for x in g))
