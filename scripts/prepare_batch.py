"""Read the morning LunchLink file, price each order and write a prompt for the quote drafter."""
import csv
import json
import sys
import traceback
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from guardrail import check_note

RUN_DATE = date(2026, 9, 30)
ROOT = Path(__file__).resolve().parent.parent
RATES = json.loads((ROOT / "rates-lunchbox.json").read_text(), parse_float=Decimal)
ZONES = {z["name"]: z["fee"] for z in RATES["delivery_zones"]}
ALIASES = json.loads((ROOT / "area-aliases.json").read_text())


class OrderStop(Exception):
    """An order that cannot be priced and must go to Priya."""


def map_boxes(raw, log):
    text = raw.strip()
    if text.isdigit():
        return int(text)
    digits = "".join(ch for ch in text if ch.isdigit())
    log("WARN", f"boxes '{text}' is text, coerced to {int(digits)}")
    return int(digits)


def map_date(raw, log):
    text = raw.strip()
    first, second = (int(p) for p in text.split("/")[:2])
    if first <= 12:
        parsed = datetime.strptime(text, "%m/%d/%y").date()
        if second <= 12:
            log("WARN", f"date '{text}' parsed as {parsed} (month first)")
        return parsed
    return datetime.strptime(text, "%d/%m/%y").date()


def map_zone(area):
    return ZONES[ALIASES.get(area, area)]


def calculate(boxes, fee):
    tier = next(
        t for t in RATES["price_tiers"]
        if boxes >= t["min_boxes"] and (t["max_boxes"] is None or boxes <= t["max_boxes"])
    )
    price = tier["price_per_box"]
    subtotal = price * boxes + fee
    gst = (subtotal * RATES["gst_rate"]).quantize(Decimal("0.01"), ROUND_HALF_UP)
    return price, gst, subtotal + gst


RULES = """You are the quote drafter for the Heicoders Catering weekday lunchbox service.
Write a short quotation email to the customer using only the order details given below.

Rules:
- Use the figures in the order details exactly. Do not calculate or change them.
- Do not mention costs, margins, discounts, free items or offers.
- Start the email with "Dear <customer>," and end it with "Warm regards," followed by
  "Priya Menon", "Sales and Events Lead" and "Heicoders Catering" on separate lines.
- Show boxes x price per box, delivery, GST (9%) and total payable.
- Write amounts in Singapore dollars as S$.
- Keep the email under 150 words.
- Return JSON only, with the keys: order, customer, boxes, price_per_box, delivery, gst, total, email.

"""


def write_prompt(order, customer, boxes, area, price, fee, gst, total):
    lines = [
        "ORDER",
        f"customer: {customer}",
        f"boxes: {boxes}",
        f"area: {area}",
        f"price_per_box: {price:.2f}",
        f"delivery_fee: {fee:.2f}",
        f"gst: {gst:.2f}",
        f"total_payable: {total:.2f}",
    ]
    lines += ["Write the quotation email using the order details above.", "Return JSON only.", ""]
    path = ROOT / "outputs" / "prompts" / f"{order}.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(RULES + "\n".join(lines))


def main(orders_file):
    print(f"Lunchbox Desk batch {RUN_DATE} 07:00")
    prepared, stopped, flagged = {}, 0, 0
    with open(orders_file, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            order = row["order"]
            log = lambda level, msg: print(f"{order}  {level:<6} {msg}")
            try:
                boxes = map_boxes(row["boxes"], log)
                delivery = map_date(row["date"], log)
                fee = map_zone(row["area"])
                if delivery < RUN_DATE:
                    raise OrderStop(f"delivery date {delivery} is before run date {RUN_DATE}")
                if boxes < RATES["minimum_boxes"]:
                    raise OrderStop(f"{boxes} boxes is below the minimum of {RATES['minimum_boxes']}")
                notes = row["notes"].strip()
                if len(notes) > 1000:
                    log("WARN", f"notes field is {len(notes):,} characters")
                price, gst, total = calculate(boxes, fee)
            except OrderStop as stop:
                log("ERROR", f"{stop} -> open item")
                stopped += 1
                continue
            except Exception as err:
                frame = traceback.extract_tb(err.__traceback__)[-1]
                log("ERROR", f"{type(err).__name__}: {err} in {frame.name} ({Path(frame.filename).name}:{frame.lineno}) -> open item")
                stopped += 1
                continue
            reasons = check_note(notes)
            if reasons:
                flagged += 1
                log("FLAG", "FLAGGED FOR PRIYA")
                print("  guardrail reason: suspicious instruction-like note")
                for r in reasons:
                    print(f"    - {r}")
                print(f"  note (ignored data, copied literally): {json.dumps(notes, ensure_ascii=False)}")
                print("  quote from approved fields only (boxes, area, rates-lunchbox.json):")
                print(f"    {boxes} x S${price:.2f} = S${price * boxes:.2f} | delivery S${fee:.2f} | "
                      f"GST {RATES['gst_rate'] * 100:.0f}% S${gst:.2f} | total S${total:.2f}")
                print("  customer output: NONE. No drafter prompt written, nothing drafted or sent.")
                continue
            log("ok", f"{str(boxes) + ' boxes':<10} {price:.2f}  fee {fee:.2f}  gst {format(gst, '.2f'):<8}total {total:.2f}")
            write_prompt(order, row["customer"], boxes, row["area"], price, fee, gst, total)
            prepared[order] = {
                "customer": row["customer"], "boxes": boxes, "area": row["area"],
                "price_per_box": f"{price:.2f}", "delivery_fee": f"{fee:.2f}",
                "gst": f"{gst:.2f}", "total": f"{total:.2f}",
            }
    (ROOT / "outputs").mkdir(exist_ok=True)
    (ROOT / "outputs" / "prepared.json").write_text(json.dumps(prepared, indent=2))
    print(f"{len(prepared)} prepared, {flagged} flagged for Priya, {stopped} open items. prompts written to outputs/prompts/")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python3 scripts/prepare_batch.py lunchlink-orders.csv")
    main(sys.argv[1])
