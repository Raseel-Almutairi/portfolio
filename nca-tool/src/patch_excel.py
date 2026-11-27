"""Applies the v1.1 fixes to the NCA Excel register by editing its XML directly.

The register has charts and data validations that openpyxl would drop on save, so the
fixes are applied to the sheet XML instead. Run:  python patch_excel.py base/register_v1.0.xlsx ../NCA_Compliance_Register_Sample.xlsx ../NCA_Compliance_Register_Blank.xlsx 2026-11-21
(base/register_v1.0.xlsx is the register before the fixes; the script always starts from it.)
- AS_OF (yyyy-mm-dd) pre-fills the assessment date in the sample file.
- The blank file is made from the patched sample by clearing every input cell, so both share one structure.
- Approval of "not applicable" is taken from controls.json (field na_approved), so Excel and the web match.
"""
import json, re, sys, zipfile
from datetime import date
from html import escape, unescape

src, dst, dst_blank, AS_OF = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
REG, MAIN, DASH = "'01 سجل الضوابط - Register'", "'07 الضوابط الرئيسية - Main'", "'06 لوحة المؤشرات - Dashboard'"
zin = zipfile.ZipFile(src)
files = {n: zin.read(n) for n in zin.namelist()}
X = lambda n: files[n].decode("utf-8")
def put(n, s): files[n] = s.encode("utf-8")
def esc(f): return escape(f, quote=False)

# ---------- styles: a yellow date input and a right-aligned text line
st = X("xl/styles.xml")
m = re.search(r'<cellXfs count="(\d+)">(.*?)</cellXfs>', st, re.S)
xfs = re.findall(r'<xf [^>]*?(?:/>|>.*?</xf>)', m.group(2), re.S)
n0 = len(xfs)
date_in = xfs[114].replace('numFmtId="0"', 'numFmtId="165"').replace('<xf ', '<xf applyNumberFormat="1" ', 1)
line = xfs[121].replace('horizontal="center" vertical="center"', 'horizontal="right" vertical="center" wrapText="1"')
st = st.replace(m.group(0), f'<cellXfs count="{n0 + 2}">' + m.group(2) + date_in + line + '</cellXfs>')
put("xl/styles.xml", st)
S_DATE, S_LINE, S_LABEL = n0, n0 + 1, 113

# ---------- shared strings (to find control IDs)
ss = [unescape(re.sub(r"<[^>]+>", "", x)) for x in re.findall(r"<si>(.*?)</si>", X("xl/sharedStrings.xml"), re.S)]

# ---------- new controls: an item in controls.json that the base register does not have (e.g. CSCC-2-3-4,
# new in CSCC-2:2026) gets a row right after the item before it, in the register (01), the requirements (02)
# and, for a new main control, the main-controls sheet (07). Rows below move down one.
from nca_logic import main_key
controls = {r["id"]: r for r in json.load(open("controls.json", encoding="utf-8"))}
ROW_RE = r'<row r="(\d+)"[^>]*?(?:/>|>.*?</row>)'
def id_rows(xml, col="B"):
    out = {}
    for mm in re.finditer(r'<c r="%s(\d+)"[^>]*?t="(s|inlineStr)"[^>]*>(?:<v>(\d+)</v>|<is><t>([^<]*)</t></is>)</c>' % col, xml):
        out[ss[int(mm.group(3))] if mm.group(2) == "s" else unescape(mm.group(4))] = int(mm.group(1))
    return out
def renumber(row_xml, old, new, own_refs=""):
    row_xml = re.sub(r'(<row r=")%d"' % old, r'\g<1>%d"' % new, row_xml, count=1)
    row_xml = re.sub(r'(<c r="[A-Z]+)%d"' % old, lambda k: f'{k.group(1)}{new}"', row_xml)
    if own_refs:  # formulas that point at their own row (A5, C5 ...): move them with the row
        row_xml = re.sub(r'(?<![$A-Z])([%s])%d(?!\d)' % (own_refs, old), lambda k: f"{k.group(1)}{new}", row_xml)
    return row_xml
def insert_after(xml, after, new_row_of, own_refs=""):
    """Moves rows > after down one and puts new_row_of(template_row_xml_renumbered) at after+1."""
    rows = {int(mm.group(1)): mm.group(0) for mm in re.finditer(ROW_RE, xml, re.S)}
    tpl = renumber(rows[after], after, after + 1, own_refs)
    def mv(mm):
        n = int(mm.group(1))
        if n < after:
            return mm.group(0)
        if n == after:
            return mm.group(0) + new_row_of(tpl)
        return renumber(mm.group(0), n, n + 1, own_refs)
    return re.sub(ROW_RE, mv, xml, flags=re.S)
