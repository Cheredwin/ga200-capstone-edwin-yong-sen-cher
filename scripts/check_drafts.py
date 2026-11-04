"""Check drafted quotations against the calculator's figures."""
import json
import sys
import traceback
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PREPARED = json.loads((ROOT / "outputs" / "prepared.json").read_text())


def money(value):
    return Decimal(str(value).replace("S$", "").replace(",", "").strip()).quantize(Decimal("0.01"))


def load_draft(path):
    raw = path.read_text()
    return json.loads(raw)


def check(order, draft):
    problems = []
    expected = PREPARED.get(order)
    if expected is None:
        return ["order was not prepared"]
    if money(draft["total"]) != Decimal(expected["total"]):
        problems.append(f"total {money(draft['total'])} != calculator {expected['total']}")
    if money(draft["price_per_box"]) != Decimal(expected["price_per_box"]):
        problems.append(
            f"price_per_box {money(draft['price_per_box'])} not valid for {expected['boxes']} boxes "
            f"(expected {expected['price_per_box']})"
        )
    email = draft.get("email", "")
    missing = []
    if "Total payable" not in email:
        missing.append("no 'Total payable' line")
    if "Warm regards" not in email:
        missing.append("no sign-off")
    if missing:
        problems.append("draft incomplete: " + ", ".join(missing))
    return problems


def main(target):
    target = Path(target)
    files = sorted(target.glob("*.json")) if target.is_dir() else [target]
    failed = False
    for path in files:
        order = path.stem
        try:
            draft = load_draft(path)
        except Exception:
            print(f"{order}  ERROR  could not read {path}")
            traceback.print_exc(file=sys.stdout)
            failed = True
            continue
        problems = check(order, draft)
        if not problems:
            print(f"{order}  PASS")
        for problem in problems:
            print(f"{order}  FAIL  {problem}")
            failed = True
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python3 scripts/check_drafts.py outputs/drafts/")
    main(sys.argv[1])
