# Reproducibility status against reviewer G8

This public repository separates a verifiable demonstration calculation from access to
the actual experiments. “Provided” below means present in this repository,
not available from the corresponding author on request.

| G8 item | Public status | What can be checked | Still required for manuscript reproduction |
| --- | --- | --- | --- |
| Posterior-updating program | **Partially provided** | Per-dekad state boundaries, weighted prior, representative-value log likelihood, stable Bayes update, propagation, RPS/KL/AUC on synthetic inputs | Authorized historical data, exact fitted state tables, archived pseudo-hindcasts, full 74-fold evaluation and source–manuscript consistency resolution |
| Optimization program | **Partially provided** | Exact toy water balance, path probabilities, three risk ratios over current and next dekad, stage threshold screens, finite-grid Bellman search and fallback | Original Java solver or validated equivalent, level–storage–area curve, demand and operation constraints, exact reported experiment configurations |
| Pseudo-hindcast series | **Not provided** | The prescribed error equation can generate a new seeded synthetic series | Actual study pseudo-hindcast values and provenance |
| Generated runoff scenarios | **Not provided** | A separate illustrative generator and its diagnostics can be run | Archived Historical-like and Extreme-dry members, screening parameters and validation records |
| Numerical files behind figures and tables | **Partially provided in this public repository** | The [Fig. 3(e) CSV](../figure_data/fig3e_dekad_summary.csv) contains 36 positions and two dimensionless mean series from the inspected aggregation calculation; the [figure inventory](figure_data_inventory.md) maps all remaining gaps | Author-approved source numbers for the other quantitative panels and tables |
| Citable release and DOI | **Not established** | Public GitHub repository, `CITATION.cff` and version notes exist | Confirmed metadata and rights, GitHub release, Zenodo archive and assigned DOI |
| Computational checks available now | **Provided for public mode** | Three independent demos and one integrated demo, per-project mathematical tests, seed replay, probability sums and balance | Independent verification of reported case-study outcomes |
| Manuscript results independently reproducible | **No** | Only the published mathematical relationships and toy outputs can be checked | All restricted inputs, exact code path and experiment outputs above |

The manuscript's data-availability paragraph states that restricted
historical data cannot be made public and derived data may be requested
from the corresponding author. This repository does not reinterpret
“available on request” as “publicly deposited.” One real aggregate for
Fig. 3(e) is publicly included; synthetic demonstrations are kept separate
and do not satisfy G8's remaining data requests.

This repository should not be advertised as an exact reproduction of
posterior RPS/AUC, supply performance, stress tests, ablations or sensitivity
figures. The implementation differences in
[scope and consistency](implementation_scope.md) also need author review.

## Release and DOI preparation

The repository has a version number, citation metadata, public GitHub URL,
tests and an explicit data boundary. Before a citable version archive:

1. Confirm software authorship and choose a license with the rights holders.
2. Review the included Fig. 3(e) aggregate and any other candidate derived
   files privately; approve each file separately for public release.
3. Reconcile source–manuscript differences or identify the exact version
   used for each reported result.
4. Run the documented commands on the release commit and attach a versioned
   test record.
5. Create a GitHub release and a Zenodo version archive only after
   authorization, then insert the assigned DOI into `CITATION.cff` and
   the manuscript response.

The reviewed 55-file tree was uploaded to
<https://github.com/FAN2943637815/endogenous-reservoir-storage-demo> on
24 October 2026. No Zenodo DOI has yet been verified. See the
[DOI preparation checklist](doi_release_checklist.md).
