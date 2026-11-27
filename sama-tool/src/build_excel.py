import sys; sys.path.insert(0, '.')
from datetime import date
from model import build, SH, CRIT, CSRC, TABLE1, action_for
from official import SUBSEC, PO, SECS
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side, Protection
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.chart import BarChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.utils import get_column_letter as CL

FN = "Arial"
def f(b=False, c="000000", s=10, i=False): return Font(name=FN, bold=b, color=c, size=s, italic=i)
def fill(h): return PatternFill("solid", fgColor=h)
NAVY, HEAD, LIGHT, YEL = fill("0B1524"), fill("1F3A68"), fill("DCE6F5"), fill("FFF2CC")
th = Side(style="thin", color="C9D3E3"); B = Border(left=th, right=th, top=th, bottom=th)
TOP = Alignment(vertical="top", wrap_text=True); CTR = Alignment(horizontal="center", vertical="center", wrap_text=True)
GOOD, WARN, BAD = fill("C6EFCE"), fill("FFEB9C"), fill("FFC7CE")

def hdr(ws, row, names, col=1):
    for j, h in enumerate(names, col):
        c = ws.cell(row, j, h); c.font = f(True, "FFFFFF"); c.fill = HEAD; c.border = B; c.alignment = CTR
    ws.row_dimensions[row].height = 36
def title(ws, t, sub, n):
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=n)
    ws["A1"] = t; ws["A1"].font = f(True, "FFFFFF", 14); ws["A1"].fill = NAVY; ws["A1"].alignment = Alignment(vertical="center", indent=1)
    ws.row_dimensions[1].height = 28
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=n)
    ws["A2"] = sub; ws["A2"].font = f(s=9, c="555555", i=True); ws["A2"].alignment = Alignment(indent=1, wrap_text=True)
    ws.row_dimensions[2].height = 26
