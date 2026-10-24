# Endogenous reservoir storage under forecast uncertainty: public demonstrations

Companion computational demonstrations for the manuscript **“Endogenous
end-of-period storage decisions for 10-day reservoir drought operation under
forecast uncertainty”** (Shuncai Zhang et al., manuscript under revision).
The study examines how a forecast-updated inflow distribution changes the
risk-feasible set of end-of-dekad storage targets before a rolling optimization
selects one. This repository is a **public methodological demonstration**. It does not
reproduce the reported case-study experiments.

## What is available

| Project | Public calculation | Starting point |
| --- | --- | --- |
| [Synthetic inflow](synthetic_inflow/README.md) | Seeded daily log-periodic AR(1) generation, calendar-dekad aggregation, batch runs and diagnostics | `python -B -m synthetic_inflow.demo` |
| [Prior and posterior](prior_posterior/README.md) | Per-dekad quantile states, weighted transitions, empirical Bayes smoothing, pseudo-hindcast likelihood, Bayes update and verification scores | `python -B -m prior_posterior.demo` |
| [Reservoir operation](reservoir_operation/README.md) | Water balance, finite-path risk screening, a two-stage finite-grid Bellman search, rolling operation and supply metrics | `python -B -m reservoir_operation.demo` |
| [Integrated workflow](workflows/README.md) | Synthetic data exchange across all three projects | `python -B -m workflows.run_integrated_demo` |

Each project runs from the repository root without the others' input files. The
integrated workflow uses the synthetic generator's dekad volumes as **stand-in
historical data**, fits the public prior on 11 generated years, produces fresh
pseudo-hindcasts for the held-out twelfth year, updates posterior state
probabilities, and passes those probabilities and representative inflow
volumes to the reservoir search. The actual held-out inflow is used only when
the selected target is executed and evaluated.

This data flow differs from the paper: historical priors were estimated from
observed 1951–2024 inflows, while the paper's separately generated 200-year
Historical-like and Extreme-dry sequences were used only for offline
robustness tests. The archived pseudo-hindcasts and generated study scenarios
are not included here.

## Directory guide

| Path | Contents |
| --- | --- |
| `synthetic_inflow/` | Periodic AR generator, diagnostics, CSV/JSON/SVG writer, independent demo and tests |
| `prior_posterior/` | State definition, weighted prior, forecast model, stable posterior, scores, independent demo and tests |
| `reservoir_operation/` | Water balance, path risk, target search, rolling simulation, evaluation, independent demo and tests |
| `workflows/` | Integrated public demonstration and interface test |
| `docs/methodology.md` | Manuscript formula numbers, variables and public functions |
| `docs/computational_workflow.md` | Data movement and research implementation interfaces |
| `docs/implementation_scope.md` | Detailed differences and protected components |
| `docs/data_schema.md` | Units and machine-readable output fields |
| `docs/reproducibility.md` | Reviewer G8 requirement-by-requirement status |
| `figure_data/` | Limited, study-derived numerical coordinates for Fig. 3(e); see its [scope note](figure_data/README.md) |
| `docs/figure_data_inventory.md` | Current manuscript figure source-data deposit status |
| `docs/doi_release_checklist.md` | Rights, archive and DOI preparation gates |
| `docs/final_audit.md` | Source review, tests, public deposit status and unresolved G8 items |

## Environment and execution

Python 3.10 or newer is required. The public runtime uses only the Python
standard library; it was run here with Python 3.12.7. The original prior and
inflow projects use scientific Python packages, and the original operation
solver uses Java and local JARs, but none are needed to execute this public
demonstration. `pyproject.toml` records the public package and
`environment.yml` supplies a tested Python version for Conda users.

From the repository root:

    python -B -m synthetic_inflow.demo
    python -B -m prior_posterior.demo
    python -B -m reservoir_operation.demo
    python -B -m workflows.run_integrated_demo

All commands write only beneath `outputs/` by default. Use `--output-dir`
with any of the four commands to choose another output directory. The inflow
demo also accepts `--config`, `--years`, `--members`, and `--seed`; the prior
demo accepts `--sigma` and `--seed`. Seeds are recorded in JSON outputs.
`outputs/` is excluded from Git so repeated runs do not alter tracked examples.

The research-mode switch deliberately reports a missing dependency:

    python -B -m workflows.run_integrated_demo --mode research

It cannot label a public calculation as a formal manuscript result.

## Example outputs

All figures below are from **synthetic demonstration inputs**, seed 20261016:

| Run | Example result | Main files |
| --- | --- | --- |
| Inflow | First member mean dekad volume 1.056 × 10^8 m³; CV 0.407 | `member_1_dekad.csv`, `diagnostics.json`, `seasonal_mean.svg` |
| Prior/posterior | Held-out synthetic year mean RPS 0.1567 for prior and 0.0305 for posterior | `transition_dekad_1.json`, `evaluation.json`, `summary.json` |
| Reservoir | First chosen storage target 5.0 × 10^8 m³ after risk screening | `candidate_screening.csv`, `decisions.csv`, `operation.csv` |
| Integrated | Synthetic-year supply reliability 0.8191 and shortage 7.813 × 10^8 m³ | `probabilities.json`, `decisions.csv`, `operation.csv`, `summary.json` |

These outputs have no empirical performance meaning and must not be compared
numerically with manuscript tables. Each project README explains its example.

## Validation

Run the four test suites from the repository root:

    python -B -m unittest discover -s synthetic_inflow/tests -v
    python -B -m unittest discover -s prior_posterior/tests -v
    python -B -m unittest discover -s reservoir_operation/tests -v
    python -B -m unittest discover -s workflows/tests -v

Tests check calendar length, exact volume aggregation, seed reproducibility,
probability normalization, quantile boundaries, Bayes' theorem, RPS, water
balance, a known finite-grid optimum, two-dekad path risk, child-stage
risk screening, and integrated replay.

## Availability, citation and release status

No observed inflow, reservoir-operation data, archived pseudo-hindcasts,
or generated research scenarios are included. The limited
[Fig. 3(e) aggregate](figure_data/README.md) is the only manuscript-derived
figure dataset in this public repository. It supplies two aggregate series for one panel, not the
other panels or the numerical results of the paper. The manuscript currently
says restricted historical data and derived supporting data may be requested
from the corresponding author. This public deposit does not claim full G8
compliance; see [reproducibility status](docs/reproducibility.md).

The nine repository software authors and their order were confirmed by the
repository owner. Cite the archived public demonstration as version 0.1.0,
DOI [10.5281/zenodo.23614749](https://doi.org/10.5281/zenodo.23614749).
The [GitHub release](https://github.com/FAN2943637815/endogenous-reservoir-storage-demo/releases/tag/v0.1.0)
is the source of that immutable archive. `CITATION.cff` identifies the software
release; the manuscript should be cited separately for its scientific claims.
The DOI identifies this **limited demonstration**, not a deposit of all G8
materials or a numerical reproduction of the paper.
`LICENSE` records the current no-license-granted status pending approval;
permission to redistribute has not been inferred from the manuscript.
Version 0.1.0 and its publication status are described in `CHANGELOG.md`.
