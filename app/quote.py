"""Price one lunchbox order for the quote page, using the batch calculator and rates-lunchbox.json only."""
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from prepare_batch import RATES, RUN_DATE, ZONES, calculate  # noqa: E402

APPROVED_AREAS = [zone["name"] for zone in RATES["delivery_zones"]]


class QuoteError(ValueError):
    """An order the page cannot price."""


def _boxes(value):
    if isinstance(value, bool):
        raise QuoteError("boxes must be a whole number")
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    raise QuoteError("boxes must be a whole number")


def _delivery_date(value):
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value).strip())
    except ValueError:
        raise QuoteError("delivery date must be a valid date (YYYY-MM-DD)") from None


def price_quote(boxes, delivery_date, area):
    """Return the quote figures as strings. Raises QuoteError for an order that cannot be priced."""
    boxes = _boxes(boxes)
    delivery = _delivery_date(delivery_date)
    if area not in ZONES:
        raise QuoteError(f"delivery area not supported: choose one of {', '.join(APPROVED_AREAS)}")
    if boxes < RATES["minimum_boxes"]:
        raise QuoteError(f"{boxes} boxes is below the minimum of {RATES['minimum_boxes']}")
    if delivery < RUN_DATE:
        raise QuoteError(f"delivery date {delivery} is before run date {RUN_DATE}")

    fee = ZONES[area]
    price, gst, total = calculate(boxes, fee)
    return {
        "boxes": boxes,
        "delivery_date": delivery.isoformat(),
        "area": area,
        "price_per_box": f"{price:.2f}",
        "boxes_total": f"{price * boxes:.2f}",
        "delivery_fee": f"{fee:.2f}",
        "gst_rate": f"{RATES['gst_rate'] * 100:.0f}",
        "gst": f"{gst:.2f}",
        "total": f"{total:.2f}",
    }