def lines(t, w): return sum(1 + len(x) // w for x in str(t).split("\n"))
def dl():
    d = DataLabelList(); d.showVal = True; d.showSerName = False; d.showCatName = False; d.showLegendKey = False; return d
ORG_BANK, ORG_OTHER = "Bank", "Other member organization"
BANK_L4 = {"3.3.14", "3.3.15", "3.3.16", "3.3.17"}  # SAMA circular 298140000067 (17 Jan 2019): banks need level 4 here
SRC = "Source: SAMA Cyber Security Framework v1.0 (May 2017). Principles, objectives, control considerations and Table 1 are taken verbatim from the official document."

def make(path, sample):
    subs, ccs, gaps, docs = build()
    wb = Workbook(); ds = wb.active; ds.title = "5. Summary"; ds.sheet_view.showGridLines = False

    # ---------------- 1. SAMA Framework ----------------
    fw = wb.create_sheet("1. SAMA Framework"); fw.sheet_view.showGridLines = False
    title(fw, "1. SAMA Cyber Security Framework v1.0 - how SAMA assesses", SRC, 4)
    for j, w in enumerate([12, 30, 80, 60], 1): fw.column_dimensions[CL(j)].width = w
    r = 4
    def sec(h):
        nonlocal r
        r += 1; fw.merge_cells(start_row=r, start_column=1, end_row=r, end_column=4)
        c = fw.cell(r, 1, h); c.font = f(True, "FFFFFF", 11); c.fill = HEAD; c.alignment = Alignment(vertical="center", indent=1)
        fw.row_dimensions[r].height = 22; r += 1
    def row(a, b, w=170, bold=False):
        nonlocal r
        x = fw.cell(r, 1, a); x.font = f(True); x.alignment = TOP; x.border = B
        fw.merge_cells(start_row=r, start_column=2, end_row=r, end_column=4)
        y = fw.cell(r, 2, b); y.font = f(bold); y.alignment = TOP; y.border = B
        fw.row_dimensions[r].height = 14 * lines(b, w) + 6; r += 1
    fw.merge_cells(start_row=r, start_column=1, end_row=r, end_column=4)
    c = fw.cell(r, 1, "This tool is a personal initiative and does not replace SAMA's assessment."); c.font = f(True, "9C5700", 10); c.fill = fill("FFF2CC"); c.alignment = Alignment(wrap_text=True, vertical="center", indent=1)
    fw.row_dimensions[r].height = 32; r += 1
    sec("What is the framework")
    row("Issued by", "The Saudi Central Bank (SAMA), for the organizations it regulates (Member Organizations).")
    row("2.2", "Principle-based: SAMA sets principles and objectives and lists control considerations to achieve them. If a control consideration cannot be implemented, apply compensating controls, accept the risk internally and request a formal waiver from SAMA.")
    row("2.3", "Self-assessment: the organization assesses itself with a questionnaire; SAMA reviews and audits the result to determine compliance and maturity.")
    row("2.4", "Maturity: each subdomain gets a level from 0 to 5. The minimum required is level 3. Levels are cumulative: a level is reached only when all criteria of the lower levels are met.")
    sec("Structure: 4 domains, 32 subdomains (each = Principle, Objective, Control considerations)")
    from official import DOMS as FULL
    for d, nm in SH.items():
        names = [x for x in subs if x["dom"] == d]
        row(d, f"{FULL[d]} ({len(names)} subdomains): " + "; ".join(f'{x["sid"]} {x["sub"]}' for x in names) + ".")
    sec("Table 1 - Cyber Security Maturity Model (verbatim)")
    for j, h in enumerate(["Level", "Name", "Definition and Criteria", "Explanation"], 1):
        c = fw.cell(r, j, h); c.font = f(True, "FFFFFF"); c.fill = fill("3B5A8A"); c.border = B
    r += 1
    for n, nm, dc, ex in TABLE1:
        a_ = "\n".join("• " + x for x in dc); b_ = "\n".join("• " + x for x in ex)
        for j, v in enumerate([n, nm, a_, b_], 1):
            x = fw.cell(r, j, v); x.font = f(j <= 2, s=9.5); x.border = B; x.alignment = TOP
            if n == 3: x.fill = fill("E8F5E9")
        fw.row_dimensions[r].height = 13 * max(lines(a_, 80), lines(b_, 60)) + 6; r += 1
    sec("What level 3 needs (2.4.1) - the documentation pyramid")
    row("Policy", "Why / What: endorsed by the board; why cyber security matters, which assets to protect, and the principles and objectives.")
    row("Standards", "What: which controls must be implemented (baselines), e.g. parameters, password rules, segregation of duties, back-up.")
    row("Procedures", "How: step-by-step how the controls are executed by staff, third parties or customers.")
    row("Plus", "Implementation can be demonstrated, compliance is monitored (preferably with a GRC tool), and KPIs are reported. Level 4 adds KRIs with thresholds (2.4.2); level 5 adds continuous improvement, ERM integration and peer/sector comparison (2.4.3).")
    sec("The 14 questionnaire criteria used in sheet 3")
    for j, h in enumerate(["Criterion", "Level", "Criterion text", "SAMA source"], 1):
        c = fw.cell(r, j, h); c.font = f(True, "FFFFFF"); c.fill = fill("3B5A8A"); c.border = B
    r += 1; CR0 = r
    for c_ in CRIT:
        for j, v in enumerate([c_[0], c_[1], c_[2], CSRC[c_[0]]], 1):
            x = fw.cell(r, j, v); x.font = f(s=9.5); x.border = B; x.alignment = TOP
        fw.row_dimensions[r].height = 13 * lines(c_[2], 80) + 4; r += 1
    CR1 = r - 1
    sec("How to use this workbook (yellow cells = inputs)")
    row("3. Assessment", "The self-assessment: for each subdomain answer the 14 criteria Yes / No and write the evidence for Yes or what was found for No. The level appears in the subdomain header automatically. The Result column tells you if evidence is missing or an action was created. The target level is in column H of each subdomain header: 3 by default (SAMA's minimum), and it can be raised to 4 or 5. Any other value (for example 6, 2 or a number pasted as text) counts as 3 and is flagged in the summary. Choose the organization type at the top (cell J1): for a Bank, SAMA requires level 4 in 3.3.14, 3.3.15, 3.3.16 and 3.3.17 (circular 298140000067, 17 Jan 2019), so their target is at least 4.")
    row("2. Controls & Evidence", "Reference only: SAMA's principle, objective and control considerations for each subdomain (official text), with the required evidence. Use it to support your Yes / No answers in sheet 3.")
    row("4. Action Plan", "Escalation: you choose the stage (1st: To owner, CC GRC Manager and Line Manager; 2nd: To Line Manager, CC GRC Manager and Head of Department; 3rd: To Head of Department, CC GRC Manager and CISO). To, CC and the email text are filled automatically. Generated automatically: every No answer up to level 3 becomes an action with its corrective action, closure evidence, owner and priority. You add the target date, status and escalation in sheet 3 next to the criterion (columns I-M), so they stay with the right action when answers change. Fill the owner emails once (right side) to use the Send reminder links, which open an email on your own device. The full reminder email for each action is ready in column P to copy and paste.")
    row("5. Summary", "Updates automatically, including lists of overdue actions and actions due in the next 30 days. A data quality line at the top warns about invalid answers, statuses or target levels, dates pasted as text, and missing target dates. The report status line under it says NOT READY FOR APPROVAL until data quality is OK and all criteria are answered.")
    row("Rules", "Not assessed: a subdomain gets a level only when all 14 criteria are answered Yes or No; until then it is Not assessed and excluded from the average. Closing an action does not change the answer or the level: re-assess the criterion with evidence in sheet 3. Risk Accepted keeps the criterion unmet; its target date is the acceptance expiry date. All dates use one assessment date (as of) in sheet 4, cell AB29 (blank = today).")
    row("Privacy", "No data is collected. This workbook runs locally on your device; nothing is sent anywhere unless you send it.")
    row("Note", "Sample answers, owners and dates are fictional. Required evidence is derived by the author from the wording of each control consideration.")

    # ---------------- 3. Assessment (input, one row per criterion) ----------------
    la = wb.create_sheet("3. Assessment"); la.sheet_view.showGridLines = False
    title(la, "3. Assessment - the self-assessment questionnaire",
          "For each subdomain: answer every criterion Yes or No, and write the evidence (Yes) or what was found (No). Optionally paste a link to the evidence file in your own system. The level is calculated automatically: a level is reached only when all its criteria and all lower-level criteria are Yes. Yellow cells are inputs.", 8)
    # organization type: for banks SAMA requires level 4 in 3.3.14-3.3.17 (circular 298140000067, 17 Jan 2019)
    ot_l = la.cell(1, 9, "Organization type:"); ot_l.font = f(True, "FFFFFF", 10); ot_l.fill = NAVY; ot_l.alignment = Alignment(horizontal="right", vertical="center")
    la.merge_cells("J1:L1"); ot = la.cell(1, 10, ORG_OTHER); ot.fill = YEL; ot.font = f(True); ot.border = B; ot.alignment = Alignment(vertical="center")
    dot = DataValidation(type="list", formula1=f'"{ORG_BANK},{ORG_OTHER}"', allow_blank=False, promptTitle="Organization type",
                         prompt="Bank: SAMA requires level 4 in 3.3.14, 3.3.15, 3.3.16 and 3.3.17. Other: level 3 everywhere.", showInputMessage=True)
    la.add_data_validation(dot); dot.add("J1")
    hdr(la, 3, ["ID", "Level", "Criterion", "Question (from SAMA Table 1 and section 2.4)", "Answer", "Evidence (Yes) / What was found (No)", "Result", "Evidence link (optional)",
              "Action Target Date (RA: expiry)", "Action Status", "Escalation", "Escalation Date", "Risk Acceptance Ref.", "Key"])
    # Action tracking is entered here, next to its criterion, so it can never move to another action (stable key = subdomain|criterion)
    GBY = {(g["sid"], g["crit"]): g for g in gaps} if sample else {}
    dst = DataValidation(type="list", formula1='"Open,In Progress,Closed,Risk Accepted"', allow_blank=True); la.add_data_validation(dst)
    desc = DataValidation(type="list", formula1='"1st Escalation,2nd Escalation,3rd Escalation"', allow_blank=True); la.add_data_validation(desc)
    dtv = DataValidation(type="date", operator="greaterThan", formula1="36526", allow_blank=True); la.add_data_validation(dtv)
    # target level per subdomain: 3 is SAMA's minimum; it can be raised to 4 or 5, never lowered
    dtg = DataValidation(type="list", formula1='"3,4,5"', allow_blank=False, promptTitle="Target level", prompt="SAMA's minimum is level 3. Raise it to 4 or 5 if needed.", showInputMessage=True); la.add_data_validation(dtg)
    dyn = DataValidation(type="list", formula1='"Yes,No"', allow_blank=True); la.add_data_validation(dyn)
    POS, HROW = {}, {}; r = 4; RPN = 3 + len(subs) * len(CRIT)
    for k, s in enumerate(subs):
        use = sample; HROW[s["sid"]] = r
        la.merge_cells(start_row=r, start_column=1, end_row=r, end_column=4)
        h = la.cell(r, 1, f'{s["sid"]}  {s["sub"]}   ·   {s["domain"]}'); h.font = f(True, "FFFFFF", 11); h.fill = HEAD; h.alignment = Alignment(vertical="center", indent=1)
        o = la.cell(r, 5, "Owner:"); o.font = f(True, "FFFFFF"); o.fill = HEAD; o.alignment = Alignment(horizontal="right", vertical="center")
        ow = la.cell(r, 6, s["owner"] if use else None); ow.fill = YEL; ow.font = f(True); ow.border = B; ow.alignment = Alignment(vertical="center")
        for j_ in range(8, 14): la.cell(r, j_).fill = HEAD
        tg = la.cell(r, 8, 3); tg.fill = YEL; tg.font = f(True); tg.border = B; tg.alignment = CTR; tg.number_format = '"Target "0'; dtg.add(f"H{r}")
        la.cell(r, 9, "Action tracking (only when sheet 4 lists an action)").font = f(True, "FFFFFF", 8.5)
        lv = la.cell(r, 7, f'=IF(ISNUMBER(INDEX(Results!$S$5:$S$36,MATCH("{s["sid"]}",Results!$B$5:$B$36,0))),"Level "&INDEX(Results!$S$5:$S$36,MATCH("{s["sid"]}",Results!$B$5:$B$36,0))&" · "&INDEX(Results!$T$5:$T$36,MATCH("{s["sid"]}",Results!$B$5:$B$36,0)),"Not assessed")'); lv.font = f(True, "FFFFFF"); lv.fill = HEAD; lv.alignment = CTR
        la.row_dimensions[r].height = 24; r += 1
        for c in CRIT:
            POS[(s["sid"], c[0])] = r
            vals = [s["sid"], c[1], c[0], c[2], s["ans"][c[0]] if use else None, s["ev"][c[0]] if use else None,
                    f'=IF(E{r}="","Not answered",IF(AND(E{r}<>"Yes",E{r}<>"No"),"Invalid answer: use Yes or No",IF(F{r}="","Add evidence",IF(AND(E{r}="No",B{r}<=INDEX(Results!$U$5:$U$36,MATCH(A{r},Results!$B$5:$B$36,0)),INDEX(Results!$S$5:$S$36,MATCH(A{r},Results!$B$5:$B$36,0))<INDEX(Results!$U$5:$U$36,MATCH(A{r},Results!$B$5:$B$36,0))),IF(COUNTIFS(\'4. Action Plan\'!$B$4:$B${RPN},A{r},\'4. Action Plan\'!$E$4:$E${RPN},C{r},\'4. Action Plan\'!$L$4:$L${RPN},"Closed")>0,"Action closed: re-assess with evidence","Action created in sheet 4"),""))))']
            for j, v in enumerate(vals, 1):
                x = la.cell(r, j, v); x.font = f(s=9.5, c="888888" if j == 1 else "000000"); x.border = B
                x.alignment = CTR if j in (1, 2, 3, 5) else TOP
                if j in (5, 6): x.fill = YEL
            y_ = la.cell(r, 8); y_.fill = YEL; y_.border = B; y_.font = f(s=9, c="0563C1")
            la.cell(r, 2).number_format = '"Level "0'; dyn.add(f"E{r}")
            g_ = GBY.get((s["sid"], c[0]))
            if True:  # tracking for every criterion: a raised target can create actions for levels 4 and 5
                for j_, v_ in ((9, date.fromisoformat(g_["due"]) if g_ else None), (10, g_["fstatus"] if g_ else None), (11, (g_["esc"] or None) if g_ else None),
                               (12, (date.fromisoformat(g_["escd"]) if g_.get("escd") else None) if g_ else None), (13, (g_["ra"] or None) if g_ else None)):
                    x = la.cell(r, j_, v_); x.fill = YEL; x.border = B; x.font = f(s=9.5); x.alignment = CTR
                for j_ in (9, 12): la.cell(r, j_).number_format = "yyyy-mm-dd"
                dst.add(f"J{r}"); desc.add(f"K{r}"); dtv.add(f"I{r}"); dtv.add(f"L{r}")
            la.cell(r, 14, f'{s["sid"]}|{c[0]}').font = f(s=8, c="999999")
            la.row_dimensions[r].height = 13 * lines(c[2], 70) + 5; r += 1
        r += 1
    la_end = r - 1
    la.conditional_formatting.add(f"E4:E{la_end}", CellIsRule(operator="equal", formula=['"Yes"'], fill=GOOD))
    la.conditional_formatting.add(f"E4:E{la_end}", CellIsRule(operator="equal", formula=['"No"'], fill=BAD))
    la.conditional_formatting.add(f"G4:G{la_end}", CellIsRule(operator="equal", formula=['"Add evidence"'], fill=WARN))
    la.conditional_formatting.add(f"G4:G{la_end}", CellIsRule(operator="equal", formula=['"Invalid answer: use Yes or No"'], fill=BAD))
    for hr_ in HROW.values():  # target level that is not the number 3, 4 or 5 (counted as 3, flagged in the summary)
        la.conditional_formatting.add(f"H{hr_}", FormulaRule(formula=[f'AND(H{hr_}<>"",NOT(OR(H{hr_}=3,H{hr_}=4,H{hr_}=5)))'], fill=BAD))
    la.conditional_formatting.add(f"G4:G{la_end}", CellIsRule(operator="equal", formula=['"Action closed: re-assess with evidence"'], fill=WARN))
    la.conditional_formatting.add(f"E4:E{la_end}", FormulaRule(formula=['AND(E4<>"",E4<>"Yes",E4<>"No")'], fill=fill("C00000"), font=Font(name=FN, bold=True, color="FFFFFF")))
    la.conditional_formatting.add(f"G4:G{la_end}", CellIsRule(operator="equal", formula=['"Action created in sheet 4"'], fill=fill("DCE6F5")))
    for j, w in enumerate([9, 9, 9, 70, 10, 50, 26, 30, 14, 14, 15, 13, 16, 12], 1): la.column_dimensions[CL(j)].width = w
    la.column_dimensions["N"].hidden = True
    la.conditional_formatting.add(f"J4:J{la_end}", FormulaRule(formula=['AND(J4<>"",J4<>"Open",J4<>"In Progress",J4<>"Closed",J4<>"Risk Accepted")'], fill=fill("C00000"), font=Font(name=FN, bold=True, color="FFFFFF")))
    LA_END = la_end
    la.freeze_panes = "A4"

    # ---------------- Results (hidden, one row per subdomain) ----------------
    ma = wb.create_sheet("Results"); ma.sheet_state = "hidden"; ids = [c[0] for c in CRIT]
    title(ma, "3. Assessment - cumulative criteria per subdomain (SAMA CSF section 2.4)",
          "Answer Yes / No for each criterion (columns E to R) and write the evidence for every answer (columns Y to AL): for Yes the evidence reference, for No what was found, because SAMA reviews and audits the self-assessment and asks for evidence. The level is the highest level whose criteria, and all lower-level criteria, are Yes. Row 4 shows the criterion text.", 39)
    cols = ["Domain", "Subdomain ID", "Subdomain", "Owner"] + ids + ["Maturity Level", "Level Name", "Target", "Status", "Next level blocked by", "Notes"] + ["Evidence / justification " + c for c in ids] + ["Answers without evidence", "Invalid answers", "Valid answers (of 14)", "Invalid target", "Required level (SAMA)"]
    hdr(ma, 3, cols)
    for j, c in enumerate(CRIT, 5):
        x = ma.cell(4, j, c[2]); x.font = f(s=8, c="333333"); x.alignment = TOP; x.border = B; x.fill = LIGHT
    for j, c in enumerate(CRIT, 25):
        x = ma.cell(4, j, "Yes = evidence reference; No = what was found (gap) for " + c[0]); x.font = f(s=8, c="333333", i=True); x.alignment = TOP; x.border = B; x.fill = LIGHT
    for j in list(range(1, 5)) + list(range(19, 25)) + [39]: ma.cell(4, j).fill = LIGHT; ma.cell(4, j).border = B
    ma.cell(4, 3, "Criterion text (from SAMA Table 1 and section 2.4) →").font = f(True, s=9)
    ma.row_dimensions[4].height = 150
    dyn = DataValidation(type="list", formula1='"Yes,No"', allow_blank=True); ma.add_data_validation(dyn)
    r0 = 5; LN = '{"Non-existent","Ad-hoc","Repeatable but informal","Structured and formalized","Managed and measurable","Adaptive"}'
    for k, s in enumerate(subs):
        r = r0 + k; use = sample or k == 0
        vals = [s["domain"], s["sid"], s["sub"], f"='3. Assessment'!F{HROW[s['sid']]}&\"\""] + [f"='3. Assessment'!E{POS[(s['sid'], c)]}&\"\"" for c in ids]
        for j, v in enumerate(vals, 1):
            x = ma.cell(r, j, v); x.font = f(); x.border = B; x.alignment = TOP if j <= 4 else CTR
        E, F_, G, L, M, O, P, R = [f"{c}{r}" for c in ("E", "F", "G", "L", "M", "O", "P", "R")]
        # Not Assessed until all 14 criteria have a valid Yes / No answer (not counted as level 0)
        lvl = (f'=IF(COUNTIF({E}:{R},"Yes")+COUNTIF({E}:{R},"No")<14,"Not Assessed",IF({E}<>"Yes",0,IF({F_}<>"Yes",1,IF(COUNTIF({G}:{L},"Yes")<6,2,'
               f'IF(COUNTIF({M}:{O},"Yes")<3,3,IF(COUNTIF({P}:{R},"Yes")<3,4,5))))))')
        ma.cell(r, 19, lvl); ma.cell(r, 20, f'=IF(ISNUMBER(S{r}),INDEX({LN},S{r}+1),"Not Assessed")'); TG = f"'3. Assessment'!H{HROW[s['sid']]}"
        REQ = f"IF('3. Assessment'!$J$1=\"{ORG_BANK}\",4,3)" if s["sid"] in BANK_L4 else "3"
        ma.cell(r, 21, f"=MAX({REQ},IF(OR({TG}=3,{TG}=4,{TG}=5),{TG},3))")
        ma.cell(r, 22, f'=IF(ISNUMBER(S{r}),IF(S{r}>=U{r},"At target","Below target"),"Not Assessed")')
        blocked = (f'=IF(NOT(ISNUMBER(S{r})),"Answer all 14 criteria",IF(S{r}=5,"",IF(S{r}=0,"L1a",IF(S{r}=1,"L2a",IF(S{r}=2,"L3 criteria: "&(6-COUNTIF({G}:{L},"Yes"))&" not met",'
                   f'IF(S{r}=3,"L4 criteria: "&(3-COUNTIF({M}:{O},"Yes"))&" not met","L5 criteria: "&(3-COUNTIF({P}:{R},"Yes"))&" not met"))))))')
        ma.cell(r, 23, blocked)
        for j in range(19, 25):
            x = ma.cell(r, j); x.font = f(j == 19); x.border = B; x.alignment = CTR if j < 23 else TOP
        ma.cell(r, 21).font = f(c="0000FF")
        for j, c_ in enumerate(ids, 25):
            x = ma.cell(r, j, f"='3. Assessment'!F{POS[(s['sid'], c_)]}&\"\""); x.font = f(s=9); x.border = B; x.alignment = TOP
        x = ma.cell(r, 39, f'=SUMPRODUCT((E{r}:R{r}<>"")*(Y{r}:AL{r}=""))'); x.font = f(True); x.border = B; x.alignment = CTR
        x = ma.cell(r, 40, f'=SUMPRODUCT((E{r}:R{r}<>"")*(E{r}:R{r}<>"Yes")*(E{r}:R{r}<>"No"))'); x.font = f(True); x.border = B; x.alignment = CTR
        x = ma.cell(r, 41, f'=COUNTIF(E{r}:R{r},"Yes")+COUNTIF(E{r}:R{r},"No")'); x.font = f(); x.border = B; x.alignment = CTR
        # invalid target level (not the number 3, 4 or 5, e.g. 6, 2 or "4" pasted as text): counted as 3 and flagged
        x = ma.cell(r, 42, f'=IF(AND({TG}<>"",NOT(OR({TG}=3,{TG}=4,{TG}=5))),1,0)'); x.font = f(True); x.border = B; x.alignment = CTR
        x = ma.cell(r, 43, f"={REQ}"); x.font = f(); x.border = B; x.alignment = CTR  # level SAMA requires for this organization type
    rn = r0 + len(subs) - 1
    ma.conditional_formatting.add(f"E{r0}:R{rn}", CellIsRule(operator="equal", formula=['"Yes"'], fill=GOOD))
    ma.conditional_formatting.add(f"E{r0}:R{rn}", CellIsRule(operator="equal", formula=['"No"'], fill=BAD))
    ma.conditional_formatting.add(f"S{r0}:S{rn}", FormulaRule(formula=[f"S{r0}>=3"], fill=GOOD))
    ma.conditional_formatting.add(f"S{r0}:S{rn}", FormulaRule(formula=[f"S{r0}=2"], fill=WARN))
    ma.conditional_formatting.add(f"S{r0}:S{rn}", FormulaRule(formula=[f"S{r0}<2"], fill=BAD))
    for j, w in enumerate([24, 11, 30, 14] + [9] * 14 + [10, 22, 8, 13, 24, 28] + [26] * 14 + [14], 1): ma.column_dimensions[CL(j)].width = w
    ma.freeze_panes = "E5"; ma.auto_filter.ref = f"A3:AM{rn}"
    ma.conditional_formatting.add(f"AM{r0}:AM{rn}", CellIsRule(operator="greaterThan", formula=["0"], fill=BAD))
    MA = lambda c: f"Results!${c}${r0}:${c}${rn}"

    # ---------------- Control Considerations ----------------
    cc = wb.create_sheet("2. Controls & Evidence")
    title(cc, "2. Controls & Evidence - SAMA principle, objective and control considerations (official text)", SRC + " Reference only: what SAMA requires and the evidence that supports each Yes / No answer in sheet 3.", 7)
    hdr(cc, 3, ["Domain", "Subdomain ID", "Subdomain", "Sub-section", "Control No.", "Control Consideration (official text)", "Required Evidence"])
    first_sid = subs[0]["sid"]
    from official import SUBSEC as _SS, SECS as _SECS
    i = 4; prev = None; prevg = None
    def head(i, sid, name, dom, pr, ob, lvl2=False):
        txt = f"PRINCIPLE: {pr}\nOBJECTIVE: {ob}"
        vals = [dom, sid, name, "", sid, txt]
        for j in range(1, 8):
            x = cc.cell(i, j, vals[j - 1] if j <= 6 else None); x.fill = LIGHT if not lvl2 else fill("EEF3FA"); x.border = B; x.alignment = TOP
            x.font = f(True, "1F3A68", 9.5)
        cc.cell(i, 6).font = f(False, "1F3A68", 9.5, i=True)
        cc.row_dimensions[i].height = 12.5 * lines(txt, 88) + 6
    for c in ccs:
        if c["sid"] != prev:
            s_ = next(x for x in subs if x["sid"] == c["sid"])
            head(i, s_["sid"], s_["sub"], c["domain"], s_["pr"], s_["ob"]); i += 1; prev = c["sid"]; prevg = None
        if c["grp"] and c["grp"] != prevg:
            g_ = _SECS[c["grp"]]; head(i, c["sid"], c["sub"], c["domain"], g_["pr"], g_["ob"], True)
            cc.cell(i, 4, f'{c["grp"]} {g_["name"]}'); cc.cell(i, 5, c["grp"]); i += 1; prevg = c["grp"]
        use = sample or c["sid"] == first_sid
        sec = f'{c["grp"]} {SECS[c["grp"]]["name"]}' if c["grp"] else ""
        vals = [c["domain"], c["sid"], c["sub"], sec, c["ccid"], c["text"], c["ev"]]
        for j, v in enumerate(vals, 1):
            x = cc.cell(i, j, v); x.font = f(s=9.5); x.border = B; x.alignment = TOP
        cc.row_dimensions[i].height = min(409, 12.5 * lines(c["text"], 88) + 4); i += 1
    cn = i - 1
    for j, w in enumerate([22, 11, 26, 22, 12, 90, 50], 1): cc.column_dimensions[CL(j)].width = w
    cc.freeze_panes = "F4"; cc.auto_filter.ref = f"A3:G{cn}"
    CC = lambda c: f"'3. Controls & Evidence'!${c}$4:${c}${cn}"

    # ---------------- Remediation Plan ----------------
    # hidden engine: one row per subdomain x level 1-3 criterion
    from model import ACT, CRITICAL
    en = wb.create_sheet("Engine"); en.sheet_state = "hidden"
    hdr(en, 1, ["Subdomain ID", "Criterion", "Criterion level", "Answer", "Subdomain level", "Needed", "Action No.", "Action", "Closure evidence", "Priority"])
    L3 = list(CRIT); col_of = {c[0]: CL(5 + j) for j, c in enumerate(CRIT)}
    er = 2
    for s_ in subs:
        for c_ in L3:
            en.cell(er, 1, s_["sid"]); en.cell(er, 2, c_[0]); en.cell(er, 3, c_[1])
            en.cell(er, 4, f'=INDEX({MA(col_of[c_[0]])},MATCH(A{er},{MA("B")},0))&""')
            en.cell(er, 5, f'=INDEX({MA("S")},MATCH(A{er},{MA("B")},0))')
            en.cell(er, 6, f'=IF(AND(ISNUMBER(E{er}),D{er}="No",C{er}<=INDEX({MA("U")},MATCH(A{er},{MA("B")},0)),E{er}<INDEX({MA("U")},MATCH(A{er},{MA("B")},0))),1,0)')
            en.cell(er, 7, f'=IF(F{er}=1,SUM($F$2:F{er}),"")')
            a_, cl_, _ = action_for(s_["sid"], s_["sub"], c_[0]); en.cell(er, 8, a_); en.cell(er, 9, cl_)
            en.cell(er, 10, "High" if (c_[1] <= 2 or s_["sid"] in CRITICAL) else "Medium")
            er += 1
    en1 = er - 1
    EN = lambda c: f"Engine!${c}$2:${c}${en1}"

    OWN = sorted(set(x["owner"] for x in subs)) if sample else [subs[0]["owner"]]
    rp = wb.create_sheet("4. Action Plan")
    title(rp, "4. Action Plan - generated automatically from the No answers in sheet 3",
          "Every criterion up to the target level answered No (for a subdomain below its target) appears here automatically. The target is level 3, SAMA's minimum, unless it is raised to 4 or 5 in sheet 3. Target date, status, escalation stage, escalation date and risk acceptance ref. are entered in sheet 3, next to the criterion (columns I-M), so they stay with their action when answers change. The next escalation date, To, CC and the email text are calculated automatically.", 22)
    hdr(rp, 3, ["Action ID", "Subdomain ID", "Subdomain", "Current Level", "Criterion", "Criterion Text", "Corrective Action", "Closure Evidence", "Owner", "Priority", "Target Date (RA: expiry)", "Status", "Overdue", "Days Overdue", "Escalation", "Escalation Date", "Next Escalation Due", "Risk Acceptance Ref.", "Email To", "Email CC", "Send email", "Email text (copy and paste)"])
    rp.cell(2, 27, "Contacts (fill once; used for To and CC)").font = f(True, "1F3A68", 9)
    hdr(rp, 3, ["Control Owner", "Owner Email", "Line Manager Email", "Head of Department Email"], col=27)
    def em_(o, kind): return (o.lower().replace(" ", ".") + kind + "@example.com") if (o and sample) else None
    for k_, o_ in enumerate(OWN + [None] * (20 - len(OWN)), 4):
        for j, v in ((27, o_), (28, em_(o_, "")), (29, em_(o_, ".manager")), (30, em_(o_, ".head"))):
            x = rp.cell(k_, j, v); x.fill = YEL; x.border = B; x.font = f(s=9.5)
    for rr, (lab, v, dflt) in enumerate((("GRC Manager (your manager) email", "grc.manager@example.com", None), ("CISO email", "ciso@example.com", None), ("Your name (email signature)", "Raseel Almutairi", None), ("Days between escalations", 3, 3), ("Assessment date (as of); blank = today", date(2026, 11, 18), None)), 25):
        a_ = rp.cell(rr, 27, lab); a_.font = f(True, s=9.5); a_.border = B
        b_ = rp.cell(rr, 28, v if sample else dflt); b_.fill = YEL; b_.border = B; b_.font = f(s=9.5, c="0000FF" if rr == 28 else "000000")
        if rr == 29:
            b_.number_format = "yyyy-mm-dd"
            u_ = rp.cell(29, 29, '=IF(AB29="",TODAY(),AB29)'); u_.number_format = "yyyy-mm-dd"; u_.font = f(True, s=9.5); u_.border = B
            rp.cell(29, 30, "<- date used for Overdue, escalation and 30 days").font = f(s=8, i=True, c="555555")
    rp.cell(30, 30, None); rp.cell(30, 27, "Escalation stages (you choose the stage and the date you sent it in sheet 3, columns K and L)").font = f(True, "1F3A68", 9)
    for rr, (st, to, cc_) in enumerate((("1st Escalation", "Control owner", "GRC Manager, Line Manager"), ("2nd Escalation", "Line Manager", "GRC Manager, Head of Department"), ("3rd Escalation", "Head of Department", "GRC Manager, CISO")), 31):
        for j, v in ((27, st), (28, "To: " + to), (29, "CC: " + cc_)):
            x = rp.cell(rr, j, v); x.border = B; x.font = f(s=9.5, b=(j == 27))
    rp.cell(35, 27, "Next Escalation Due = Escalation Date + days between escalations. If the action is still open after the 3rd escalation, report it to the Cyber Security Committee, which monitors cyber security risks (SAMA CSF 3.1.4).").font = f(s=8, i=True, c="555555")
    for c_, w_ in (("AA", 30), ("AB", 30), ("AC", 34), ("AD", 34)): rp.column_dimensions[c_].width = w_
    nrows = en1 - 1
    DONE = lambda i: f'OR(L{i}="Closed",L{i}="Risk Accepted")'
    LK = lambda col, i: f'IFERROR(INDEX(${col}$4:${col}$23,MATCH(I{i},$AA$4:$AA$23,0))&"","")'
    for k in range(1, nrows + 1):
        i = 3 + k
        KEY = f'B{i}&"|"&E{i}'
        TR = lambda col: f"=IF(B{i}=\"\",\"\",IF(INDEX('3. Assessment'!${col}$4:${col}${LA_END},MATCH({KEY},'3. Assessment'!$N$4:$N${LA_END},0))=\"\",\"\",INDEX('3. Assessment'!${col}$4:${col}${LA_END},MATCH({KEY},'3. Assessment'!$N$4:$N${LA_END},0))))"
        M_ = lambda c: f'IFERROR(INDEX({EN(c)},MATCH({k},{EN("G")},0)),"")'
        vals = [f'=IF(B{i}="","",B{i}&"-"&E{i})', f"={M_('A')}",
                f'=IF(B{i}="","",INDEX({MA("C")},MATCH(B{i},{MA("B")},0)))',
                f'=IF(B{i}="","",INDEX({MA("S")},MATCH(B{i},{MA("B")},0)))',
                f"={M_('B')}", f"=IF(E{i}=\"\",\"\",INDEX('1. SAMA Framework'!$C${CR0}:$C${CR1},MATCH(E{i},'1. SAMA Framework'!$A${CR0}:$A${CR1},0)))",
                f"={M_('H')}", f"={M_('I')}",
                f'=IF(B{i}="","",INDEX({MA("D")},MATCH(B{i},{MA("B")},0))&"")', f"={M_('J')}",
                TR("I"), TR("J"),
                f'=IF(B{i}="","",IF(AND(K{i}<>"",NOT(ISNUMBER(K{i}))),"Invalid date",IF(AND(L{i}="Risk Accepted",K{i}<>"",K{i}<$AC$29),"RA expired",IF({DONE(i)},"",IF(K{i}="","No target date",IF(K{i}<$AC$29,"Yes",""))))))',
                f'=IF(M{i}="Yes",$AC$29-K{i},"")',
                TR("K"), TR("L"),
                f'=IF(OR(B{i}="",{DONE(i)},P{i}="",O{i}=""),"",IF(O{i}="3rd Escalation","Report to Committee",IF(ISNUMBER(P{i}),P{i}+$AB$28,"Invalid date")))',
                TR("M"),
                f'=IF(OR(B{i}="",{DONE(i)}),"",IF(O{i}="2nd Escalation",{LK("AC", i)},IF(O{i}="3rd Escalation",{LK("AD", i)},{LK("AB", i)})))',
                f'=IF(OR(B{i}="",{DONE(i)},O{i}=""),"",IF(O{i}="1st Escalation",$AB$25&";"&{LK("AC", i)},IF(O{i}="2nd Escalation",$AB$25&";"&{LK("AD", i)},$AB$25&";"&$AB$26)))']
        for j, v in enumerate(vals, 1):
            x = rp.cell(i, j, v); x.font = f(s=9.5); x.border = B; x.alignment = TOP
        for j in (11, 16, 17): rp.cell(i, j).number_format = "yyyy-mm-dd"
        subj = f'"SAMA CSF action "&A{i}&IF(O{i}=""," - reminder"," - "&O{i})'
        body = f'LEFT("Please update action "&A{i}&" ("&B{i}&" "&E{i}&"): "&G{i},80)'
        rm = rp.cell(i, 21, f'=IF(S{i}="","",HYPERLINK("mailto:"&S{i}&"?cc="&T{i}&"&subject="&SUBSTITUTE({subj}," ","%20")&"&body="&SUBSTITUTE({body}," ","%20"),"Send email"))')
        rm.font = Font(name=FN, size=9.5, color="0563C1", underline="single"); rm.border = B
        N_ = 'CHAR(10)'
        mail = (f'=IF(B{i}="","","To: "&S{i}&{N_}&"CC: "&IF(T{i}="","-",T{i})&{N_}&"Subject: SAMA CSF Action "&A{i}&IF(O{i}=""," - Reminder"," - "&O{i})&{N_}&{N_}'
                f'&"Dear "&I{i}&IF(O{i}="2nd Escalation"," Line Manager",IF(O{i}="3rd Escalation"," Head of Department"," team"))&","&{N_}&{N_}'
                f'&IF(O{i}="","This is a reminder about the following action","This action has been escalated ("&O{i}&")")&" from the SAMA Cyber Security Framework self-assessment:"&{N_}&{N_}'
                f'&"- Action ID: "&A{i}&{N_}&"- Subdomain: "&B{i}&" "&C{i}&{N_}&"- Missing criterion: "&E{i}&" - "&F{i}&{N_}'
                f'&"- Required action: "&G{i}&{N_}&"- Closure evidence: "&H{i}&{N_}&"- Action owner: "&I{i}&{N_}&"- Target date: "&IF(K{i}="","(not set)",TEXT(K{i},"yyyy-mm-dd"))&{N_}'
                f'&"- Current status: "&IF(L{i}="","Open",L{i})&IF(M{i}="Yes"," ("&N{i}&" days overdue)","")&{N_}'
                f'&IF(AND(O{i}<>"",O{i}<>"3rd Escalation",ISNUMBER(Q{i})),"- Next escalation: "&TEXT(Q{i},"yyyy-mm-dd")&" if there is no update"&{N_},"")&IF(O{i}="3rd Escalation","- Next step: the action will be reported to the Cyber Security Committee"&{N_},"")&{N_}'
                f'&"Please share an update on the progress, or send the closure evidence if the action is completed. If the action cannot be completed, please let us know so the risk can be formally accepted by the risk owner."&{N_}&{N_}'
                f'&"Thank you,"&{N_}&IF($AB$27="","[Your name]",$AB$27)&{N_}&"GRC")')
        me = rp.cell(i, 22, mail); me.font = f(s=8.5); me.border = B; me.alignment = Alignment(wrap_text=False, vertical="top")
        rp.cell(i, 23, f'=IF(M{i}="Yes",COUNTIF(M$4:M{i},"Yes"),"")')
        rp.cell(i, 24, f'=IF(AND(B{i}<>"",ISNUMBER(K{i}),NOT({DONE(i)}),K{i}>=$AC$29,K{i}<=$AC$29+30),1,0)')
        rp.cell(i, 25, f'=IF(X{i}=1,SUM(X$4:X{i}),"")')
        for j in (23, 24, 25): rp.cell(i, j).font = f(s=8, c="999999")
    rpn = 3 + nrows
    rp.conditional_formatting.add(f"M4:M{rpn}", CellIsRule(operator="equal", formula=['"Yes"'], fill=BAD, font=Font(name=FN, bold=True, color="9C0006")))
    rp.conditional_formatting.add(f"J4:J{rpn}", CellIsRule(operator="equal", formula=['"High"'], fill=BAD))
    for v_, fl in (("3rd Escalation", fill("C00000")), ("2nd Escalation", BAD), ("1st Escalation", WARN)):
        rp.conditional_formatting.add(f"O4:O{rpn}", CellIsRule(operator="equal", formula=[f'"{v_}"'], fill=fl, font=Font(name=FN, bold=True, color="FFFFFF") if v_.startswith("3rd") else None))
    rp.conditional_formatting.add(f"Q4:Q{rpn}", FormulaRule(formula=[f'AND(ISNUMBER(Q4),Q4<=$AC$29)'], fill=BAD, font=Font(name=FN, bold=True, color="9C0006")))
    rp.conditional_formatting.add(f"L4:L{rpn}", CellIsRule(operator="equal", formula=['"Risk Accepted"'], fill=fill("E4DFEC")))
    rp.conditional_formatting.add(f"L4:L{rpn}", CellIsRule(operator="equal", formula=['"Closed"'], fill=WARN))
    rp.conditional_formatting.add(f"M4:M{rpn}", CellIsRule(operator="equal", formula=['"No target date"'], fill=WARN))
    for c_ in ("M", "Q"):
        rp.conditional_formatting.add(f"{c_}4:{c_}{rpn}", CellIsRule(operator="equal", formula=['"Invalid date"'], fill=BAD))
    rp.conditional_formatting.add(f"M4:M{rpn}", CellIsRule(operator="equal", formula=['"RA expired"'], fill=BAD))
    rp.conditional_formatting.add(f"L4:L{rpn}", FormulaRule(formula=['AND(L4<>"",L4<>"Open",L4<>"In Progress",L4<>"Closed",L4<>"Risk Accepted")'], fill=fill("C00000"), font=Font(name=FN, bold=True, color="FFFFFF")))
    for j, w in enumerate([9, 11, 26, 10, 9, 46, 40, 30, 14, 10, 12, 13, 9, 9, 15, 13, 16, 18, 30, 40, 12, 60, 6, 6, 6], 1): rp.column_dimensions[CL(j)].width = w
    for j, h in ((23, "Overdue #"), (24, "Due 30d"), (25, "Due 30d #")):
        x = rp.cell(3, j, h); x.font = f(s=8, c="999999")
    rp.freeze_panes = "D4"; rp.auto_filter.ref = f"A3:V{rpn}"
    RP = lambda c: f"'4. Action Plan'!${c}$4:${c}${rpn}"
    AS = "'4. Action Plan'!$AC$29"

    # ---------------- Dashboard ----------------
    title(ds, "5. Summary - SAMA CSF Maturity Self-Assessment", ("Sample data for demonstration only. " if sample else "") + "Personal initiative; does not replace SAMA's assessment. " + "All figures are formulas linked to sheets 3 and 4. Subdomains that are not fully answered are shown as Not assessed and excluded from the average.", 12)
    k = [("Average maturity", f'=IFERROR(ROUND(AVERAGE({MA("S")}),1),"Not assessed")', "0.0"),
         ("Subdomains at level 3+", f'=COUNTIF({MA("S")},">=3")&" / "&COUNTA({MA("B")})', None),
         ("Open actions", f'=COUNTIFS({RP("A")},"?*",{RP("L")},"<>Closed",{RP("L")},"<>Risk Accepted")', None),
         ("Overdue", f'=COUNTIF({RP("M")},"Yes")', None),
         ("Assessment completion", f'=SUM({MA("AO")})/(14*COUNTA({MA("B")}))', "0%"),
         ("Closed - re-assess", f'=COUNTIF({RP("L")},"Closed")', None)]
    for j, (lab, fm, nf) in enumerate(k):
        c0 = 1 + j * 2 if j else 1
        c0 = [1, 3, 5, 7, 9, 11][j]
        ds.merge_cells(start_row=4, start_column=c0, end_row=4, end_column=c0 + 1)
        ds.merge_cells(start_row=5, start_column=c0, end_row=5, end_column=c0 + 1)
        a_ = ds.cell(4, c0, lab); a_.font = f(True, "FFFFFF", 9); a_.fill = HEAD; a_.alignment = CTR
        v = ds.cell(5, c0, fm); v.font = f(True, "1F3A68", 18); v.alignment = CTR; v.fill = LIGHT
        if nf: v.number_format = nf
    ds.row_dimensions[5].height = 34
    ds.cell(4, 3).value = "Subdomains at level 3+ (assessed)"
    # data quality banner (FIX-02): invalid answers, invalid statuses, missing target dates
    dq = (f'=SUM({MA("AN")})+IF(OR(\'3. Assessment\'!$J$1="{ORG_BANK}",\'3. Assessment\'!$J$1="{ORG_OTHER}"),0,1)+SUMPRODUCT(({RP("L")}<>"")*({RP("L")}<>"Open")*({RP("L")}<>"In Progress")*({RP("L")}<>"Closed")*({RP("L")}<>"Risk Accepted"))'
          f'+SUMPRODUCT(({RP("O")}<>"")*({RP("O")}<>"1st Escalation")*({RP("O")}<>"2nd Escalation")*({RP("O")}<>"3rd Escalation"))+COUNTIF({RP("M")},"No target date")'
          f'+COUNTIF({RP("M")},"Invalid date")+COUNTIF({RP("Q")},"Invalid date")+SUM({MA("AP")})')
    ds.merge_cells("A6:L6")
    w_ = ds.cell(6, 1, f'=IF(({dq[1:]})=0,"Data quality: OK. Assessment date (as of) "&TEXT({AS},"yyyy-mm-dd"),"WARNING: "&({dq[1:]})&" data quality issue(s) (invalid answers, statuses, target levels or dates, or missing target dates). Fix them before using the figures. Assessment date (as of) "&TEXT({AS},"yyyy-mm-dd"))')
    w_.font = f(True, s=9.5); w_.alignment = Alignment(vertical="center", indent=1)
    ds.conditional_formatting.add("A6", FormulaRule(formula=['LEFT(A6,7)="WARNING"'], fill=fill("C00000"), font=Font(name=FN, bold=True, color="FFFFFF")))
    ds.conditional_formatting.add("A6", FormulaRule(formula=['LEFT(A6,4)="Data"'], fill=GOOD))
    ds.row_dimensions[6].height = 22
    # report status: the figures are not ready for approval while data quality fails or the assessment is incomplete
    ds.merge_cells("A7:L7")
    rs_ = ds.cell(7, 1, f'=IF(({dq[1:]})>0,"Report status: NOT READY FOR APPROVAL. Fix the data quality issues above first.",'
                        f'IF(I5<1,"Report status: NOT READY FOR APPROVAL. The assessment is not complete ("&TEXT(I5,"0%")&" of the criteria answered).",'
                        f'IF(SUM({MA("AM")})>0,"Report status: NOT READY FOR APPROVAL. "&SUM({MA("AM")})&" answer(s) have no evidence or finding written.",'
                        f'"Report status: Ready for approval (data quality OK, all criteria answered with evidence).")))')
    rs_.font = f(True, s=9.5); rs_.alignment = Alignment(vertical="center", indent=1)
    ds.conditional_formatting.add("A7", FormulaRule(formula=['ISNUMBER(SEARCH("NOT READY",A7))'], fill=fill("C00000"), font=Font(name=FN, bold=True, color="FFFFFF")))
    ds.conditional_formatting.add("A7", FormulaRule(formula=['ISNUMBER(SEARCH("Ready for approval",A7))'], fill=GOOD))
    ds.row_dimensions[7].height = 22
    r = 8; hdr(ds, r, ["Domain", "Subdomains", "Average maturity", "At level 3+", "Open actions"])
    for i, (d, nm) in enumerate(SH.items(), r + 1):
        vals = [nm, f'=COUNTIF({MA("A")},A{i})', f'=IFERROR(ROUND(AVERAGEIF({MA("A")},A{i},{MA("S")}),1),"-")',
                f'=COUNTIFS({MA("A")},A{i},{MA("S")},">=3")&" / "&B{i}', f'=COUNTIFS({RP("AF")},A{i},{RP("L")},"<>Closed",{RP("L")},"<>Risk Accepted",{RP("A")},"?*")']
        for j, v in enumerate(vals, 1):
            x = ds.cell(i, j, v); x.font = f(); x.border = B; x.alignment = CTR if j > 1 else TOP
    rp.cell(3, 32, "Domain (lookup)"); rp.cell(3, 32).font = f(True, "FFFFFF"); rp.cell(3, 32).fill = HEAD; rp.cell(3, 32).border = B; rp.cell(3, 32).alignment = CTR
    for i in range(4, rpn + 1):
        x = rp.cell(i, 32, f'=IF(B{i}="","",INDEX({MA("A")},MATCH(B{i},{MA("B")},0)))'); x.font = f(s=9.5); x.border = B
    t = r + 5
    for j, v in enumerate(["Total", f"=SUM(B{r+1}:B{t-1})", f'=IFERROR(ROUND(AVERAGE({MA("S")}),1),"-")', f'=COUNTIF({MA("S")},">=3")&" / "&B{t}', f"=SUM(E{r+1}:E{t-1})"], 1):
        x = ds.cell(t, j, v); x.font = f(True); x.border = B; x.fill = LIGHT; x.alignment = CTR if j > 1 else TOP
    ch = BarChart(); ch.type = "col"; ch.title = "Average maturity by domain (target 3)"; ch.y_axis.scaling.min = 0; ch.y_axis.scaling.max = 5
    ch.add_data(Reference(ds, min_col=3, min_row=r, max_row=r + 4), titles_from_data=True); ch.set_categories(Reference(ds, min_col=1, min_row=r + 1, max_row=r + 4))
    ch.dataLabels = dl(); ch.legend = None; ch.height = 8; ch.width = 18; ds.add_chart(ch, f"A{t+2}")
    hdr(ds, 8, ["Escalation", "Actions"], col=9)
    for q, (lab, crit_) in enumerate((("Overdue, not escalated yet", None), ("1st Escalation", "1st Escalation"), ("2nd Escalation", "2nd Escalation"), ("3rd Escalation", "3rd Escalation"), ("Next escalation due now", "DUE"), ("Risk accepted (criterion still unmet)", "RA"), ("Risk acceptance expired", "RAX"), ("Open without target date", "ND")), 9):
        a_ = ds.cell(q, 9, lab); a_.font = f(s=9.5); a_.border = B
        fm_ = (f'=COUNTIFS({RP("M")},"Yes",{RP("O")},"")' if crit_ is None else f'=COUNTIFS({RP("Q")},"<="&{AS},{RP("L")},"<>Closed",{RP("L")},"<>Risk Accepted")' if crit_ == "DUE" else f'=COUNTIF({RP("L")},"Risk Accepted")' if crit_ == "RA" else f'=COUNTIF({RP("M")},"RA expired")' if crit_ == "RAX" else f'=COUNTIF({RP("M")},"No target date")' if crit_ == "ND" else f'=COUNTIFS({RP("O")},"{crit_}",{RP("L")},"<>Closed",{RP("L")},"<>Risk Accepted")')
        b_ = ds.cell(q, 10, fm_); b_.font = f(True); b_.border = B; b_.alignment = CTR
    ds.conditional_formatting.add("J15:J16", CellIsRule(operator="greaterThan", formula=["0"], fill=BAD, font=Font(name=FN, bold=True, color="9C0006")))
    ds.conditional_formatting.add("J12:J13", CellIsRule(operator="greaterThan", formula=["0"], fill=BAD, font=Font(name=FN, bold=True, color="9C0006")))
    ds.column_dimensions["I"].width = 34; ds.column_dimensions["J"].width = 10
    lr = t + 20
    for title_, rk, third in (("Overdue actions (first 10)", "W", ("Escalation", "O")), ("Due in the next 30 days (first 10)", "Y", ("Criterion", "E"))):
        ds.merge_cells(start_row=lr, start_column=1, end_row=lr, end_column=7)
        c_ = ds.cell(lr, 1, title_); c_.font = f(True, "FFFFFF", 11); c_.fill = HEAD; lr += 1
        for j, h in enumerate(["Action ID", "Subdomain", third[0], "Corrective Action", "", "Owner", "Target Date"], 1):
            x = ds.cell(lr, j, h); x.font = f(True, s=9); x.fill = LIGHT; x.border = B
        ds.merge_cells(start_row=lr, start_column=4, end_row=lr, end_column=5); lr += 1
        for k_ in range(1, 11):
            g_ = lambda c: f'=IFERROR(INDEX({RP(c)},MATCH({k_},{RP(rk)},0)),"")'
            for j, c in ((1, "A"), (2, "C"), (3, third[1]), (4, "G"), (6, "I"), (7, "K")):
                x = ds.cell(lr, j, g_(c)); x.font = f(s=9); x.border = B; x.alignment = TOP
            ds.merge_cells(start_row=lr, start_column=4, end_row=lr, end_column=5)
            ds.cell(lr, 7).number_format = "yyyy-mm-dd"; lr += 1
        lr += 1
    for j, w in enumerate([30, 12, 14, 14, 12, 12, 14, 12], 1): ds.column_dimensions[CL(j)].width = w
    ds.column_dimensions["I"].width = 34; ds.column_dimensions["J"].width = 12; ds.column_dimensions["K"].width = 12; ds.column_dimensions["L"].width = 12

    wb._sheets = [fw, cc, la, rp, ds, ma, en]
    for w in wb.worksheets:
        for dv in w.data_validations.dataValidation:
            dv.showErrorMessage = True; dv.errorStyle = "stop"; dv.errorTitle = "Invalid value"; dv.error = "Choose a value from the list."
        # protect formulas: only yellow input cells are editable (no password; this prevents mistakes, it is not a security control)
        for row_ in w.iter_rows():
            for c_ in row_:
                if c_.fill is not None and c_.fill.fgColor is not None and str(c_.fill.fgColor.rgb).endswith("FFF2CC") and w is not fw:
                    c_.protection = Protection(locked=False)
        w.protection.sheet = True; w.protection.autoFilter = False; w.protection.sort = False
        w.protection.formatColumns = False; w.protection.formatRows = False; w.protection.selectLockedCells = False
    wb.properties.creator = "Raseel Almutairi"; wb.properties.lastModifiedBy = "Raseel Almutairi"; wb.properties.title = "SAMA CSF Maturity Self-Assessment" 
    wb.active = 0
    for w in wb.worksheets:
        w.sheet_properties.pageSetUpPr.fitToPage = True; w.page_setup.fitToWidth = 1; w.page_setup.fitToHeight = 0; w.page_setup.orientation = "landscape"
    wb.save(path)

make("../SAMA_CSF_Assessment_Sample.xlsx", True)
make("../SAMA_CSF_Assessment_Blank.xlsx", False)
print("ok")
