"""The calculation rules of the NCA tool, in Python.

The same rules are written in the web page (template.html) and in the Excel register (sheet 07).
tests.py checks that all three give the same numbers."""

VALID = ["مطبق", "مطبق جزئيًا", "غير مطبق", "لا ينطبق"]


def main_key(cid):
    """Main control of an item: ECC-2-3-1-4 -> ECC-2-3-1; CCC-2-3-P-1-6 -> CCC-2-3-P-1."""
    p = cid.split("-")
    s = p[1:]
    k = next((i for i, x in enumerate(s) if x in ("P", "T")), -1)
    return p[0] + "-" + "-".join(s[: k + 2] if k >= 0 else s[:3])


def na_ok(r):
    return r["status"] == "لا ينطبق" and r.get("na_approved") is True


def na_pending(r):
    return r["status"] == "لا ينطبق" and r.get("na_approved") is not True  # missing approval = pending


def main_status(rows):
    st = [r["status"] or "" for r in rows]
    done = [x for x in st if x]
    if not done:
        return "لم يُقيّم"
    if any(x not in VALID for x in done):
        return "حالة غير صالحة"
    if len(done) < len(st):
        return "تقييم غير مكتمل"
    a = [r for r in rows if not na_ok(r)]
    if not a or all(na_pending(r) for r in a):
        return "لا ينطبق"
    b = [r for r in a if not na_pending(r)]
    if all(r["status"] == "مطبق" for r in b):
        return "مطبق جزئيًا" if any(na_pending(r) for r in a) else "مطبق"
    if all(r["status"] == "غير مطبق" for r in b):
        return "غير مطبق"
    return "مطبق جزئيًا"


def summary(controls, as_of):
    groups = {}
    for r in controls:
        groups.setdefault(main_key(r["id"]), []).append(r)
    mains = [(main_status(rs), any(na_pending(r) for r in rs)) for rs in groups.values()]
    implemented = sum(s == "مطبق" for s, _ in mains)
    excluded = sum(s == "لا ينطبق" and not p for s, p in mains)
    gaps = [r for r in controls if r["status"] in ("مطبق جزئيًا", "غير مطبق")]
    open_ = [r for r in gaps if r["gap_status"] != "مغلقة"]
    return {
        "mains": len(mains), "implemented": implemented, "denom": len(mains) - excluded,
        "compliance": round(implemented / (len(mains) - excluded), 4) if len(mains) > excluded else None,  # no denominator: no rate
        "open": len(open_), "overdue": sum(1 for r in open_ if r["due"] and r["due"] < as_of),
        "na_pending": sum(na_pending(r) for r in controls),
        "closed_reassess": sum(r["gap_status"] == "مغلقة" for r in gaps),
        "no_due": sum(1 for r in open_ if not r["due"]),
    }