def set_inline(row_xml, ref, text):
    pat = re.compile(r'<c r="%s"( s="\d+")?[^>]*?(?:/>|>.*?</c>)' % ref, re.S)
    mm = pat.search(row_xml)
    assert mm, ref
    return row_xml[:mm.start()] + '<c r="%s"%s t="inlineStr"><is><t>%s</t></is></c>' % (ref, mm.group(1) or "", escape(text, quote=False)) + row_xml[mm.end():]
def shift_links(xml, after, target_sheet):
    def mv(mm):
        a, b = int(mm.group(1)), int(mm.group(2))
        return mm.group(0).replace(f'ref="B{a}"', f'ref="B{a + 1 if a > after else a}"').replace(f"'!B{b}\"", f"'!B{b + 1 if b > after else b}\"")
    xml = re.sub(r'<hyperlink ref="B(\d+)" location="[^"]*!B(\d+)"[^>]*/>', mv, xml)
    return xml.replace("</hyperlinks>", f'<hyperlink ref="B{after + 1}" location="\'{target_sheet}\'!B{after + 1}" display="{new_id}"/></hyperlinks>')
reg, req, main = X("xl/worksheets/sheet2.xml"), X("xl/worksheets/sheet3.xml"), X("xl/worksheets/sheet8.xml")
order = list(controls)
new_mains = 0
for new_id in [i for i in order if i not in id_rows(reg)]:
    r, prev = controls[new_id], order[order.index(new_id) - 1]
    at = id_rows(reg)[prev]
    # 01 register: last (empty) row dropped so the sheet still ends at row 1000
    reg = insert_after(reg, at, lambda t: set_inline(set_inline(t, f"B{at + 1}", new_id), f"O{at + 1}", main_key(new_id)))
    reg = re.sub(r'<row r="1001"[^>]*?(?:/>|>.*?</row>)', "", reg, flags=re.S)
    reg = shift_links(reg, at, "02 المتطلبات - Requirements")
    # 02 requirements
    ev = "\n".join("• " + x.strip() for x in r["req_evidence"].split("•") if x.strip())
    docs = "\n".join(f"{k}: {r[f]}" for k, f in (("سياسة", "req_policy"), ("معيار", "req_standard"), ("إجراء", "req_procedure"), ("خطة", "req_plan"), ("وثائق أخرى", "req_other")) if r[f]) or "—"
    def req_row(t, n=at + 1):
        t = set_inline(t, f"B{n}", new_id)
        for col, v in (("C", r["req_type"]), ("D", docs), ("E", ev), ("F", r["ref_guide"])):
            t = set_inline(t, f"{col}{n}", v)
        return re.sub(r'(<c r="G%d"[^>]*?)(?:/>|>.*?</c>)' % n, lambda k: f'{k.group(1)}><v>{r["ref_page"]}</v></c>', t, flags=re.S)
    assert id_rows(req)[prev] == at, "requirements rows must match register rows"
    req = insert_after(req, at, req_row)
    req = shift_links(req, at, "01 سجل الضوابط - Register")
    req = re.sub(r'<dimension ref="A1:G(\d+)"/>', lambda k: f'<dimension ref="A1:G{int(k.group(1)) + 1}"/>', req)
    # 07 main controls
    mk = main_key(new_id)
    if mk not in id_rows(main, "A"):
        pm = id_rows(main, "A")[main_key(prev)]
        main = insert_after(main, pm, lambda t: set_inline(t, f"A{pm + 1}", mk), own_refs="A-H")
        main = re.sub(r'<dimension ref="A1:H(\d+)"/>', lambda k: f'<dimension ref="A1:H{int(k.group(1)) + 1}"/>', main)
        new_mains += 1
# the sequence formula in L counts findings above each row
reg = re.sub(r'(<c r="L(\d+)"[^>]*><f>)IF\(OR\(B\d+="".*?</f>', lambda k: k.group(1) + esc(f'IF(OR(B{k.group(2)}="",NOT(OR(F{k.group(2)}="مطبق جزئيًا",F{k.group(2)}="غير مطبق"))),"",COUNT($L$4:L{int(k.group(2)) - 1})+1)') + "</f>", reg)
# 02 requirements: the guide page of every item comes from controls.json too
def set_page(mm):
    row = mm.group(0)
    ids = id_rows(row)
    r = controls.get(next(iter(ids))) if ids else None
    if not r or not r.get("ref_page"):
        return row
    n = mm.group(1)
    return re.sub(r'(<c r="G%s"[^>]*?)(?: t="[a-zA-Z]+")?(?:/>|>.*?</c>)' % n, lambda k: f'{k.group(1)}><v>{r["ref_page"]}</v></c>', row, count=1, flags=re.S)
