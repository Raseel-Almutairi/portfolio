# Source and build: NCA tool

One source, `controls.json`, feeds the web page, the Excel register and the Power BI data.

| File | What it is |
|---|---|
| `controls.json` | The 689 items: control text, sample status, evidence, approval of "not applicable" (`na_approved`), findings |
| `guides.json` | The NCA guides used as references |
| `template.html` | The page layout, styles and logic. D3 is embedded, so the page loads nothing from the internet. |
| `nca_logic.py` | The calculation rules in Python, used by the tests |
| `base/register_v1.0.xlsx` | The Excel register before the v1.1 fixes. The patch always starts from it. |

## Build

```
python build.py                 # web page -> ../index.html
python patch_excel.py base/register_v1.0.xlsx ../NCA_Compliance_Register_Sample.xlsx ../NCA_Compliance_Register_Blank.xlsx 2026-11-21
python build_powerbi_data.py    # Power BI data -> ../../nca-powerbi/3_Sample_Data.xlsx and 4_Blank_Data.xlsx
```

Open each Excel file in Excel and save it, so the formulas are calculated. LibreOffice also works:
`soffice --headless --convert-to xlsx`.

## Test

```
python tests.py
```

Needs Python 3 with openpyxl, Node.js for the web checks, and LibreOffice for the scenario tests (skipped without it). The tests run on every push (GitHub Actions), after the web page is rebuilt from this folder and compared with the published one.
