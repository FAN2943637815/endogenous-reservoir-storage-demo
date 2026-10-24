import calendar
import math
import unittest

from synthetic_inflow.diagnostics import summarize_dekad
from synthetic_inflow.generation import (
    GenerationConfig, aggregate_dekad, generate_daily, generate_members,
)


class SyntheticGenerationTests(unittest.TestCase):
    def test_calendar_volume_and_seed(self):
        config = GenerationConfig(start_year=2004, years=2, seed=17)
        daily = generate_daily(config)
        again = generate_daily(config)
        self.assertEqual(daily, again)
        self.assertEqual(len(daily), 366 + 365)
        self.assertEqual(daily[0]["date"], "2004-01-01")
        self.assertEqual(daily[-1]["date"], "2005-12-31")
        self.assertTrue(all(math.isfinite(float(row["flow_cms"])) and
                            float(row["flow_cms"]) >= 0 for row in daily))
        dekads = aggregate_dekad(daily)
        self.assertEqual(len(dekads), 72)
        self.assertEqual(sum(int(row["days"]) for row in dekads), len(daily))
        self.assertAlmostEqual(
            sum(float(row["volume_1e8m3"]) for row in daily),
            sum(float(row["inflow_1e8m3"]) for row in dekads),
        )
        self.assertEqual(sum(int(row["days"]) for row in dekads[:36]), 366)
        self.assertEqual(int(dekads[5]["days"]), calendar.monthrange(2004, 2)[1] - 20)

    def test_batch_and_diagnostics(self):
        config = GenerationConfig(years=1, seed=3)
        members = generate_members(config, 2)
        self.assertEqual(len(members), 2)
        self.assertNotEqual(members[0], members[1])
        summary = summarize_dekad(members[0])
        self.assertEqual(summary["n_dekads"], 36)
        self.assertEqual(len(summary["seasonal_mean_1e8m3"]), 36)
        self.assertGreater(summary["mean_1e8m3"], 0)
        self.assertGreaterEqual(summary["longest_low_dekad_run"], 1)


if __name__ == "__main__":
    unittest.main()
