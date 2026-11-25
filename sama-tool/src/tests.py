"""Regression and rule tests for the SAMA CSF demo (run: python tests.py).

The figures below are the sample data as of 2026-11-18. If a change moves one of them,
the change must explain why (see CHANGELOG.md)."""
from datetime import date
from model import build, AS_OF

subs, ccs, gaps, docs = build()
ok = 0


def check(name, cond):
    global ok
    assert cond, "FAILED: " + name
    ok += 1
    print("PASS", name)


# Baseline figures (sample data, as of 2026-11-18)
check("assessment date is pinned", AS_OF == date(2026, 11, 18))
check("32 subdomains", len(subs) == 32)
check("149 control considerations", len(ccs) == 149)
check("average maturity 2.5", round(sum(s["level"] for s in subs) / 32, 1) == 2.5)
check("17 of 32 at level 3+", sum(s["level"] >= 3 for s in subs) == 17)
check("63 actions", len(gaps) == 63)
check("8 overdue", sum(g["overdue"] for g in gaps) == 8)

# Rules
check("controls carry no status (reference only)", all("st" not in c for c in ccs))
check("every action is for a criterion still answered No",
      all(next(s for s in subs if s["sid"] == g["sid"])["ans"][g["crit"]] == "No" for g in gaps))
check("closing an action does not change the answer: closed actions are flagged re-assess",
      all(g["reassess"] == (g["fstatus"] == "Closed") for g in gaps) and sum(g["reassess"] for g in gaps) == 6)
check("risk accepted is not counted as met and is not counted as open",
      sum(g["fstatus"] == "Risk Accepted" for g in gaps) == 1)
check("closed or risk accepted actions are never overdue",
      not any(g["overdue"] for g in gaps if g["fstatus"] in ("Closed", "Risk Accepted")))
check("every action has a target date", all(g["due"] for g in gaps))
check("action text names the subdomain", all(g["action"].startswith(g["sub"] + ": ") for g in gaps))
check("every action is linked to the control considerations of its subdomain",
      all(g["ccids"] and g["ccids"] == [c["ccid"] for c in ccs if c["sid"] == g["sid"]] and g["ccids"][0] in g["action"] for g in gaps))
check("the implementation action (L3d) names the evidence per control consideration",
      all(g["ccids"][0] in g["closure"] or "sheet 2" in g["closure"] for g in gaps if g["crit"] == "L3d"))

# Built files
import os
web = open(os.path.join("..", "index.html"), encoding="utf-8").read()
check("action IDs are stable keys (subdomain-criterion)", all(g["gid"] == f'{g["sid"]}-{g["crit"]}' for g in gaps))
check("web makes no external requests", "googleapis" not in web and "Content-Security-Policy" in web)
check("web shows the assessment date", "18 Nov 2026" in web)

# Excel (reads the values saved in the file: open and save it in Excel, or recalculate with LibreOffice, after a rebuild)
import shutil, subprocess, tempfile, warnings
from openpyxl import load_workbook
warnings.filterwarnings("ignore")
SAMPLE = os.path.join("..", "SAMA_CSF_Assessment_Sample.xlsx")


def actions(path):
    rp = load_workbook(path, data_only=True)["4. Action Plan"]
    ids = [rp.cell(r, 1).value for r in range(4, rp.max_row + 1) if rp.cell(r, 1).value]
    assert len(ids) == len(set(ids)), "repeated action ID in the Excel action plan"
    return {rp.cell(r, 1).value: (rp.cell(r, 12).value, rp.cell(r, 13).value, rp.cell(r, 15).value)
            for r in range(4, rp.max_row + 1) if rp.cell(r, 1).value}


xa = actions(SAMPLE)
check("Excel actions = web actions: same 63 keys, none missing, extra or repeated", set(xa) == {g["gid"] for g in gaps} and len(xa) == len(gaps) == 63)
check("Excel action status = web status, per key", all(xa[g["gid"]][0] == g["fstatus"] for g in gaps))
check("Excel overdue = web overdue (8)", sum(v[1] == "Yes" for v in xa.values()) == sum(g["overdue"] for g in gaps) == 8)
ds = load_workbook(SAMPLE, data_only=True)["5. Summary"]
check("Excel summary: 2.5 average, 17 / 32, 56 open", (ds["A5"].value, ds["C5"].value, ds["E5"].value) == (2.5, "17 / 32", 56))
blank = load_workbook(os.path.join("..", "SAMA_CSF_Assessment_Blank.xlsx"), data_only=True)["5. Summary"]
check("blank Excel: not assessed, 0% complete", (blank["A5"].value, blank["I5"].value) == ("Not assessed", 0))

