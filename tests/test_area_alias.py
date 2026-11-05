"""Area alias tests: 'Sentosa Cove' maps to the approved zone and LL-0412 prices correctly."""
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from decimal import Decimal
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import prepare_batch  # noqa: E402


class AreaAliasTests(unittest.TestCase):
    def test_sentosa_cove_resolves_to_approved_zone(self):
        self.assertEqual(prepare_batch.ALIASES["Sentosa Cove"], "Sentosa and Jurong Island")
        self.assertEqual(prepare_batch.map_zone("Sentosa Cove"), Decimal("80.00"))

    def test_ll_0412_prices_correctly(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            with mock.patch.object(prepare_batch, "ROOT", tmp), redirect_stdout(io.StringIO()):
                prepare_batch.main(str(ROOT / "lunchlink-orders.csv"))
            prepared = json.loads((tmp / "outputs" / "prepared.json").read_text())

        order = prepared["LL-0412"]
        self.assertEqual(order["boxes"], 60)
        self.assertEqual(order["price_per_box"], "11.80")
        self.assertEqual(Decimal(order["price_per_box"]) * order["boxes"], Decimal("708.00"))
        self.assertEqual(order["delivery_fee"], "80.00")
        self.assertEqual(order["gst"], "70.92")
        self.assertEqual(order["total"], "858.92")


if __name__ == "__main__":
    unittest.main()
