"""Regression and rule tests for the SAMA CSF demo (run: python tests.py).

The figures below are the sample data as of 2026-11-18. If a change moves one of them,
the change must explain why (see CHANGELOG.md)."""
from datetime import date
from model import build, AS_OF

subs, ccs, gaps, docs = build()
ok = 0


def check(name, cond):
    global ok
    assert cond, "FAILED: " + name
    ok += 1
    print("PASS", name)


# Baseline figures (sample data, as of 2026-11-18)
check("assessment date is pinned", AS_OF == date(2026, 11, 18))
check("32 subdomains", len(subs) == 32)
check("149 control considerations", len(ccs) == 149)
check("average maturity 2.5", round(sum(s["level"] for s in subs) / 32, 1) == 2.5)
check("17 of 32 at level 3+", sum(s["level"] >= 3 for s in subs) == 17)
check("63 actions", len(gaps) == 63)
check("8 overdue", sum(g["overdue"] for g in gaps) == 8)

# Rules
check("controls carry no status (reference only)", all("st" not in c for c in ccs))
check("every action is for a criterion still answered No",
      all(next(s for s in subs if s["sid"] == g["sid"])["ans"][g["crit"]] == "No" for g in gaps))
check("closing an action does not change the answer: closed actions are flagged re-assess",
      all(g["reassess"] == (g["fstatus"] == "Closed") for g in gaps) and sum(g["reassess"] for g in gaps) == 6)
check("risk accepted is not counted as met and is not counted as open",
      sum(g["fstatus"] == "Risk Accepted" for g in gaps) == 1)
check("closed or risk accepted actions are never overdue",
      not any(g["overdue"] for g in gaps if g["fstatus"] in ("Closed", "Risk Accepted")))
check("every action has a target date", all(g["due"] for g in gaps))
check("action text names the subdomain", all(g["action"].startswith(g["sub"] + ": ") for g in gaps))

# Built files
import os
web = open(os.path.join("..", "index.html"), encoding="utf-8").read()
check("web makes no external requests", "googleapis" not in web and "Content-Security-Policy" in web)
check("web shows the assessment date", "18 November 2026" in web)
print(f"\n{ok} tests passed")
