# Changelog: NCA tool

## v1.1 (2026-11-21): fixes after the technical review

### Changes by FIX number

| FIX | Change |
|---|---|
| FIX-00 | One source (`src/controls.json`) for the web, the Excel register and the Power BI data, with build scripts and 24 tests (`src/tests.py`). The tests check, field by field, that the three hold the same data and give the same results. The 9 items that differed (web: «لا ينطبق - بانتظار الاعتماد», Excel: «معتمد») were settled on the web version. |
| FIX-01 + 04 | Approval of "not applicable" is now its own field (`na_approved` in the web, column P in Excel, `NAApproved` in Power BI), no longer part of the evidence status. An item awaiting approval is not excluded when the main control's status is set: implemented + pending exception gives «مطبق جزئيًا». A main control leaves the denominator only if all its items are approved as not applicable. The "pending" indicator works now; it showed 0 before because the field it read did not exist. |
| FIX-02 | Every Excel list now blocks invalid values (Stop alert). Values pasted around the list are caught: the main control shows «حالة غير صالحة» instead of «لم يُقيّم», and a data quality line on the dashboard counts them. The evidence list is the same in the register and the Power BI data. |
| FIX-03 | One assessment date, in Riyadh time. The web demo is pinned to 21 November 2026, so its numbers no longer age and it no longer uses UTC. In Excel the date is in the dashboard (cell D26; blank = today), and all 36 `TODAY()` were replaced with it. |
| FIX-05 | Open findings without a target date have their own counter (web and Excel), and Excel marks them «بلا تاريخ مستهدف». |
| FIX-06 | Closing a finding does not change compliance. The 27 closed findings whose control is still a gap are shown as «بانتظار إعادة التقييم», with a counter. |
| FIX-10 | The "all frameworks" figure is labelled as a comparison only, not a single regulatory compliance rate. |
| FIX-14 | Arabic search ignores diacritics, tatweel, hamza forms, alef maqsura and taa marbuta, so «استراتيجية» and «إستراتيجية» give the same results. Search also covers status, owner and corrective action. |
| FIX-21 | The dashboard total compliance uses the same rule as the KPI. The file author is no longer `openpyxl`. |
| FIX-22 | Power BI sample data rebuilt from the same source, with the `NAJustification` and `NAApproved` columns the model expects (they were missing), the corrected main-control rule and Stop alerts. `README_DAX` was removed from the data files. |
| FIX-23 | Print layout (tables are no longer cut). Rows open with Enter or Space, and tabs move with the arrow keys. |

### Figures before and after (sample data, as of 2026-11-21)

| Figure | Before | After | Reason |
|---|---|---|---|
| Compliance (all frameworks) | 102 / 285 = 35.79% | 101 / 289 = 34.95% | FIX-01: CSCC-4-1-1 is no longer «مطبق», and 4 main controls with pending exceptions stay in the denominator |
| Implemented / partial / not implemented (main) | 102 / 147 / 36 | 101 / 148 / 36 | FIX-01 |
| Not applicable awaiting approval | 0 (field missing) | 9 | FIX-01 + 04 |
| Open findings | 271 | 271 | - |
| Overdue | 99 on 21 Nov, changes every day | 99 (pinned date) | FIX-03 |
| Closed, control still a gap | not shown | 27 | FIX-06 |
| Open without target date | not shown | 0 | FIX-05 |
| Excel register compliance | 35.79% | 34.95% (same as web) | FIX-00 + 01 |

### Not done, and why
- **Power BI:** the report (`.pbix`), the template (`.pbit`) and the PDF were not rebuilt, because Power BI Desktop runs only on Windows. The model was not changed either: the DAX measures still use `TODAY()`, and the new indicators were not added. Open the report in Power BI Desktop and press Refresh to load the new data. These were not tested.
- **Organization profile (FIX-10 in full):** it needs saved data.
- **Text review (FIX-15):** the 689 item texts and page numbers still need a human review against the NCA guides.
- **Mandatory approver and approval date for exceptions:** the register has no columns for them yet.
- **Arabic normalization inside Excel formulas:** not added, because the Stop alert and the data quality check catch these values first.
- **Tested in LibreOffice, not Microsoft Excel:** the Stop alert and pasting a value.
