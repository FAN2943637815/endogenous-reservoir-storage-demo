# Integrated public demonstration

`run_integrated_demo.py` connects the three public projects using freshly
generated data. Run from the repository root:

    python -B -m workflows.run_integrated_demo
    python -B -m workflows.run_integrated_demo --seed 7

The default seed is 20261016. The workflow creates 12 years of synthetic
daily flow, aggregates them to 36 calendar-dekad volumes per year, and
reserves the last year for evaluation. The first 11 **synthetic** years
stand in for the manuscript's observed historical record. Their per-dekad
quantiles and weighted transition counts form the prior. A separate
log-Gaussian pseudo-hindcast generator produces forecast values from the
held-out synthetic inflow. The prior and representative-value likelihood
produce a posterior vector at each decision stage.

Each posterior, its matching state inflow representatives, and one next-period transition matrix enter the two-dekad reservoir path-risk and finite-grid search.
Only the current target is executed with the held-out actual inflow. The next
stage uses its newly available previous observation and forecast. All
volumes are 10^8 m³; the synthetic generator converts daily m³/s using the
actual day count in each calendar dekad.

`outputs/integrated/` contains `synthetic_history_dekad.csv`,
`probabilities.json`, `decisions.csv`, `operation.csv`, and
`summary.json`. For the default seed, mean prior RPS is about 0.1844 and
mean posterior RPS is about 0.0906. Supply reliability is about 0.8191
and cumulative shortage is 7.813 × 10^8 m³. These are teaching outputs,
not manuscript results.

The paper's generated Historical-like and Extreme-dry sequences are
separate offline evaluation scenarios and were **not used to fit its
historical prior**. The integrated demo's synthetic training years are a
necessary public stand-in for inaccessible observed data, and the software
records this departure.

`--mode research` fails with a clear missing-dependency message. A formal
research run would require authorized observed historical inflows, demand and
engineering inputs, archived pseudo-hindcasts, state classifications,
scenario data, and the original optimized solver, with their units and
versions checked. The public workflow does not silently substitute a
teaching algorithm.

Verify replay and mass balance:

    python -B -m unittest discover -s workflows/tests -v
