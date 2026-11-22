# Changelog: NCA tool

## v1.3 (2026-11-22): ECC text review (FIX-15)

- The 176 ECC item texts were compared one by one with the official NCA guide (GECC-2:2026, Arabic). The guide pages were read with OCR, compared automatically, and every difference was checked on the page image.
- 151 matched, and 25 were corrected to the guide's wording. Most of them had been shortened; a few had a missing word (for example «الخارجية» in ECC-2-15-4). The list, before and after, is in `src/TEXT_REVIEW.md`.
- Each item now has a text review status: **Verified** for the 176 ECC items, and **Needs Review** for the other 7 frameworks until they are checked against their guides. The status is shown in the item details on the web.
- The corrected texts are in the web, the Excel register and the Power BI data (tests check they match).
- The 41 OSMACC item texts were compared the same way with the OSMACC-1:2021 document (Arabic): 38 matched and 3 were corrected. OSMACC is now **Verified** too.

## v1.2.1 (2026-11-22)

- The overall compliance rate is empty (not an error) when every main control is excluded, so there is no division by zero.
- The tests now fail if an ID is missing, extra or repeated in the Excel register or the Power BI data, instead of skipping it.

## v1.2 (2026-11-22): fixes after the second review

| Item | Change |
|---|---|
| One source for the Excel register | Before, the register took only the approval column from `controls.json`, and its other values came from the base file. Now `patch_excel.py` writes every register field from `controls.json`. A test changes an item in `controls.json`, rebuilds the register and checks that the change arrives. |
| Missing approval | If the approval field is missing, the web, Python and Excel all treat the exception as pending, not approved. |
| Date written as text | A target date pasted as text is no longer hidden. The finding shows «تاريخ غير صالح», and the dashboard data quality line counts it (tested with LibreOffice). |
| Lists | The framework pickers on the dashboard and the documents sheet now also block invalid values. All lists in the register are now Stop alerts. |
| Assessment date | Shown next to the overdue figure (intro and KPI card), not only in the method tab. |
| CI | Installs LibreOffice and rebuilds the web page from `src/`, then fails if it differs from the published page. |

Correction to v1.1 below: "one source" was only true for the web and Power BI data until v1.2, because the register was still read from its base file.


## v1.1 (2026-11-21): fixes after the technical review

### Changes by FIX number

| FIX | Change |
|---|---|
| FIX-00 | One source (`src/controls.json`) for the web, the Excel register and the Power BI data, with build scripts and 27 tests (`src/tests.py`). The tests check, field by field, that the three hold the same data and give the same results. The 9 items that differed (web: «لا ينطبق - بانتظار الاعتماد», Excel: «معتمد») were settled on the web version. |
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