req = re.sub(ROW_RE, set_page, req, flags=re.S)
put("xl/worksheets/sheet3.xml", req)
MAIN_LAST = 300 + new_mains

# ---------- 01 Register
def set_cell(xml, ref, text):
    pat = re.compile(r'<c r="%s"( s="\d+")?[^>]*?(?:/>|>.*?</c>)' % ref, re.S)
    mm = pat.search(xml)
    new = '<c r="%s"%s t="inlineStr"><is><t>%s</t></is></c>' % (ref, mm.group(1) or "" if mm else "", escape(text, quote=False))
    assert mm, ref
    return xml[:mm.start()] + new + xml[mm.end():]
# every register field comes from controls.json (one source): text, owner, status, evidence, finding, date, priority, approval
FIELDS = {"A": "framework", "C": "domain", "D": "description", "E": "owner", "F": "status", "G": "evidence", "H": "gap",
          "I": "action", "J": "due", "M": "priority", "N": "gap_status", "P": "na_approved"}
def cell_xml(ref, style, v):
    if v in (None, ""):
        return f'<c r="{ref}"{style}/>'
    if isinstance(v, date):
        return f'<c r="{ref}"{style}><v>{(v - date(1899, 12, 30)).days}</v></c>'
    return f'<c r="{ref}"{style} t="inlineStr"><is><t>{escape(str(v), quote=False)}</t></is></c>'
def fill_row(m_):
    row_xml, n = m_.group(0), m_.group(1)
    b = id_rows(row_xml)
    r = controls.get(next(iter(b))) if b else None
    if not r:
        return row_xml
    global changed
    changed += 1
    for col, key in FIELDS.items():
        v = r[key]
        if key == "due":
            v = date.fromisoformat(v) if v else None
        if key == "na_approved":
            v = ("نعم" if v is True else "لا") if r["status"] == "لا ينطبق" else None
        pat = re.compile(r'<c r="%s%s"( s="\d+")?[^>]*?(?:/>|>.*?</c>)' % (col, n), re.S)
        c_ = pat.search(row_xml)
        assert c_, (col, n)
        row_xml = row_xml[:c_.start()] + cell_xml(f"{col}{n}", c_.group(1) or "", v) + row_xml[c_.end():]
    return row_xml
changed = 0
reg = re.sub(r'<row r="(\d+)"[^>]*>.*?</row>', fill_row, reg, flags=re.S)
# evidence list: approval of "not applicable" now lives only in column P
reg = reg.replace("لا ينطبق - معتمد,لا ينطبق - بانتظار الاعتماد", "لا ينطبق")
# every list blocks invalid typing (Stop alert)
def stop(tag):
    tag = re.sub(r'\s(errorStyle|showErrorMessage|errorTitle|error)="[^"]*"', "", tag)
    return tag.replace("<dataValidation ", '<dataValidation errorStyle="stop" showErrorMessage="1" errorTitle="قيمة غير صالحة" error="اختر قيمة من القائمة." ', 1).replace("<x14:dataValidation ", '<x14:dataValidation errorStyle="stop" showErrorMessage="1" errorTitle="قيمة غير صالحة" error="اختر قيمة من القائمة." ', 1)
reg = re.sub(r"<(?:x14:)?dataValidation [^>]*>", lambda k: stop(k.group(0)), reg)
reg = re.sub(r'error="اختر قيمة من القائمة\." (type="date")', r'error="أدخل تاريخاً صحيحاً." \1', reg)
put("xl/worksheets/sheet2.xml", reg)
# the framework pickers in the dashboard and the documents sheet also block invalid values
for n_ in [f"xl/worksheets/sheet{i}.xml" for i in (1, 3, 4, 5, 6, 7, 8)]:
    put(n_, re.sub(r"<(?:x14:)?dataValidation [^>]*>", lambda k: stop(k.group(0)), X(n_)))

