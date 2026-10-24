import math
import unittest

from prior_posterior.evaluation import (
    kl_information_gain, low_inflow_auc, ranked_probability_score,
)
from prior_posterior.forecast import forecast_support, pseudo_hindcast
from prior_posterior.posterior import bayes_update
from prior_posterior.prior import (
    build_transition_matrices, circular_distance, propagate, seasonal_weight,
)
from prior_posterior.states import StateDefinition, fit_dekad_states


class ProbabilityTests(unittest.TestCase):
    def test_quantile_state_and_seasonal_weight(self):
        definition = StateDefinition((2.0, 4.0), 1.0, 6.0)
        self.assertEqual(definition.classify(2.0), 1)
        self.assertEqual(definition.classify(2.1), 2)
        self.assertEqual(definition.representatives, (1.5, 3.0, 5.0))
        self.assertEqual(circular_distance(1, 36), 1)
        self.assertAlmostEqual(seasonal_weight(1, 36), math.exp(-0.5))

    def test_transition_smoothing_and_propagation(self):
        rows = [
            {"year": year, "dekad": period, "inflow_1e8m3": 1.0 + year % 3 + period / 100}
            for year in range(2001, 2007) for period in range(1, 37)
        ]
        definitions = fit_dekad_states(rows, states=3, excluded_year=2006)
        matrices = build_transition_matrices(
            rows, definitions, states=3, excluded_year=2006
        )
        self.assertEqual(len(matrices), 36)
        for matrix in matrices.values():
            for row in matrix:
                self.assertAlmostEqual(sum(row), 1.0)
                self.assertTrue(all(0 <= p <= 1 for p in row))
        prediction = propagate([1.0, 0.0, 0.0], matrices[1])
        self.assertEqual(prediction, matrices[1][0])

    def test_bayes_rps_kl_auc_and_pseudohindcast(self):
        posterior = bayes_update([0.5, 0.5], [math.log(0.2), math.log(0.8)])
        self.assertAlmostEqual(posterior[0], 0.2)
        self.assertAlmostEqual(posterior[1], 0.8)
        self.assertEqual(ranked_probability_score([1.0, 0.0], 1), 0.0)
        self.assertEqual(ranked_probability_score([0.0, 1.0], 1), 1.0)
        self.assertAlmostEqual(kl_information_gain([0.5, 0.5], [0.5, 0.5]), 0)
        self.assertEqual(low_inflow_auc([0.9, 0.8, 0.2, 0.1], [1, 1, 0, 0]), 1.0)
        self.assertEqual(
            pseudo_hindcast([1.0, 2.0], 0.15, 9),
            pseudo_hindcast([1.0, 2.0], 0.15, 9),
        )
        support = forecast_support((1.0, 2.0), 1.1, 0.15)
        self.assertGreater(support[0], support[1])
        with self.assertRaises(ValueError):
            bayes_update([0.2, 0.2], support)


if __name__ == "__main__":
    unittest.main()
