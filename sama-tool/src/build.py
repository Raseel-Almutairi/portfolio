"""Builds the SAMA CSF demo from one source.

Run from this folder:  python build.py
Outputs (one level up): index.html, SAMA_CSF_Assessment_Sample.xlsx, SAMA_CSF_Assessment_Blank.xlsx

Source of truth:
- sama_official.json / official.py : SAMA CSF v1.0 text (principles, objectives, control considerations, Table 1)
- evcc.py : required evidence per control consideration (author's derivation)
- data.py / model.py : sample answers, levels, actions and the assessment date (AS_OF)
Requires Python 3 and openpyxl. Open the Excel files in Excel to calculate the formulas.
"""
import runpy

runpy.run_path("build_web.py")
runpy.run_path("build_excel.py")
print("Built index.html and the two Excel files.")
