import csv
import unittest
from pathlib import Path

from workflows.run_integrated_demo import run


class IntegratedTests(unittest.TestCase):
    def test_repeatable_units_and_mass_balance(self):
        root = Path("outputs/tests")
        first = run(root / "integrated_a", seed=41)
        second = run(root / "integrated_b", seed=41)
        self.assertEqual(first, second)
        self.assertEqual(first["synthetic_inflow_diagnostics"]["n_dekads"], 432)
        self.assertGreaterEqual(first["operation"]["supply_reliability"], 0.0)
        self.assertLessEqual(first["operation"]["supply_reliability"], 1.0)
        self.assertGreaterEqual(first["operation"]["final_storage_1e8m3"], 1.0)
        with (root / "integrated_a" / "operation.csv").open(
            newline="", encoding="utf-8"
        ) as handle:
            operation = list(csv.DictReader(handle))
        self.assertEqual(len(operation), 36)
        for row in operation:
            self.assertAlmostEqual(
                float(row["start_storage"]) + float(row["inflow"]) - float(row["loss"]),
                float(row["supply"]) + float(row["spill"]) + float(row["end_storage"]),
            )
            self.assertGreaterEqual(float(row["end_storage"]), 1.0)


if __name__ == "__main__":
    unittest.main()
