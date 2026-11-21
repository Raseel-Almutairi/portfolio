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

PBI = "../../nca-powerbi/"
EVIDENCE = "متوفر,تم التحقق,جزئي,بانتظار التحقق,مفقود,غير متوفر,لا ينطبق"
C = "Controls!$B$2:$B$690"
I = "Controls!$I$2:$I$690"
AE = "Controls!$AE$2:$AE$690"


def main_status(n):
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


def prepare(wb):
    if "README_DAX" in wb.sheetnames:
        del wb["README_DAX"]
    ws = wb["Controls"]
    for dv in ws.data_validations.dataValidation:
        dv.showErrorMessage = True
        dv.errorStyle = "stop"
        dv.errorTitle = "قيمة غير صالحة"
        dv.error = "اختر قيمة من القائمة."
        if str(dv.sqref) == "J2:J690":
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
        vals = {8: r["owner"], 9: r["status"], 10: r["evidence"], 11: r["gap"] or None, 12: r["action"] or None,
                13: date.fromisoformat(r["due"]) if r["due"] else None, 14: r["priority"] or None, 15: r["gap_status"] or None,
                30: "خارج نطاق أعمال الجهة (بيانات نموذجية)" if na else None,
                31: ("نعم" if r["na_approved"] else "لا") if na else None}
        for col, v in vals.items():
            ws.cell(n, col).value = v
        ws.cell(n, 13).number_format = "yyyy-mm-dd"


if __name__ == "__main__":
    controls = json.load(open("controls.json", encoding="utf-8"))
    wb = load_workbook(PBI + "4_Blank_Data.xlsx")
    prepare(wb)
    wb.save(PBI + "4_Blank_Data.xlsx")
    wb = load_workbook(PBI + "4_Blank_Data.xlsx")
    fill(wb, controls)
    wb.save(PBI + "3_Sample_Data.xlsx")
    print("Built 3_Sample_Data.xlsx and 4_Blank_Data.xlsx")
