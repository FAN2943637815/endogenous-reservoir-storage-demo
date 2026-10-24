# Data schema and units

All public CSV/JSON files are UTF-8. A calendar dekad is days 1–10,
11–20, or 21–month end. `dekad` is one-based, 1–36. A dekad volume
`V` is the sum of daily `Q_d × 86400 / 10^8`, where `Q_d` is m³/s.
The third-dekad duration changes with the calendar, including leap years.

| File | Required fields | Interpretation |
| --- | --- | --- |
| `synthetic_inflow/member_N_dekad.csv` | `year`, `dekad`, `days`, `annual_state`, `inflow_1e8m3` | One generated member. `annual_state` is an illustrative dry/normal/wet label. |
| `prior_posterior/evaluation.json` | `year`, `dekad`, `actual_1e8m3`, `pseudo_forecast_1e8m3`, `previous_state`, `observed_state`, `prior`, `posterior`, `prior_rps`, `posterior_rps`, `kl_information_gain` | Probability arrays are ordered dry to wet and sum to one. |
| `reservoir_operation/candidate_screening.csv` | `target_1e8m3`, `bellman_objective`, `expected_shortage_ratio`, `critical_probability`, `cvar_shortage_ratio`, `risk_feasible` | First-period screening of every finite-grid candidate. Ratios and probabilities are dimensionless. |
| `reservoir_operation/operation.csv` | `start_storage`, `inflow`, `loss`, `target_storage`, `supply`, `shortage`, `spill`, `end_storage` | Every volume is 10^8 m³. `start+inflow-loss=supply+spill+end`. |
| `integrated/probabilities.json` | `year`, `dekad`, `actual_1e8m3`, `pseudo_forecast_1e8m3`, `previous_state`, `observed_state`, `prior`, `posterior`, `prior_rps`, `posterior_rps` | Held-out synthetic year; current observed inflow is used only for ex-post evaluation and forecast construction. |
| `integrated/decisions.csv` | `target_1e8m3`, `objective`, three risk diagnostics, `risk_feasible`, `fallback` | Target selected before current inflow is executed. |
| `figure_data/fig3e_dekad_summary.csv` | `dekad_index`, `mean_delta_rps`, `mean_kl_divergence` | Genuine study-derived, dimensionless 36-point aggregate for Fig. 3(e); unlike all demonstration outputs above, it is not synthetic. |

The Fig. 3(e) CSV is the only deposited manuscript figure data. Its
[scope note](../figure_data/README.md) explains the aggregation and limits.

Example outputs under `outputs/` are ignored by Git. The optional curated
`examples/` files contain only freshly generated synthetic material. No
research record is required by any public schema.

The independent reservoir example uses prescribed toy probabilities. The
integrated workflow uses computed posterior probabilities. Neither is an
archived study posterior sequence.
