"""Tests for the NCA tool (run from this folder: python tests.py).

Checks the calculation rules, the sample figures, and that the web page, the Excel register
and the Power BI data file hold the same data and give the same results.
The Excel checks read the values saved in the files, so run them after the files were calculated
(opened and saved in Excel, or recalculated with LibreOffice)."""
import json, subprocess, shutil, warnings
from collections import Counter
from openpyxl import load_workbook
from nca_logic import main_status, main_key, summary

warnings.filterwarnings("ignore")
controls = json.load(open("controls.json", encoding="utf-8"))
ok = 0


def check(name, cond):
    global ok
    assert cond, "FAILED: " + name
    ok += 1
    print("PASS", name)


r = lambda s, na=None: {"id": "X-1-1-1", "status": s, "na_approved": na}
# ---- rules
check("implemented + not applicable awaiting approval is not implemented", main_status([r("مطبق"), r("لا ينطبق", False)]) == "مطبق جزئيًا")
check("implemented + approved not applicable is implemented", main_status([r("مطبق"), r("لا ينطبق", True)]) == "مطبق")
check("unknown status is flagged, not 'not assessed'", main_status([r("مطبق جزئيا")]) == "حالة غير صالحة")
check("main key of a sub-control", main_key("CCC-2-3-P-1-6") == "CCC-2-3-P-1" and main_key("ECC-2-3-1-4") == "ECC-2-3-1")

# ---- sample figures (as of 2026-11-21); any change must be explained in CHANGELOG.md
s = summary(controls, "2026-11-21")
check("690 items, 298 main controls", len(controls) == 690 and s["mains"] == 298)
check("compliance 101 / 290 = 34.83%", (s["implemented"], s["denom"], s["compliance"]) == (101, 290, 0.3483))
check("272 open findings, 99 overdue on 2026-11-21", (s["open"], s["overdue"]) == (272, 99))
check("10 overdue on 2026-08-01", summary(controls, "2026-08-01")["overdue"] == 10)
check("9 not-applicable items awaiting approval, 27 closed findings to re-assess, 0 without date",
      (s["na_pending"], s["closed_reassess"], s["no_due"]) == (9, 27, 0))
check("approval is its own field, not part of the evidence status",
      all(x["evidence"] == "لا ينطبق" for x in controls if x["status"] == "لا ينطبق") and not any("معتمد" in x["evidence"] for x in controls))

# ---- web page (runs the page's own JavaScript in Node)
html = open("../index.html", encoding="utf-8").read()
check("web makes no external requests", "Content-Security-Policy" in html and "googleapis" not in html and "connect-src 'none'" in html)
if shutil.which("node"):
    w = json.loads(subprocess.run(["node", "web_calc.js", "../index.html", "", "2026-10-23T21:30:00Z"], capture_output=True, text=True, check=True).stdout)
    check("web figures = Python figures", (w["implemented"], w["denom"], w["open"], w["overdue"], w["na_pending"], w["closed_reassess"], w["no_due"]) ==
          (s["implemented"], s["denom"], s["open"], s["overdue"], s["na_pending"], s["closed_reassess"], s["no_due"]))
    check("web: implemented + pending exception is not implemented", w["rule_mixed_pending"] == "مطبق جزئيًا")
    check("web: all-pending main control stays in the denominator", w["rule_all_pending"] == 2)
    check("web: invalid status flagged", w["rule_invalid"] == "حالة غير صالحة")
    check("web search: 'استراتيجية' = 'إستراتيجية'", w["search_same"])
    check("web date uses Riyadh time (00:30 on 24 Oct is 24 Oct)", w["riyadh_0030"] == "2026-10-24")
else:
    print("SKIP web checks (Node.js not installed)")

# ---- Excel register and Power BI data hold the same data as the web
reg = load_workbook("../NCA_Compliance_Register_Sample.xlsx", data_only=True)
ws = reg["01 سجل الضوابط - Register"]
by_id = {x["id"]: x for x in controls}
diff = 0
for n in range(5, ws.max_row + 1):
    cid = ws.cell(n, 2).value
    if not cid:
        continue
    x = by_id.get(cid)
    if x is None:
        diff += 1
        continue
    due = ws.cell(n, 10).value
    row = (ws.cell(n, 5).value, ws.cell(n, 6).value, ws.cell(n, 7).value, due.date().isoformat() if due else "",
           ws.cell(n, 13).value or "", ws.cell(n, 14).value or "", (ws.cell(n, 16).value == "نعم") if x["status"] == "لا ينطبق" else None)
    diff += row != (x["owner"], x["status"], x["evidence"], x["due"], x["priority"], x["gap_status"], x["na_approved"])
check("Excel register = web data, field by field (690 items)", diff == 0)
check("Excel register text = source text (690 items)", all(ws.cell(n, 4).value == by_id[ws.cell(n, 2).value]["description"] for n in range(5, ws.max_row + 1) if ws.cell(n, 2).value in by_id))
check("text review status: all 690 item texts Verified (ECC, OSMACC, CSCC, TCC, CCC, OTCC, DCC)",
      Counter(x["text_review"] for x in controls) == Counter({"Verified": 690}))
reg_ids = [ws.cell(n, 2).value for n in range(5, ws.max_row + 1) if ws.cell(n, 2).value]
check("same IDs in the source and the Excel register: none missing, extra or repeated",
      len(reg_ids) == len(set(reg_ids)) == len(by_id) == len(controls) and set(reg_ids) == set(by_id))
mains = {}
for x in controls:
    mains.setdefault(main_key(x["id"]), []).append(x)
