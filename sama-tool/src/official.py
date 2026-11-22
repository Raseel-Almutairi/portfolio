# Official SAMA CSF v1.0 text (extracted verbatim from the official PDF) mapped to the 32 assessed subdomains.
# Risk management sub-sections 3.2.1.1 to 3.2.1.4 are kept under 3.2.1 as groups.
import json, os
from evcc import E as OLD_EV
_d = json.load(open(os.path.join(os.path.dirname(__file__), "sama_official.json"), encoding="utf-8"))
DOMS = _d["doms"]
SECS = {s["id"]: s for s in _d["secs"]}

NEW_EV = {
"3.2.1": ["Approved cyber security risk management process (methodology)",
 "Risk methodology showing CIA-based impact criteria",
 "Mapping of the cyber risk process to the enterprise risk management (ERM) framework",
 "Risk methodology sections for identification, analysis, response and monitoring",
 "Risk assessment scope covering business processes, applications and infrastructure",
 "Risk assessments for projects, critical changes, outsourcing and new products",
 "Periodic risk assessment schedule and reports based on classification or risk profile",
 "Risk workshop attendance (business owners, IT, cyber security, key users)",
 "Risk assessment reports sent to the risk owners",
 "Risk owner sign-off and endorsement of the assessment results",
 "Board or committee approved risk appetite and risk tolerance statement",
 "Risk identification records for each assessment",
 "Central cyber security risk register",
 "Register entries listing assets, threats, vulnerabilities and existing controls",
 "Risk analysis worksheets with impact and likelihood ratings",
 "Risk scoring matrix (impact x likelihood) applied to each risk",
 "Treatment decisions aligned with the approved risk appetite",
 "Documented treatment options for each risk (accept, avoid, transfer, mitigate)",
 "Risk acceptance forms signed by the business owner and reported to the committee",
 "Business owner decisions to cancel or postpone high-risk activities",
 "Risk transfer agreements (e.g., insurance, contracts) accepted by the receiving party",
 "Control selection records with cost, feasibility and compliance review, and signed residual risk",
 "Approved risk treatment plan with owners and due dates",
 "Treatment plan progress reports to the committee",
 "Control effectiveness review reports for new or revised controls"],
"3.3.5": ["Approved identity and access management policy with responsibilities",
 "IAM compliance monitoring reports",
 "IAM effectiveness KPIs (e.g., orphan accounts, overdue access reviews)",
 "HR-driven joiner/mover/leaver records, approved access requests, periodic access reviews, audit trail, MFA configuration and privileged access review records"],
"3.3.8": ["Approved infrastructure security standards",
 "Infrastructure compliance reports (e.g., configuration compliance scans)",
 "Infrastructure security effectiveness KPIs",
 "Standard scope covering main data centers, DR sites and offices",
 "Standard scope covering all infrastructure types (servers, VMs, firewalls, network devices, etc.)",
 "Hardening baselines, network segmentation design, malware/APT protection, patch reports, DDoS protection and backup test records"],
"3.3.12": ["SARIE Information Security Policy compliance evidence",
 "mada Rules and Standards (Part IIIa, Part IIIb) and SAMA CA IPK compliance evidence"],
"3.3.13": ["Approved electronic banking services cyber security standard",
 "E-banking compliance monitoring reports",
 "E-banking control effectiveness KPIs",
 "Brand protection and takedown records, MFA configuration, ATM/POS hardening and anti-skimming evidence, SMS notification configuration and SAMA approvals for new services"],
}

def _items(sid):
    ids = [sid] + (["3.2.1.1", "3.2.1.2", "3.2.1.3", "3.2.1.4"] if sid == "3.2.1" else [])
    out = []
    for gid in ids:
        s = SECS[gid]
        for i, t in enumerate(s["cc"], 1):
            out.append(dict(ccid=f"{gid}.{i}", text=t, grp=None if gid == sid else gid))
    return out

ITEMS = {sid: _items(sid) for sid in SECS if sid.count(".") == 2}
PO = {sid: (SECS[sid]["pr"], SECS[sid]["ob"]) for sid in ITEMS}
SUBSEC = {"3.2.1": [dict(id=g, name=SECS[g]["name"], pr=SECS[g]["pr"], ob=SECS[g]["ob"]) for g in ("3.2.1.1", "3.2.1.2", "3.2.1.3", "3.2.1.4")]}
EV = {sid: NEW_EV.get(sid, OLD_EV.get(sid)) for sid in ITEMS}
for sid in ITEMS:
    assert len(EV[sid]) == len(ITEMS[sid]), (sid, len(EV[sid]), len(ITEMS[sid]))

