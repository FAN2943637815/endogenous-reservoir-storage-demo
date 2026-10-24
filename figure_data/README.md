# Limited numerical data for manuscript Fig. 3(e)

`fig3e_dekad_summary.csv` contains 36 calendar-dekad x positions and two
dimensionless aggregate y series calculated for the Fig. 3(e) panel.
It is a **small aggregate extracted from the actual verification
calculation**, not a synthetic demonstration. It is included in this
local release draft under the user's instruction to share a limited
amount of figure data. No public upload or redistribution license is
asserted by this file.

| Column | Meaning |
| --- | --- |
| `dekad_index` | Calendar-dekad position, 1–36; no year or event date |
| `mean_delta_rps` | Mean of `RPS_prior - RPS_posterior` for that dekad |
| `mean_kl_divergence` | Mean posterior-versus-prior KL divergence for that dekad |

The two means were calculated by grouping 2,662 verification
cases in the inspected source calculation for Fig. 3(e). Each dekad group contains
73 or 74 cases. Values were rounded to six decimal places. Across
the complete case table, mean ΔRPS rounds to 0.128 and mean KL to
1.113, matching the manuscript text. To redraw the numerical traces
for this panel, use `dekad_index` as x and the two mean columns as
separate y series. The inspected plotting source postdates the manuscript
image. The exact code version that rendered that image was not established,
so byte-for-byte agreement with the submitted image is not asserted.

The file contains no case-level score, observed inflow, forecast,
state probability, year, date, reservoir-operation value, engineering
parameter, internal program name, or internal path. The restricted
case-level source table and plotting program are not included.
Aggregation limits direct disclosure but is not a claim that all
research-derived values are unrestricted.

This file **does not** reproduce the distribution, representative-case
or ROC panels of Fig. 3, any other manuscript figure, or the paper's
operation results. The remaining figure-source requests and DOI
status are recorded in
[the G8 audit](../docs/reproducibility.md) and
[figure inventory](../docs/figure_data_inventory.md).
