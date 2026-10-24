# Prior Construction and Bayesian Updating

## Scientific purpose

This project exposes the published probability chain: historical inflow
states → seasonally weighted transition frequencies → smoothed historical
prior → pseudo-hindcast likelihood → posterior state probabilities. It is
fully executable with synthetic inflow, while the manuscript's archived
historical observations and pseudo-hindcasts remain unavailable.

## Mathematical background

For each calendar dekad, historical inflows are assigned to `K` dry-to-wet
quantile states using Eqs. (A.1)–(A.2). An arrival-period transition sample in
the circular neighborhood `|Delta|≤b` receives weight
`exp[-Delta²/(2 tau²)]` (Eqs. A.3–A.6). With weighted counts `n_ij` and
arrival-state climatology `p0_j`, the published empirical Bayes row is

    P_t[i,j] = (n_ij + lambda_K * p0_j) / (sum_j n_ij + lambda_K)

The public default uses the manuscript's stated `b=1`, `tau=1` and
`lambda_K=K`, with `K=5`. Period 1 uses period 36 of the preceding year;
missing cross-year pairs are excluded. For a held-out year, thresholds and
transitions are fitted only on other years.

The public pseudo-hindcast follows Eq. (12):
`ln(Qhat)=ln(Q)+epsilon`, `epsilon~N(0,sigma²)`. This generator is separate
from the runoff scenario generator. Forecast support is evaluated at each
state's midpoint representative (Eqs. 13 and 15), and the posterior is
`pi_post[k] ∝ pi_prior[k] * likelihood[k]` (Eq. 16). Log weights prevent
underflow. State probabilities can be propagated as a row vector with
`pi_next = pi_current P_next` (Eq. 18).

## Computational procedure and code

| Module | Function and role |
| --- | --- |
| `states.py` | `fit_dekad_states` and `StateDefinition.classify`: training-year quantiles, one-based states, finite-bound representatives |
| `prior.py` | `seasonal_weight`, `build_transition_matrices`, `prior_from_previous`, `propagate`, probability validation |
| `forecast.py` | `pseudo_hindcast` and `forecast_support`: independent synthetic forecasts and representative-value log likelihood |
| `posterior.py` | `bayes_update`: normalized posterior; `likelihood_only`: forecast-only comparator |
| `evaluation.py` | Normalized RPS (Eq. D.3), KL information gain (Eq. D.5), tie-aware low-state AUC |
| `demo.py` | Synthetic held-out-year pipeline and JSON outputs |

## Inputs and outputs

The reusable input table has `year`, `dekad` (1–36), and
`inflow_1e8m3` (dekad volume). The standalone demo creates 16 synthetic
years internally and reserves the last one for evaluation. Its
`pseudo_forecast_1e8m3` is generated *after* the synthetic actual series is
drawn, then used for current decisions without revealing current actual
inflow. The script writes `transition_dekad_1.json`,
`evaluation.json`, and `summary.json` under `outputs/prior_posterior/`.
See [data schema](../docs/data_schema.md).

## Installation and execution

Run from the repository root with Python 3.10+:

    python -B -m prior_posterior.demo
    python -B -m prior_posterior.demo --seed 7 --sigma 0.18

No observed inflow workbook, private package, or third-party Python library is
required. `--output-dir` changes the output location.

## Example results and validation

For seed 20261016, the held-out synthetic year's mean RPS is approximately
0.1567 for the prior and 0.0305 after updating; the low-state AUC is 0.956.
These values depend on the generated series and nominal forecast error and
are not the manuscript's verification results. Inspect the first-dekad
`prior` and `posterior` arrays in `summary.json` to see the update directly.
Recreate them with the first command above.

Run:

    python -B -m unittest discover -s prior_posterior/tests -v

Tests check threshold assignment, circular weights, row normalization,
cross-year matrix construction, deterministic pseudo-hindcasts, stable Bayes
weights, RPS, KL and AUC. The public held-out example illustrates
information-leakage control; it does not rerun the full 74-fold study
verification.

## Implementation scope and limitations

The public implementation follows the manuscript's formula for climatology
as the column marginal of valid weighted transition pairs. The historical
Excel script has a subtly different climatology count that includes all
arrival-state observations, including some without valid preceding states;
this discrepancy needs reconciliation before claiming exact equivalence.
The state-midpoint likelihood can differ materially from interval-integrated
support, as the manuscript itself notes. No observed data, fitted likelihood,
or archived pseudo-hindcast sequence is provided. The formal LOYO workbook
pipeline and all manuscript numerical verification outputs remain outside
this public demonstration.
