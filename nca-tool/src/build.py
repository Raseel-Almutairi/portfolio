"""Builds nca-tool/index.html from one source.

Run from this folder:  python build.py
- controls.json : the 689 items (control text, sample status, evidence, approval of "not applicable", findings)
- guides.json   : NCA guides used as references
- template.html : page layout, styles and logic (D3 is embedded, so the page loads nothing from the internet)
- AS_OF         : the assessment date the demo is pinned to (empty = today in Riyadh time)
"""
import json
from datetime import date

AS_OF = "2026-11-21"
MONTHS = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]


def as_of_text(iso):
    d = date.fromisoformat(iso)
    return f"{d.day} {MONTHS[d.month - 1]} {d.year}"


def build(out="../index.html"):
    t = open("template.html", encoding="utf-8").read()
    controls = json.load(open("controls.json", encoding="utf-8"))
    guides = json.load(open("guides.json", encoding="utf-8"))
    # JSON inside <script>: escape "</" so text can never close the tag
    dump = lambda x: json.dumps(x, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    t = t.replace("__CONTROLS__", dump(controls)).replace("__GUIDES__", dump(guides))
    t = t.replace("__AS_OF_TXT__", as_of_text(AS_OF) if AS_OF else "تاريخ اليوم").replace("__AS_OF__", AS_OF)
    open(out, "w", encoding="utf-8").write(t)
    print("Built", out)


if __name__ == "__main__":
    build()
