# Local G8 audit — updated 24 October 2026

## Scope and evidence

The current `manuscript.tex` was read without modification, including
Methods, Appendix A (prior), Appendix C (scenario generation), risk and
Bellman equations, experimental design, results, and Data availability.
`references.bib` was read; all 13 images referenced by the TeX source
exist alongside the manuscript. The three original project directories
were inspected read-only: historical-prior Python, Java reservoir
operation, and synthetic-inflow Python. Their observed workbooks,
engineering inputs, generated research outputs, code, and manuscript
files were not copied or executed.

Only this `gitHub` directory was edited. Public code here consists of
newly written standard-library demonstrations and synthetic inputs. The
only study-derived numeric file in the prospective Git inclusion list is
the limited Fig. 3(e) aggregate. The reviewed 55-file tree is now public at
<https://github.com/FAN2943637815/endogenous-reservoir-storage-demo>.
No research source, original study data,
engineering input, case-level record, internal name, or private path is
included. `.private_review/` and `outputs/` are Git-ignored.

## Reviewer G8, item by item

| Requested public material | Audit status | Evidence and exact limit |
| --- | --- | --- |
| Posterior-updating code | **Partly addressed** | `prior_posterior/` has executable state construction, seasonal weighting, smoothing, pseudo-forecast likelihood, stable Bayes update, propagation and scores. It is newly written on synthetic inputs, not the exact research program or fitted state tables. |
| Optimization code | **Partly addressed** | `reservoir_operation/` has executable toy water balance, current-plus-next-dekad path risk, three thresholds, two-stage risk-screened finite-grid Bellman search and fallback. The original Java solver, engineering curves and experiment settings are withheld. |
| Actual pseudo-hindcast series | **Not met** | The public generator creates a fresh seeded series from synthetic inflows. The archived study series and provenance are absent. |
| Actual generated scenarios | **Not met** | The public AR example is not the accepted 200-year Historical-like or Extreme-dry scenario set. Neither study scenario series is present. |
| Numerical data behind figures | **Partly addressed publicly** | The [Fig. 3(e) CSV](../figure_data/fig3e_dekad_summary.csv) gives 36 calendar-dekad x positions and two dimensionless mean series from the inspected aggregation calculation. The exact source version for the submitted image has not been established. All other quantitative figure panels and tables lack numerical source files; see [figure inventory](figure_data_inventory.md). |
| Public archive with DOI | **Not met** | The public GitHub repository exists, but no versioned Zenodo archive or assigned DOI has been verified. See the [DOI checklist](doi_release_checklist.md). |
| Full manuscript numerical reproduction | **Not possible from this repository** | Restricted observations and reservoir-operation inputs, research code/configurations and the derived materials above are missing. |

The manuscript currently says derived supporting material and code are
available from the corresponding author on reasonable request. That
statement does not satisfy G8's public-deposit request. Under the user's
current restrictions, the actual pseudo-hindcasts, study scenarios,
remaining figure/table numbers and core optimization code cannot be added. This repository must not
be described to the reviewer as fully meeting G8.

## Three independent public projects

| Project | Substantive modules | README, environment and minimal example | Mathematical check |
| --- | --- | --- | --- |
| `synthetic_inflow/` | Daily log-periodic AR generation, annual state chain, exact calendar-dekad aggregation, batch members, diagnostics and writers | Independent README; Python 3.10+ standard library; `python -B -m synthetic_inflow.demo` | Leap-year count, volume conservation, reproducible seed and diagnostics |
| `prior_posterior/` | Quantile states, weighted transition/smoothing, forecast support, Bayes update, propagation and scores | Independent README; same public environment; `python -B -m prior_posterior.demo` | Thresholds, row sums, cross-year pairs, Bayes probabilities, RPS/KL/AUC |
| `reservoir_operation/` | Water balance, path risk/CVaR, candidate/Bellman decision, rolling simulation and evaluation | Independent README; same public environment; `python -B -m reservoir_operation.demo` | Balance, normalized loss, `K²` paths for `h=2`, current shortage, child risk screen, known optimum and fallback |
| `workflows/` | Synthetic exchange across all three projects | Separate README; `python -B -m workflows.run_integrated_demo` | Seed replay and per-period mass balance |

`pyproject.toml` and `environment.yml` describe the public Python
environment. No third-party runtime package is required for these
demonstrations. The original projects have different scientific Python
and Java/JAR dependencies; those are outside this public runtime.

## Manuscript alignment corrected in this audit

The current manuscript defines a path `(k_t,...,k_(t+h-1))`. With
`K=5,h=2`, it has 25 paths: the current and next dekad. It includes
current-period shortage in the demand-normalized path loss and screens
risk at each Bellman recursion stage. An older draft of this repository
described a current-plus-two-future-period risk window and child stages
without a risk screen. The public risk code, tests and descriptions now
follow the current source on these points. The code remains a teaching
case because its future supply rule and engineering system are
deliberately simplified.

Three source-to-manuscript questions remain for the authors:
climatology arrivals versus valid predecessor pairs; summed raw
fallback exceedances in inspected Java versus the manuscript's maximum
standardized violation; and the original prior script's default `K=10`
versus the manuscript baseline `K=5`. The exact research run/version
must be established before any equivalence or numerical reproduction
claim. See [implementation scope](implementation_scope.md).

## Executed verification

Python 3.12.7 ran all four documented default commands successfully.
The four `unittest` commands passed:

| Suite | Tests passed |
| --- | ---: |
| `synthetic_inflow/tests` | 2 |
| `prior_posterior/tests` | 3 |
| `reservoir_operation/tests` | 6 |
| `workflows/tests` | 1 |

On 24 October 2026, all four test suites were rerun and passed (12 tests).
The Fig. 3(e) CSV was checked for its exact three-column schema, ordered
1–36 dekad indices, finite six-decimal values and prospective Git inclusion.
Relative Markdown links resolved, and a scan found no case-study name,
private path or internal program name in the prospective public files.

The integrated default run reported synthetic-year supply reliability
0.8191 and shortage 7.813 × 10^8 m³. The standalone reservoir example
selected target 5.0 × 10^8 m³ first. These numbers are generated
demonstration outputs only. The `--mode research` command exited with
the intended explicit missing-input/solver error before producing a
research result.

A Git inclusion check found 55 published files: public source,
tests, documentation, citation/license metadata, synthetic
examples, and the limited Fig. 3(e) aggregate. It found no Java/JAR, workbook, TeX/BIB or private-key file,
local absolute path or author email in that list. GitHub uploads were verified
by directory and commit on 24 October 2026. No versioned release, license grant
or DOI registration has yet been verified.