m = reg["07 الضوابط الرئيسية - Main"]
xl_main = {m.cell(n, 1).value: m.cell(n, 8).value for n in range(4, 302) if m.cell(n, 1).value}
check("Excel main-control status = web rule (298 main controls)", all(xl_main[k] in (main_status(v), "لا ينطبق - بانتظار الاعتماد") for k, v in mains.items()))
d = reg["06 لوحة المؤشرات - Dashboard"]
check("Excel dashboard: 34.83%, 272 open, 99 overdue", (round(d["B6"].value, 4), d["D6"].value, d["F6"].value) == (0.3483, 272, 99))
check("Excel dashboard: no data quality issues", d["B25"].value.startswith("جودة البيانات"))

pbi = load_workbook("../../nca-powerbi/3_Sample_Data.xlsx", data_only=True)
c = pbi["Controls"]
diff = 0
for n in range(2, c.max_row + 1):
    if not c.cell(n, 1).value:
        continue
    x = by_id.get(c.cell(n, 1).value)
    if x is None:
        diff += 1
        continue
    na = (c.cell(n, 31).value == "نعم") if x["status"] == "لا ينطبق" else None
    diff += (c.cell(n, 9).value, c.cell(n, 10).value, c.cell(n, 15).value or "", na) != (x["status"], x["evidence"], x["gap_status"], x["na_approved"])
check("Power BI data = web data (status, evidence, finding status, approval)", diff == 0)
pbi_ids = [c.cell(n, 1).value for n in range(2, c.max_row + 1) if c.cell(n, 1).value]
check("same IDs in the source and the Power BI data: none missing, extra or repeated",
      len(pbi_ids) == len(set(pbi_ids)) == len(by_id) and set(pbi_ids) == set(by_id))
pm = pbi["MainControls"]
check("Power BI main-control status = Excel register", all(xl_main.get(pm.cell(n, 1).value) == pm.cell(n, 5).value for n in range(2, 300)))
blank = load_workbook("../NCA_Compliance_Register_Blank.xlsx", data_only=True)
check("blank register: 298 main controls not assessed", Counter(blank["07 الضوابط الرئيسية - Main"].cell(n, 8).value for n in range(4, 302)) == Counter({"لم يُقيّم": 298}))
req = reg["02 المتطلبات - Requirements"]
check("new control CSCC-2-3-4 sits right after CSCC-2-3-1-8 in the register, the requirements and the main sheet",
      [ws.cell(n, 2).value for n in (267, 268, 269)] == [req.cell(n, 2).value for n in (267, 268, 269)] == ["CSCC-2-3-1-8", "CSCC-2-3-4", "CSCC-2-4-1-1"]
      and [m.cell(n, 1).value for n in (122, 123, 124)] == ["CSCC-2-3-1", "CSCC-2-3-4", "CSCC-2-4-1"]
      and all(ws.cell(n, 2).hyperlink.location.endswith(f"!B{n}") for n in (267, 268, 269, 694)))
check("no compliance rate (not an error) when every main control is excluded",
      summary([{"id": "X-1-1", "status": "لا ينطبق", "na_approved": True, "gap_status": "", "due": ""}], "2026-11-21")["compliance"] is None)
check("missing approval counts as pending", main_status([r("مطبق"), {"id": "X-1-1-2", "status": "لا ينطبق"}]) == "مطبق جزئيًا")

# One source: a change in controls.json reaches the Excel register (patch run in a temporary folder)
import os, tempfile
with tempfile.TemporaryDirectory() as tmp:
    changed_ = json.loads(json.dumps(controls))
    changed_[0]["status"], changed_[0]["owner"] = "غير مطبق", "تقنية المعلومات"
    json.dump(changed_, open(os.path.join(tmp, "controls.json"), "w", encoding="utf-8"), ensure_ascii=False)
    subprocess.run(["python3" if shutil.which("python3") else "python", os.path.abspath("patch_excel.py"), os.path.abspath("base/register_v1.0.xlsx"),
                    os.path.join(tmp, "s.xlsx"), os.path.join(tmp, "b.xlsx"), "2026-11-21"], cwd=tmp, check=True, capture_output=True)
    w_ = load_workbook(os.path.join(tmp, "s.xlsx"))["01 سجل الضوابط - Register"]
    row0 = next(n for n in range(5, w_.max_row + 1) if w_.cell(n, 2).value == changed_[0]["id"])
    check("a change in controls.json reaches the Excel register", (w_.cell(row0, 6).value, w_.cell(row0, 5).value) == ("غير مطبق", "تقنية المعلومات"))

soffice = shutil.which("soffice") or shutil.which("libreoffice")
if soffice:
    # A target date pasted as text must not disappear: it is flagged in the findings sheet and in the data quality line
    with tempfile.TemporaryDirectory() as tmp:
        wb = load_workbook("../NCA_Compliance_Register_Sample.xlsx")
        w_ = wb["01 سجل الضوابط - Register"]
        n = next(n for n in range(5, w_.max_row + 1) if w_.cell(n, 6).value == "غير مطبق" and w_.cell(n, 14).value != "مغلقة")
        w_.cell(n, 10).value = "2026-01-01"
        wb.save(os.path.join(tmp, "t.xlsx"))
        subprocess.run([soffice, "--headless", "--convert-to", "xlsx", "--outdir", os.path.join(tmp, "o"), os.path.join(tmp, "t.xlsx")], check=True, capture_output=True, timeout=300)
        out = load_workbook(os.path.join(tmp, "o", "t.xlsx"), data_only=True)
        k_ = [c.value for c in out["05 متابعة الملاحظات - Findings"]["K"]]
        check("date written as text is flagged, not hidden", "تاريخ غير صالح" in k_ and out["06 لوحة المؤشرات - Dashboard"]["B25"].value.startswith("تنبيه: 1 "))
else:
    print("SKIP text-date scenario (LibreOffice not installed)")
print(f"\n{ok} tests passed")
