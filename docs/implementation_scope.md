# Public implementation scope and scientific limits

## Provenance and boundaries

The public Python code was written from equations disclosed in the
manuscript and generic scientific computations. No source file from the
historical-prior Python project, the original Java reservoir system, or
the research runoff generators was copied. No observed input,
reservoir characteristic table, archived pseudo-hindcast, study-generated
scenario is shipped. The only study-derived numerical material in this
public repository is the limited Fig. 3(e) aggregate in `figure_data/`; it does
not expose engineering inputs or case-level records.

| Component | Formal research function | Public implementation | Main difference |
| --- | --- | --- | --- |
| Runoff scenario generator | Fits annual states, persistence, periodic AR and low-flow tails; screens Historical-like and Extreme-dry members | Fixed-parameter log AR(1), illustrative annual states, calendar-dekad aggregation and diagnostics | No fitted statistics, semi-Markov residence times, Student-t/GPD tail, acceptance screen or 200-year samples |
| State definition and prior | Per-dekad empirical states and seasonally weighted, smoothed transitions from 1951–2024 observations | Published quantile, circular weight and smoothing relationships on synthetic rows | One synthetic held-out year rather than archived 74-year verification |
| Forecast sequence | Prescribed log-Gaussian pseudo-hindcasts for controlled retrospective experiments | Fresh seeded pseudo-hindcasts from synthetic actual inflow | Different random stream and no archived study series |
| Posterior update | Representative-value likelihood and Bayes update | Midpoint support and stable Bayes normalization | Formal state boundaries and reported posterior sequence absent |
| Probability propagation | Period-specific transition products and path probabilities | Row propagation and exact small-path enumeration | Only toy matrices and a two-period risk window |
| Engineering system | Case-study level–storage–area relation, seasonal flood limit, evaporation, required release, outlet capacity and sector demand | One storage pool with explicit loss, demand, fixed upper/critical bounds, spill and balance | Cannot represent the actual engineering feasible set |
| Target optimization | Rolling Java dynamic programming with risk screening and fallback at each recursion stage | Two-stage finite-grid teaching Bellman search, each stage risk-screened, with published three risk ratios | Fixed future path-supply rule and illustrative constraints/objective inputs |
| Numerical evaluation | Historical and generated-scenario comparisons, ablation, sensitivity and figure/table values | Synthetic RPS, KL, AUC, shortage and supply metrics; one real Fig. 3(e) aggregate CSV | The two Fig. 3(e) aggregate series can be plotted; exact submitted-image correspondence is unverified and no full reported result can be recomputed |

## Interfaces for nonpublic functions

**Scenario fitting and acceptance.** Inputs: authorized daily observed
discharge (m³/s), dates, annual-state feature definitions, transform and AR
settings, candidate-screening weights and thresholds. Outputs: dated daily
members, year-state sequences, dekad volumes and validation statistics.
These members enter offline robustness tests only. The public generator
has fixed illustrative parameters and no acceptance decision.

**Engineering constraints.** Inputs: level–storage–area curve, seasonal
upper levels, dead and critical levels, evaporation, sector demand, required
release and outlet capacity. Outputs: period-specific feasible storage
nodes, losses and water-balanced execution records. The public `Stage`
has only scalar demand, loss, upper and critical storage.

**Full rolling risk and DP solver.** Inputs: current storage and posterior,
state representatives, future transition matrices, engineering candidates,
demand/loss trajectories, risk thresholds, discount and terminal value.
Outputs: target, benefit, path risks, feasibility/fallback status, realized
supply and next storage. The public `choose_target` is a two-stage
illustration and is not a substitute for the research solver.

## Source–manuscript consistency items for author review

Read-only comparison of the current `manuscript.tex` with the original
programs found three points that prevent a source-to-results equivalence
claim:

1. Appendix A defines climatology from the column marginal of **valid
   weighted transition pairs**. The historical-prior script's
   climatology function counts arrivals in the neighborhood even when a
   preceding state is unavailable. The public calculation follows the
   manuscript equation.
2. The manuscript fallback minimizes the **maximum standardized** risk
   violation. The inspected Java candidate selector sums raw threshold
   exceedances and a physical deficit before choosing fallback. The
   public example follows the manuscript expression.
3. The historical-prior script currently defaults to `K=10`, while the
   manuscript baseline is `K=5`. The exact invocation or workbook
   version that produced each reported result must be recorded; a default
   does not prove that the reported baseline used the wrong `K`.

An earlier local draft described `h=2` as the current plus two future
periods and child-stage risk screening as absent from the manuscript.
The current source explicitly defines `h=2` as the current plus one
future period, `K^h=K²` paths, and risk screening at each Bellman stage.
The public code and documentation have been updated accordingly. These
changes do not establish which original program version generated every
reported table. No protected research code or manuscript was changed.