soffice = shutil.which("soffice") or shutil.which("libreoffice")
if soffice:
    # Re-assess one closed action to Yes: it must leave the plan, and every other action keeps its own status and escalation
    with tempfile.TemporaryDirectory() as tmp:
        wb = load_workbook(SAMPLE)
        la = wb["3. Assessment"]
        r = next(r for r in range(4, la.max_row + 1) if la.cell(r, 10).value == "Closed")
        key = la.cell(r, 14).value.replace("|", "-")
        la.cell(r, 5).value = "Yes"
        wb.save(os.path.join(tmp, "t.xlsx"))
        subprocess.run([soffice, "--headless", "--convert-to", "xlsx", "--outdir", os.path.join(tmp, "out"), os.path.join(tmp, "t.xlsx")],
                       capture_output=True, check=True, timeout=300)
        after = actions(os.path.join(tmp, "out", "t.xlsx"))
    check("re-assessed action leaves the plan", key not in after and len(after) == len(xa) - 1)
    check("no other action changes status, overdue or escalation (no row shift)", all(after[k] == xa[k] for k in after))
    # Raise one level-3 subdomain's target to 4: its unmet level-4 criteria become actions; the target cannot go below 3
    with tempfile.TemporaryDirectory() as tmp:
        wb = load_workbook(SAMPLE)
        la = wb["3. Assessment"]
        lvl3 = [x for x in subs if x["level"] == 3 and any(v == "No" for k_, v in x["ans"].items() if k_.startswith("L4"))]
        sid = lvl3[0]["sid"]
        hr = next(r for r in range(4, la.max_row + 1) if str(la.cell(r, 1).value).startswith(sid + " "))
        la.cell(hr, 8).value = 4
        other = next(x for x in subs if x["sid"] != sid)
        la.cell(next(r for r in range(4, la.max_row + 1) if str(la.cell(r, 1).value).startswith(other["sid"] + " ")), 8).value = 2
        wb.save(os.path.join(tmp, "t.xlsx"))
        subprocess.run([soffice, "--headless", "--convert-to", "xlsx", "--outdir", os.path.join(tmp, "out"), os.path.join(tmp, "t.xlsx")],
                       capture_output=True, check=True, timeout=300)
        after = actions(os.path.join(tmp, "out", "t.xlsx"))
    new = {k for k in after if k.startswith(sid + "-L4")}
    check("raising a target to 4 creates actions for its unmet level-4 criteria",
          new == {f"{sid}-{k_}" for k_, v in lvl3[0]["ans"].items() if k_.startswith("L4") and v == "No"} and all(after[k] == xa[k] for k in xa if k in after))
    check("a target below 3 is not allowed (counted as 3)", {k for k in after if k.startswith(other["sid"] + "-")} == {k for k in xa if k.startswith(other["sid"] + "-")})
    # Values pasted past the drop-down lists are flagged, not hidden: target 6, target "4" as text, a target date as text
    with tempfile.TemporaryDirectory() as tmp:
        wb = load_workbook(SAMPLE)
        la = wb["3. Assessment"]
        heads = [r for r in range(4, la.max_row + 1) if isinstance(la.cell(r, 8).value, int)]
        la.cell(heads[0], 8).value = 6
        la.cell(heads[1], 8).value = "4"
        r = next(r for r in range(4, la.max_row + 1) if la.cell(r, 10).value in ("Open", "In Progress") and la.cell(r, 9).value)
        key = la.cell(r, 14).value.replace("|", "-")
        la.cell(r, 9).value = "2026-01-01"
        wb.save(os.path.join(tmp, "t.xlsx"))
        subprocess.run([soffice, "--headless", "--convert-to", "xlsx", "--outdir", os.path.join(tmp, "out"), os.path.join(tmp, "t.xlsx")],
                       capture_output=True, check=True, timeout=300)
        after = actions(os.path.join(tmp, "out", "t.xlsx"))
        out = load_workbook(os.path.join(tmp, "out", "t.xlsx"), data_only=True)
        banner = out["5. Summary"]["A6"].value
        h0 = out["3. Assessment"].cell(heads[0], 1).value.split(" ")[0]
    check("target 6 or \"4\" as text counts as 3 (no extra actions) and a date pasted as text shows Invalid date",
          {k for k in after if k.startswith(h0 + "-")} == {k for k in xa if k.startswith(h0 + "-")} and after[key][1] == "Invalid date")
    check("the summary warns about the 3 pasted values", banner.startswith("WARNING: 3 "))
else:
    print("SKIP re-assessment scenario (LibreOffice not installed)")
print(f"\n{ok} tests passed")