# SAMA CSF Table 1 - Cyber Security Maturity Model (verbatim)
TABLE1 = [
 (0, "Non-existent", ["No documentation.", "There is no awareness or attention for certain cyber security control."],
  ["Cyber security controls are not in place. There may be no awareness of the particular risk area or no current plans to implement such cyber security controls."]),
 (1, "Ad-hoc", ["Cyber security controls is not or partially defined.", "Cyber security controls are performed in an inconsistent way.", "Cyber security controls are not fully defined."],
  ["Cyber security control design and execution varies by department or owner.", "Cyber security control design may only partially mitigate the identified risk and execution may be inconsistent."]),
 (2, "Repeatable but informal", ["The execution of the cyber security control is based on an informal and unwritten, though standardized, practice."],
  ["Repeatable cyber security controls are in place. However, the control objectives and design are not formally defined or approved.", "There is limited consideration for a structured review or testing of a control."]),
 (3, "Structured and formalized", ["Cyber security controls are defined, approved and implemented in a structured and formalized way.", "The implementation of cyber security controls can be demonstrated."],
  ["Cyber security policies, standards and procedures are established.", "Compliance with cyber security documentation i.e., policies, standards and procedures is monitored, preferably using a governance, risk and compliance tool (GRC).", "key performance indicators are defined, monitored and reported to evaluate the implementation."]),
 (4, "Managed and measurable", ["The effectiveness of the cyber security controls are periodically assessed and improved when necessary.", "This periodic measurement, evaluations and opportunities for improvement are documented."],
  ["Effectiveness of cyber security controls are measured and periodically evaluated.", "key risk indicators and trend reporting are used to determine the effectiveness of the cyber security controls.", "Results of measurement and evaluation are used to identify opportunities for improvement of the cyber security controls."]),
 (5, "Adaptive", ["Cyber security controls are subject to a continuous improvement plan."],
  ["The enterprise-wide cyber security program focuses on continuous compliance, effectiveness and improvement of the cyber security controls.", "Cyber security controls are integrated with enterprise risk management framework and practices.", "Performance of cyber security controls are evaluated using peer and sector data."]),
]

# Questionnaire criteria: each one is a statement from Table 1 or section 2.4.1-2.4.3, with its source.
CRIT = [
 ("L1a", 1, "Cyber security controls are performed, even if in an inconsistent way.", "Table 1, level 1"),
 ("L2a", 2, "The execution of the cyber security control is based on an informal and unwritten, though standardized, practice.", "Table 1, level 2"),
 ("L3a", 3, "A cyber security policy is endorsed and mandated by the board, stating \"why\" cyber security is important and \"what\" principles and objectives are established.", "2.4.1"),
 ("L3b", 3, "Cyber security standards define \"what\" cyber security controls must be implemented (cyber security baselines).", "2.4.1"),
 ("L3c", 3, "Cyber security procedures prescribe \"how\" the cyber security controls, tasks and activities are executed.", "2.4.1"),
 ("L3d", 3, "The implementation of cyber security controls can be demonstrated.", "Table 1, level 3"),
 ("L3e", 3, "Compliance with cyber security documentation i.e., policies, standards and procedures is monitored, preferably using a governance, risk and compliance tool (GRC).", "Table 1, level 3"),
 ("L3f", 3, "Key performance indicators are defined, monitored and reported to evaluate the implementation.", "Table 1, level 3"),
 ("L4a", 4, "The effectiveness of the cyber security controls are periodically assessed and improved when necessary.", "Table 1, level 4"),
 ("L4b", 4, "Key risk indicators (KRIs) with thresholds and trend reporting are used to determine the effectiveness of the cyber security controls.", "Table 1, level 4 and 2.4.2"),
 ("L4c", 4, "This periodic measurement, evaluations and opportunities for improvement are documented.", "Table 1, level 4"),
 ("L5a", 5, "Cyber security controls are subject to a continuous improvement plan.", "Table 1, level 5"),
 ("L5b", 5, "Cyber security controls are integrated with enterprise risk management framework and practices.", "Table 1, level 5"),
 ("L5c", 5, "Performance of cyber security controls are evaluated using peer and sector data.", "Table 1, level 5"),
]