# ---------- 07 Main: a control with a not-applicable item awaiting approval is not "implemented"
def main_f(n):
    ok = f'COUNTIFS({REG}!$O$5:$O$1000,A{n},{REG}!$F$5:$F$1000,"لا ينطبق",{REG}!$P$5:$P$1000,"نعم")'
    filled = f'COUNTIFS({REG}!$O$5:$O$1000,A{n},{REG}!$F$5:$F$1000,"<>")'
    return (f'IF({filled}>D{n},"حالة غير صالحة",IF(D{n}=0,"لم يُقيّم",IF(D{n}<C{n},"تقييم غير مكتمل",IF(G{n}=C{n},IF({ok}=C{n},"لا ينطبق","لا ينطبق - بانتظار الاعتماد"),'
            f'IF(AND(E{n}=C{n}-G{n},{ok}=G{n}),"مطبق",IF(F{n}=C{n}-G{n},"غير مطبق","مطبق جزئيًا"))))))')
main, k = re.subn(r'(<c r="H(\d+)"[^>]*><f>)IF\(D\d+=0.*?(</f>)', lambda mm: mm.group(1) + esc(main_f(mm.group(2))) + mm.group(3), main)
assert k == 297 + new_mains, k
put("xl/worksheets/sheet8.xml", main)

# ---------- 05 Findings: closed findings and missing dates are shown, not hidden
fnd = X("xl/worksheets/sheet6.xml")
pat = re.compile(r'IF\(C(\d+)="","",IF\(AND\(ISNUMBER\(F\1\),H\1&lt;&gt;"مغلقة",F\1&lt;TODAY\(\)\),"متأخرة",""\)\)')
fnd, k = pat.subn(lambda mm: esc(f'IF(C{mm.group(1)}="","",IF(H{mm.group(1)}="مغلقة","مغلقة - أعد تقييم الضابط",IF(F{mm.group(1)}="","بلا تاريخ مستهدف",IF(NOT(ISNUMBER(F{mm.group(1)})),"تاريخ غير صالح",IF(F{mm.group(1)}<{DASH}!$M$26,"متأخرة","")))))'), fnd)
assert k == 16, k
fnd = fnd.replace('<f t="shared" ca="1"', '<f t="shared"')
put("xl/worksheets/sheet6.xml", fnd)

# ---------- 06 Dashboard
d = X("xl/worksheets/sheet7.xml")
d = re.sub(r"(Main'!\$[A-H]\$4:\$[A-H]\$)300(?!\d)", lambda k: f"{k.group(1)}{MAIN_LAST}", d)
n_today = d.count("TODAY()")
d = d.replace("TODAY()", "$M$26")
d = re.sub(r'(<c r="H41"[^>]*><f>).*?(</f>)', lambda mm: mm.group(1) + esc(f'IFERROR(D41/(COUNTA({MAIN}!$A$4:$A${MAIN_LAST})-G41),"")') + mm.group(2), d)
R = lambda c: f"{REG}!${c}$5:${c}$1000"
def bad(col, vals):
    arr = "{" + ",".join(f'"{v}"' for v in vals) + "}"
    return f'SUMPRODUCT(({R(col)}<>"")*ISNA(MATCH({R(col)},{arr},0)))'
dq = "+".join([bad("F", ["مطبق", "مطبق جزئيًا", "غير مطبق", "لا ينطبق"]),
               bad("G", ["متوفر", "تم التحقق", "جزئي", "بانتظار التحقق", "مفقود", "غير متوفر", "لا ينطبق"]),
               bad("M", ["حرجة", "عالية", "متوسطة", "منخفضة"]), bad("N", ["مفتوحة", "قيد المعالجة", "بانتظار التحقق", "مغلقة"]), bad("P", ["نعم", "لا"]),
               f'SUMPRODUCT(({R("J")}<>"")*NOT(ISNUMBER({R("J")})))'])
dq_f = f'IF(({dq})=0,"جودة البيانات: لا توجد قيم غير صالحة في سجل الضوابط.","تنبيه: "&IF(({dq})=1,"قيمة واحدة غير صالحة",IF(({dq})=2,"قيمتان غير صالحتين",({dq})&IF(AND(({dq})>=3,({dq})<=10)," قيم غير صالحة"," قيمة غير صالحة")))&" في سجل الضوابط (الحالة أو الأدلة أو الأولوية أو حالة الملاحظة أو اعتماد عدم الانطباق أو تاريخ مكتوب كنص). صحّحها قبل اعتماد المؤشرات.")'
gap2 = lambda extra: (f'COUNTIFS({R("A")},$M$3,{R("F")},"مطبق جزئيًا"{extra})+COUNTIFS({R("A")},$M$3,{R("F")},"غير مطبق"{extra})')
cnt_f = (f'"«لا ينطبق» بانتظار الاعتماد: "&COUNTIFS({R("A")},$M$3,{R("F")},"لا ينطبق",{R("P")},"<>نعم")'
         f'&"   |   ملاحظات مغلقة بانتظار إعادة التقييم: "&({gap2(f",{R(chr(78))},\"مغلقة\"")})'
         f'&"   |   ملاحظات مفتوحة بلا تاريخ مستهدف: "&({gap2(f",{R(chr(78))},\"<>مغلقة\",{R(chr(74))},\"\"")})')
