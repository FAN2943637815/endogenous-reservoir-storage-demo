# Synthetic Inflow Generation

## Scientific purpose

The manuscript uses separately generated Historical-like and Extreme-dry runoff
sequences for **offline robustness tests**. This project demonstrates how a
daily seasonal autoregressive sequence can be generated, aggregated into actual
calendar dekads, and checked statistically. It supplies only synthetic
teaching data, never the archived 200-year study scenarios.

## Mathematical background

Appendix C, Eqs. (C.1), (C.2), (C.5), and (C.6), describe a Box–Cox transform,
calendar standardization, state-dependent periodic AR process, and inverse
transform. The public generator uses the explicit restricted case
`lambda=0` and `P=1`:

    z_d = phi * z_(d-1) + epsilon_d
    log(Q_d + delta) = mu_d + a_(R_y) + z_d
    Q_d = max(0, exp(mu_d + a_(R_y) + z_d) - delta)

Here `Q_d` is daily discharge in m³/s, `delta` is a positive offset,
`mu_d` is a fixed sinusoidal seasonal log mean, `R_y` is one of three
illustrative annual states, and `epsilon_d` is seeded Gaussian noise.
Fixed illustrative state-transition probabilities generate the annual states.
The study generator instead estimates annual states, persistence, seasonal
parameters, residual distributions and candidate-acceptance rules from
observed runoff. Its GMM/semi-Markov and state-month AR/tail calibration are
not included.

## Computational procedure and code

1. `generation.GenerationConfig` validates explicitly illustrative parameters.
2. `generation.generate_daily` draws annual states and daily AR innovations.
3. `generation.aggregate_dekad` sums
   `flow_cms × 86400 / 10^8` to volumes in 10^8 m³. Calendar dekads are days
   1–10, 11–20, and 21–month end; leap days are retained.
4. `generation.generate_members` repeats the process with seeds
   `seed + member_index`.
5. `diagnostics.summarize_dekad` computes mean, population standard deviation,
   CV, quantiles, lag-one correlation, seasonal means, low-dekad event count,
   and longest low-dekad spell.
6. `outputs.py` writes CSV, JSON, and an SVG seasonal profile.
   `demo.py` is the command-line entry point.

The source project contains an older STL/AR/year-type implementation and a
newer dual-scenario generator. The manuscript's Appendix C corresponds most
closely to the latter. Neither implementation is copied here.

## Inputs and outputs

No input file is required. `GenerationConfig` can be supplied as a JSON object
with keys `start_year`, `years`, `seed`, `mean_flow_cms`,
`seasonal_log_amplitude`, `ar_coefficient`, `innovation_std` and
`log_offset_cms`. All defaults are **teaching parameters**, not fitted
manuscript parameters. The default uses 12 calendar years and seed 20261016.

Outputs are `member_N_dekad.csv`, `diagnostics.json` and
`seasonal_mean.svg` under `outputs/synthetic_inflow/`. The CSV has one row per
calendar dekad; see [data schema](../docs/data_schema.md). Outputs are
regenerated from the seed and never copied from research records.

## Installation and execution

Run from the repository root with Python 3.10+:

    python -B -m synthetic_inflow.demo
    python -B -m synthetic_inflow.demo --years 3 --members 4 --seed 7
    python -B -m synthetic_inflow.demo --config synthetic_inflow/examples/config.json

The runtime has no third-party dependencies. A configuration file is included
in `examples/config.json`. The command writes to `outputs/` by default; use
`--output-dir` for another path.

## Example results and validation

With the default seed, first-member mean dekad volume is approximately
1.056 × 10^8 m³ and CV is 0.407. `seasonal_mean.svg` plots 36 mean
calendar-dekad volumes. Those numbers describe this generated sample only.
The diagram and summary can be recreated by the first command above.

Run:

    python -B -m unittest discover -s synthetic_inflow/tests -v

The tests assert exact day and dekad counts across a leap year, volume
conservation under aggregation, finite nonnegative flows, deterministic
replay, and valid diagnostics. They do not validate the study's scenario
statistics, because the observed calibration series and archived scenario
members are unavailable.

## Implementation scope and limitations

The public model preserves the transform–periodic AR–inverse transform and
daily-to-dekad relationships, but omits Box–Cox parameter estimation, annual
feature weighting and GMM classification, semi-Markov residence-time fitting,
month/state AR-order selection, low-flow tail modeling, acceptance/rejection
screening, and the Extreme-dry perturbations. Consequently it cannot
recreate the paper's Historical-like or Extreme-dry sequences or Fig. C1.
