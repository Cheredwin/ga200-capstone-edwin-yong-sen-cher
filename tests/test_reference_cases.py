"""Deterministic checks for the quote calculator in app/quote.py. No server, drafter, API or network."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))

from quote import QuoteError, price_quote  # noqa: E402


class ReferenceCases(unittest.TestCase):
    """The three reference cases in brief.md, to the cent."""

    def check(self, boxes, area, price, boxes_total, fee, gst, total):
        q = price_quote(boxes, "2026-10-15", area)
        self.assertEqual(
            (q["price_per_box"], q["boxes_total"], q["delivery_fee"], q["gst"], q["total"]),
            (price, boxes_total, fee, gst, total),
        )

    def test_ll_0413(self):
        self.check(30, "Central and CBD", "12.50", "375.00", "30.00", "36.45", "441.45")

    def test_ll_0412(self):
        self.check(60, "Sentosa and Jurong Island", "11.80", "708.00", "80.00", "70.92", "858.92")

    def test_ll_0414(self):
        self.check(120, "Other mainland Singapore", "11.00", "1320.00", "45.00", "122.85", "1487.85")


class Rejections(unittest.TestCase):
    def test_below_minimum(self):
        with self.assertRaisesRegex(QuoteError, "below the minimum of 20"):
            price_quote(19, "2026-10-15", "Central and CBD")

    def test_unsupported_area(self):
        with self.assertRaisesRegex(QuoteError, "delivery area not supported"):
            price_quote(30, "2026-10-15", "Unknown Area")


if __name__ == "__main__":
    unittest.main()
