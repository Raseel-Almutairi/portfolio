# Changelog: SAMA CSF tool

## v1.1 (2026-11-21): fixes after the technical review

### Changes by FIX number

| FIX | Change |
|---|---|
| FIX-00 | Build scripts and source data added in `src/`. `python build.py` rebuilds the web page and both Excel files from one source. `python tests.py` runs 16 checks. |
| FIX-03 | One assessment date (as of date). The web shows it in the header ("18 November 2026"). In Excel it is cell AB29 in sheet 4 (blank = today), and every `TODAY()` was replaced with it. Overdue, days overdue, next escalation and due in 30 days all use it. |
| FIX-08 | A subdomain is **Not assessed** until all 14 criteria have a valid Yes or No. It no longer counts as level 0 and is left out of the average. New KPI: assessment completion. The example in the blank file was removed. |
| FIX-06 / 13 | Closing an action does not change the answer or the level. Closed actions are flagged **Re-assess**, and there is a new counter for them. The text "closing all actions moves the subdomain to level 3" was corrected. |
| FIX-07 | The unused control status (Addressed / Partially addressed) was removed from the data. Controls are reference only, and the maturity level comes only from the 14 criteria. |
| FIX-11 | Risk Accepted keeps the criterion unmet. The target date is used as the acceptance expiry date, and there are separate counters for risk accepted and acceptance expired. |
| FIX-05 | An open action without a target date shows "No target date" and is counted on the Summary. |
| FIX-02 / 21 | Excel lists now block invalid values (Stop alert). Pasted values that bypass the list are flagged in red, and a data quality line at the top of the Summary counts them. Formulas are protected without a password, so only the yellow input cells can be edited. The file author is no longer `openpyxl`. |
| FIX-12 | The subdomain name is included in each action text, so the 63 actions now have 63 distinct texts instead of 7. |
| FIX-24 | Level filter from 0 to 5. A ready email for each action is now in the web too. The title says "Demo". |
| FIX-25 | The Google Fonts request was removed (system fonts are used instead), and a Content Security Policy was added. The page makes no network requests. |

### Figures before and after (sample data)

| Figure | Before | After | Reason |
|---|---|---|---|
| Average maturity | 2.5 | 2.5 | - |
| Subdomains at level 3+ | 17 / 32 | 17 / 32 | - |
| Actions | 63 | 63 | - |
| Open actions (Open + In Progress) | 56 | 56 | - |
| Overdue (web) | 8 | 8 | - |
| Overdue (Excel) | changed every day (`TODAY()`) | 8 | FIX-03: same as-of date as the web |
| Closed, criterion still No | not shown | 6 | FIX-13 |
| Risk accepted | 1 (not counted) | 1 (own counter) | FIX-11 |
| Blank file: average maturity | 0.1 | Not assessed | FIX-08 |
| Blank file: at level 3+ | 1 / 32 | 0 / 32 | FIX-08: example removed |
| Distinct action texts | 7 | 63 | FIX-12 |

### Not done, and why
- Linking each action to a specific control consideration (FIX-12 in full) would need the assessment to be done per control, which is a change of method.
- Excel cannot approve a report, so the data quality warning is the alternative.
- These were tested in LibreOffice, not in Microsoft Excel: the Stop alert and pasting a value.
- FIX-16 to FIX-20 need a server and are out of scope for a static demo.
