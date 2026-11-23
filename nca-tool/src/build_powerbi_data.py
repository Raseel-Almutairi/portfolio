"""Builds the two Power BI data files from controls.json (one source for web, Excel and Power BI).

Run from this folder:  python build_powerbi_data.py
- ../../nca-powerbi/4_Blank_Data.xlsx  : structure, formulas and lists (inputs empty)
- ../../nca-powerbi/3_Sample_Data.xlsx : the same file filled with the sample data from controls.json
Fixes: main-control status treats a "not applicable" item awaiting approval as not met (FIX-01),
invalid statuses are flagged (FIX-02), every list blocks invalid values, one evidence list for all tools.
"""
import json
from datetime import date
from openpyxl import load_workbook

import re
from copy import copy
from nca_logic import main_key

PBI = "../../nca-powerbi/"
EVIDENCE = "متوفر,تم التحقق,جزئي,بانتظار التحقق,مفقود,غير متوفر,لا ينطبق"
LAST = 690  # last row of the Controls table; set by add_new_controls()
C = lambda: f"Controls!$B$2:$B${LAST}"
I = lambda: f"Controls!$I$2:$I${LAST}"
AE = lambda: f"Controls!$AE$2:$AE${LAST}"


def main_status(n):
    C, I, AE = globals()["C"](), globals()["I"](), globals()["AE"]()
    total = f"COUNTIFS({C},A{n})"
    filled = f'({total}-COUNTIFS({C},A{n},{I},""))'
    valid = "+".join(f'COUNTIFS({C},A{n},{I},"{s}")' for s in ("مطبق", "مطبق جزئيًا", "غير مطبق", "لا ينطبق"))
    na = f'COUNTIFS({C},A{n},{I},"لا ينطبق")'
    ok = f'COUNTIFS({C},A{n},{I},"لا ينطبق",{AE},"نعم")'
    impl = f'COUNTIFS({C},A{n},{I},"مطبق")'
    noimpl = f'COUNTIFS({C},A{n},{I},"غير مطبق")'
    return (f'=IF({filled}>({valid}),"حالة غير صالحة",IF({filled}=0,"لم يُقيّم",IF({filled}<{total},"تقييم غير مكتمل",'
            f'IF({na}={total},IF({ok}={total},"لا ينطبق","لا ينطبق - بانتظار الاعتماد"),'
            f'IF(AND({impl}={total}-{na},{ok}={na}),"مطبق",IF({noimpl}={total}-{na},"غير مطبق","مطبق جزئيًا"))))))')


def copy_style(src, dst):
    for a, b in zip(src, dst):
        b._style = copy(a._style)


def add_new_controls(wb, controls):
    """Appends controls.json items the file does not have yet (e.g. CSCC-2-3-4, new in CSCC-2:2026),
    and their main control, then widens every range to the new last row."""
    global LAST
    ws, m = wb["Controls"], wb["MainControls"]
    have = {ws.cell(n, 1).value for n in range(2, ws.max_row + 1)}
    mains = {m.cell(n, 1).value for n in range(2, m.max_row + 1)}
    for r in controls:
        if r["id"] in have:
            continue
        code = r["framework"].split("(")[-1].rstrip(")")
        like = next(n for n in range(2, ws.max_row + 1) if ws.cell(n, 4).value == code)
        n = ws.max_row + 1
        copy_style(ws[like], ws[n])
        vals = {1: r["id"], 2: main_key(r["id"]), 3: r["framework"], 4: code, 5: ws.cell(like, 5).value, 6: r["domain"], 7: r["description"],
                16: f'=IF(OR(I{n}="مطبق جزئيًا",I{n}="غير مطبق"),1,0)', 17: r["req_type"], 18: r["req_policy"], 19: r["req_standard"],
                20: r["req_procedure"], 21: r["req_plan"], 22: r["req_other"], 23: r["req_evidence"], 24: r["ref_guide"], 25: r["ref_page"],
                26: r["ecc_sub"], 27: r["ecc_sub_name"], 28: r["ecc_basis"], 29: r["ecc_ref"]}
        for col, v in vals.items():
            ws.cell(n, col).value = v if v != "" else None
        if main_key(r["id"]) not in mains:
            k = m.max_row + 1
            ml = next(j for j in range(2, m.max_row + 1) if m.cell(j, 3).value == code)
            copy_style(m[ml], m[k])
            for col in (1, 2, 3, 4):
                m.cell(k, col).value = m.cell(ml, col).value
            m.cell(k, 1).value = main_key(r["id"])
            mains.add(main_key(r["id"]))
    LAST = ws.max_row
    ws.tables["Controls"].ref = f"A1:AE{LAST}"
    m.tables["MainControls"].ref = f"A1:G{m.max_row}"
    for dv in ws.data_validations.dataValidation:
        dv.sqref = re.sub(r"(\d+):([A-Z]+)\d+$", lambda k: f"{k.group(1)}:{k.group(2)}{LAST}", str(dv.sqref))
    for j in range(2, m.max_row + 1):
        m.cell(j, 6).value = f"=COUNTIFS({C()},A{j})"
        m.cell(j, 7).value = f'=COUNTIFS({C()},A{j},{I()},"مطبق")'


def prepare(wb, controls):
    if "README_DAX" in wb.sheetnames:
        del wb["README_DAX"]
    add_new_controls(wb, controls)
    ws = wb["Controls"]
    for dv in ws.data_validations.dataValidation:
        dv.showErrorMessage = True
        dv.errorStyle = "stop"
        dv.errorTitle = "قيمة غير صالحة"
        dv.error = "اختر قيمة من القائمة."
        if str(dv.sqref).startswith("J2:"):
            dv.formula1 = f'"{EVIDENCE}"'
    m = wb["MainControls"]
    for n in range(2, m.max_row + 1):
        if m.cell(n, 1).value:
            m.cell(n, 5).value = main_status(n)
    wb.properties.creator = "Raseel Almutairi"
    wb.properties.lastModifiedBy = "Raseel Almutairi"


def fill(wb, controls):
    ws = wb["Controls"]
    by_id = {r["id"]: r for r in controls}
    for n in range(2, ws.max_row + 1):
        r = by_id.get(ws.cell(n, 1).value)
        if not r:
            continue
        na = r["status"] == "لا ينطبق"
        vals = {7: r["description"], 8: r["owner"], 9: r["status"], 10: r["evidence"], 11: r["gap"] or None, 12: r["action"] or None,
                13: date.fromisoformat(r["due"]) if r["due"] else None, 14: r["priority"] or None, 15: r["gap_status"] or None,
                30: "خارج نطاق أعمال الجهة (بيانات نموذجية)" if na else None,
                31: ("نعم" if r["na_approved"] else "لا") if na else None}
        for col, v in vals.items():
            ws.cell(n, col).value = v
        ws.cell(n, 13).number_format = "yyyy-mm-dd"


if __name__ == "__main__":
    controls = json.load(open("controls.json", encoding="utf-8"))
    wb = load_workbook(PBI + "4_Blank_Data.xlsx")
    prepare(wb, controls)
    wb.save(PBI + "4_Blank_Data.xlsx")
    wb = load_workbook(PBI + "4_Blank_Data.xlsx")
    fill(wb, controls)
    wb.save(PBI + "3_Sample_Data.xlsx")
    print("Built 3_Sample_Data.xlsx and 4_Blank_Data.xlsx")
