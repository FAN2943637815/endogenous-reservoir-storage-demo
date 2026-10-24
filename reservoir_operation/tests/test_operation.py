import unittest

from reservoir_operation.decision import _continuation_value, choose_target
from reservoir_operation.evaluation import (
    critical_storage_hit_frequency, supply_reliability, total_shortage,
)
from reservoir_operation.risk import (
    RiskThresholds, evaluate_risk, is_feasible, weighted_cvar,
)
from reservoir_operation.system import Reservoir, Stage, realize


class OperationTests(unittest.TestCase):
    def test_realized_balance_and_metric_denominator(self):
        reservoir = Reservoir(1.0)
        stage = Stage(demand=2.0, loss=0.1, upper_storage=5.0, critical_storage=2.0)
        step = realize(reservoir, stage, start=3.0, inflow=1.0, target=3.0)
        self.assertAlmostEqual(step.end_storage, 3.0)
        self.assertAlmostEqual(step.supply, 0.9)
        self.assertAlmostEqual(step.shortage, 1.1)
        self.assertAlmostEqual(
            step.start_storage + step.inflow - step.loss,
            step.supply + step.spill + step.end_storage,
        )
        self.assertAlmostEqual(supply_reliability([step]), 0.45)
        self.assertAlmostEqual(total_shortage([step]), 1.1)
        self.assertEqual(critical_storage_hit_frequency([step], [3.1]), 1.0)
        with self.assertRaises(ValueError):
            realize(reservoir, stage, 3.0, 1.0, 6.0)

    def test_weighted_tail_and_risk_screening(self):
        self.assertAlmostEqual(weighted_cvar([0.0, 0.5, 1.0], [0.5, 0.4, 0.1]), 1.0)
        reservoir = Reservoir(0.0)
        stage = Stage(1.0, 0.0, 4.0, 3.0)
        risk = evaluate_risk(
            reservoir, start_storage=2.0, current_stage=stage,
            current_inflows=(0.0, 1.0), target=2.0, posterior=[0.5, 0.5],
            transitions=[[[1.0, 0.0], [0.0, 1.0]]],
            future_inflows=[(0.0, 1.0)], future_stages=[stage],
        )
        self.assertAlmostEqual(risk.critical_probability, 1.0)
        self.assertEqual(risk.path_count, 2)
        self.assertFalse(is_feasible(risk, RiskThresholds(1.0, 0.5, 1.0)))

    def test_two_period_path_count_and_current_shortage(self):
        reservoir = Reservoir(0.0)
        stage = Stage(1.0, 0.0, 4.0, 0.0)
        risk = evaluate_risk(
            reservoir, start_storage=0.0, current_stage=stage,
            current_inflows=(0.0, 1.0), target=0.0, posterior=[0.5, 0.5],
            transitions=[[[0.5, 0.5], [0.5, 0.5]]],
            future_inflows=[(1.0, 1.0)], future_stages=[stage],
        )
        self.assertEqual(risk.path_count, 4)  # K^h: K=2, h=2.
        self.assertAlmostEqual(risk.expected_shortage, 0.25)
        self.assertAlmostEqual(risk.cvar, 0.5)
        self.assertAlmostEqual(risk.critical_probability, 0.0)
        five_state_risk = evaluate_risk(
            reservoir, start_storage=0.0, current_stage=stage,
            current_inflows=(1.0,) * 5, target=0.0, posterior=[0.2] * 5,
            transitions=[[[0.2] * 5 for _ in range(5)]],
            future_inflows=[(1.0,) * 5], future_stages=[stage],
        )
        self.assertEqual(five_state_risk.path_count, 25)  # Manuscript baseline K=5, h=2.

    def test_bellman_child_uses_risk_screen(self):
        reservoir = Reservoir(0.0)
        stage = Stage(1.0, 0.0, 4.0, 1.5)
        value = _continuation_value(
            reservoir, start=2.0, probabilities=[1.0], inflows=(0.0,),
            stage=stage, nodes=(0.0, 2.0),
            limits=RiskThresholds(1.0, 0.1, 1.0), beta=0.90,
        )
        # Target 0 has larger unconstrained benefit but breaches critical storage.
        # Risk-screened target 2 supplies nothing and earns terminal value 25.
        self.assertAlmostEqual(value, 25.0)
    def test_known_finite_grid_optimum(self):
        reservoir = Reservoir(0.0)
        stage = Stage(1.0, 0.0, 4.0, 0.0)
        decision = choose_target(
            reservoir, start_storage=2.0, current_stage=stage,
            current_inflows=(1.0,), posterior=[1.0],
            transitions=[[[1.0]]], future_inflows=[(1.0,)],
            future_stages=[stage], nodes=(0.0, 1.0, 2.0, 3.0, 4.0),
            limits=RiskThresholds(1.0, 1.0, 1.0),
        )
        self.assertFalse(decision.used_fallback)
        self.assertEqual(decision.chosen.target_storage, 2.0)
        self.assertAlmostEqual(decision.chosen.objective, 225.0)

    def test_empty_risk_domain_uses_least_standardized_violation(self):
        reservoir = Reservoir(0.0)
        current = Stage(2.0, 0.0, 3.0, 1.0)
        future = Stage(5.0, 0.0, 3.0, 1.0)
        decision = choose_target(
            reservoir, start_storage=2.0, current_stage=current,
            current_inflows=(1.0,), posterior=[1.0],
            transitions=[[[1.0]]], future_inflows=[(1.0,)],
            future_stages=[future], nodes=(0.0, 1.0, 2.0, 3.0),
            limits=RiskThresholds(0.10, 0.10, 0.10),
        )
        self.assertTrue(decision.used_fallback)
        self.assertFalse(any(candidate.feasible for candidate in decision.candidates))
        self.assertAlmostEqual(
            decision.chosen.standardized_violation,
            min(candidate.standardized_violation for candidate in decision.candidates
                if candidate.objective != float("-inf")),
        )


if __name__ == "__main__":
    unittest.main()