asof_v = ""
if AS_OF:
    asof_v = "<v>%d</v>" % (date.fromisoformat(AS_OF) - date(1899, 12, 30)).days
rows = (f'<row r="25" spans="2:13" ht="30" customHeight="1"><c r="B25" s="{S_LINE}" t="str"><f>{esc(dq_f)}</f></c></row>'
        f'<row r="26" spans="2:13" ht="30" customHeight="1"><c r="B26" s="{S_LABEL}" t="inlineStr"><is><t>تاريخ التقييم (فارغ = اليوم)</t></is></c>'
        f'<c r="C26" s="{S_LABEL}"/><c r="D26" s="{S_DATE}">{asof_v}</c><c r="E26" s="{S_DATE}"/>'
        f'<c r="F26" s="{S_LINE}" t="str"><f>{esc(cnt_f)}</f></c>'
        f'<c r="M26" s="{S_DATE}"><f>IF(D26="",TODAY(),D26)</f></c></row>')
d = d.replace('<row r="27"', rows + '<row r="27"', 1)
d = d.replace('<mergeCells count="', '<mergeCells count="X', 1)
mc = re.search(r'<mergeCells count="X(\d+)">', d)
d = d.replace(mc.group(0), f'<mergeCells count="{int(mc.group(1)) + 4}"><mergeCell ref="B25:I25"/><mergeCell ref="B26:C26"/><mergeCell ref="D26:E26"/><mergeCell ref="F26:I26"/>')
put("xl/worksheets/sheet7.xml", d)

# ---------- workbook: recalculate on open; drop the stale calc chain; author
wbx = X("xl/workbook.xml").replace('<calcPr calcId="191029"', '<calcPr calcId="191029" fullCalcOnLoad="1"')
put("xl/workbook.xml", wbx)
files.pop("xl/calcChain.xml", None)
put("xl/_rels/workbook.xml.rels", re.sub(r'<Relationship [^>]*calcChain[^>]*/>', "", X("xl/_rels/workbook.xml.rels")))
put("[Content_Types].xml", re.sub(r'<Override [^>]*calcChain[^>]*/>', "", X("[Content_Types].xml")))
core = X("docProps/core.xml")
core = re.sub(r"<dc:creator>.*?</dc:creator>", "<dc:creator>Raseel Almutairi</dc:creator>", core)
core = re.sub(r"<cp:lastModifiedBy>.*?</cp:lastModifiedBy>", "<cp:lastModifiedBy>Raseel Almutairi</cp:lastModifiedBy>", core)
put("docProps/core.xml", core)

def save(path):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for n in zin.namelist():
            if n in files:
                z.writestr(n, files[n])
save(dst)
print(f"{dst}: {changed} rows filled from controls.json, {n_today} TODAY() replaced by the assessment date")

# ---------- blank: clear the inputs (register answers, owners list, assessment date); default view ECC
def clear(xml, cols, first):
    return re.sub(r'<c r="([A-Z]+)(\d+)"( s="\d+")?[^>]*?(?:/>|>.*?</c>)',
                  lambda k: f'<c r="{k.group(1)}{k.group(2)}"{k.group(3) or ""}/>' if k.group(1) in cols and int(k.group(2)) >= first else k.group(0), xml, flags=re.S)
put("xl/worksheets/sheet2.xml", clear(X("xl/worksheets/sheet2.xml"), {"E", "F", "G", "H", "I", "J", "K", "M", "N", "P"}, 5))
put("xl/worksheets/sheet5.xml", clear(X("xl/worksheets/sheet5.xml"), {"A"}, 2))
d = X("xl/worksheets/sheet7.xml")
d = set_cell(d, "D3", "الضوابط الأساسية للأمن السيبراني (ECC)")
d = re.sub(r'(<c r="D26" s="\d+">)<v>\d+</v>(</c>)', r"\1\2", d)
put("xl/worksheets/sheet7.xml", d)
save(dst_blank)
print(f"{dst_blank}: inputs cleared")
