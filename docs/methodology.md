# Manuscript equations and public calculations

Equation labels refer to the current `manuscript.tex` source inspected on
22 October 2026. Printed equation numbers are indicative; use the labels
when a later compilation renumbers equations. This document explains
computations rather than reproducing manuscript prose.

## 1. Synthetic inflow and scenario role

| Manuscript equation | Variables and units | Public function | Scope |
| --- | --- | --- | --- |
| (C.1), `eq:app_boxcox_transform` | Daily `Q_d` in m³/s; `delta` in m³/s; transformed `Y_d` | `synthetic_inflow.generation.generate_daily` | Uses the `lambda=0` log case and fixed `delta=1` m³/s. |
| (C.2), `eq:app_seasonal_standardization` | Calendar position `kappa(d)`; transformed mean and SD | `generate_daily` | Represents the seasonal transformed mean with a fixed sinusoid; does not estimate a climatology. |
| (C.5), `eq:app_periodic_ar_model` | Standardized `Z_d`, annual state `R_y`, innovation | `generate_daily` | Restricted AR(1) with one coefficient and Gaussian innovation; annual state is a simple seeded Markov chain. |
| (C.6), `eq:app_inverse_transform` | Simulated daily `Q_d` in m³/s | `generate_daily` | Applies exponential inverse and a nonnegative floor. |
| (C.7), `eq:app_screening_distance` | Weighted distance between observed and simulated diagnostics | Not implemented | No observed calibration data or approved screening parameters. Public `diagnostics.summarize_dekad` describes its output but does not claim to accept study scenarios. |

`aggregate_dekad` multiplies each daily discharge by exactly 86,400 s
and divides by 10^8 m³, then sums calendar days within each dekad. The
published Historical-like and Extreme-dry scenarios are offline tests.
The public generator's output is only a teaching sequence.

## 2. Historical prior

For arrival period `t`, smaller state indices are drier. `Q_(y,t)` is a
dekad inflow volume in 10^8 m³; `K` is dimensionless.

| Manuscript equation | Calculation | Public function |
| --- | --- | --- |
| (A.1)–(A.2), `eq:app_quantile_thresholds`, `eq:app_state_assignment` | Per-dekad empirical thresholds at `m/K`; a value on a threshold remains in the lower state | `states.fit_dekad_states`; `StateDefinition.classify` |
| (A.3)–(A.5), `eq:app_circular_distance`, `eq:app_neighborhood`, `eq:app_weight_function` | `Delta(t,r)=min(|t-r|,36-|t-r|)` and `w=exp[-Delta²/(2 tau²)]` | `prior.circular_distance`; `prior.seasonal_weight` |
| (A.6)–(A.8), `eq:app_weighted_frequency`, `eq:app_cross_year_state`, `eq:app_initial_state_sample_size` | Weighted transitions; period 1 follows prior year's period 36; missing pairs excluded | `prior.build_transition_matrices` |
| (A.9)–(A.11), `eq:app_climatological_probability`, `eq:app_smoothed_transition_probability`, `eq:app_smoothing_strength` | `p0_j=sum_i n_ij/sum_i,j n_ij` and `P_ij=(n_ij+K p0_j)/(n_i+K)` | `prior.build_transition_matrices` |
| (9)–(11), `eq:bayes_smoothing`, `eq:transition_matrix`, `eq:historical_prior` | Row-stochastic seasonal matrix and prior row given previous observed state | `prior.build_transition_matrices`; `prior.prior_from_previous` |
| (A.12)–(A.13), `eq:app_training_year_set`, `eq:app_loyo_smoothed_transition_probability` | Evaluation year excluded from fitting | `states.fit_dekad_states(..., excluded_year=...)` and `prior.build_transition_matrices(..., excluded_year=...)` |

The public script holds out one **synthetic** year. The manuscript's 74-year
leave-one-year-out verification and its input workbooks are not included.

## 3. Forecast likelihood, posterior and propagation

| Manuscript equation | Calculation and units | Public function |
| --- | --- | --- |
| (12), `eq:forecast_error_model` | `ln Qhat = ln Q + epsilon`; `epsilon~N(0,sigma²)`; both `Q` and `Qhat` are 10^8 m³/dekad | `forecast.pseudo_hindcast` |
| (13), `eq:forecast_likelihood` | Positive forecast density conditional on a positive candidate inflow | `forecast.log_likelihood` |
| (14)–(15), `eq:forecast_support`, `eq:forecast_support_approx` | Interval support concept; reported study results used state representatives | `forecast.forecast_support` implements only midpoint approximation |
| (16), `eq:posterior_state_probability` | `pi_post[k]=pi_prior[k] ell[k]/sum_j pi_prior[j] ell[j]` | `posterior.bayes_update`, implemented in log space |
| (17), `eq:mixed_posterior_distribution` | Mixture of within-state inflow densities | Not reconstructed; the demo carries discrete state probabilities and midpoint inflows |
| (18), `eq:posterior_propagation` | Row-vector multiplication by nonstationary `P_(t+s)` | `prior.propagate`; `risk.evaluate_risk` uses transitions in paths |
| (21), `eq:path_probability` | `pi_t[k_t]` times future transition probabilities | `risk.evaluate_risk`, exact finite enumeration |

The current posterior is a decision-time information state. No future
observation or forecast is introduced within the risk window. At the next
rolling stage, `workflows.run_integrated_demo` obtains a new prior and
posterior from the new preceding observation and pseudo-forecast.

## 4. Water balance, risk and target selection

All storage, inflow, loss, demand, supply, shortage and spill volumes are
10^8 m³; probabilities, benefits and risk ratios are dimensionless.

| Manuscript equation | Public calculation | Public function |
| --- | --- | --- |
| (2), (4)–(5), `eq:water_balance`, `eq:actual_supply`, `eq:shortage_state` | Available water, demand-bounded supply, shortage, end storage and spill | `system.realize` |
| (6)–(7), `eq:stage_benefit`, `eq:expected_benefit` | `100 r/D - 10 max(a-D,0)/D`, averaged under current probabilities | `system.stage_benefit`; `decision.choose_target` |
| (22)–(25), `eq:path_storage_initial`, `eq:path_storage_evolution`, `eq:path_shortage`, `eq:path_shortage_loss` | Current state determines current shortage; the next period starts at candidate `S_(t+1)`; divide both shortages by both demands for `h=2` | `risk.evaluate_risk` |
| (26), `eq:cumulative_shortage_risk` | Expected demand-normalized path shortage | `risk.evaluate_risk` |
| (27), `eq:critical_storage_risk` | Probability that candidate start or projected next end storage breaches the toy critical threshold | `risk.evaluate_risk` |
| (28), `eq:cvar_shortage_risk` | Worst 10% probability-mass average of normalized path shortage | `risk.weighted_cvar` |
| (30)–(31), `eq:engineering_feasible_domain`, `eq:risk_feasible_domain` | Bound-constrained candidate grid, then three risk comparisons | `system.engineering_candidates`; `risk.is_feasible` |
| (32)–(34), `eq:bellman_recursion`, `eq:terminal_value`, `eq:optimal_storage` | Current expected benefit plus one risk-screened continuation stage and terminal storage reward | `decision.choose_target`; `terminal_storage_value` |
| (35), `eq:fallback_solution` | Minimize maximum standardized threshold violation, then maximize Bellman value | `risk.maximum_standardized_violation`; `decision.choose_target` |

The teaching model uses a fixed future supply-above-critical rule for path
risk, one reservoir, a fixed volume grid and two risk-screened Bellman
stages. It does not include the source system's level–storage conversion,
sector demands, seasonal flood limit, required release or outlet
constraints. The current manuscript's `h=2` risk window includes the
current state and one future state: `K^h=K²` positive-probability paths.
The public test checks this path count and the current-period contribution
to the normalized shortage ratio.

## 5. Verification metrics

`evaluation.ranked_probability_score` implements normalized RPS from
Eqs. (D.1)–(D.4). `evaluation.kl_information_gain` implements Eq. (D.5)
without replacing exact zero-prior events by invented positive mass;
`low_inflow_auc` implements the discrimination concept of Eqs. (D.6)–(D.7).
In the operation project, `total_shortage` and `supply_reliability` use
Eqs. (D.8)–(D.11); `critical_storage_hit_frequency` uses Eq. (D.13).
`annual_shortage_cvar` follows the manuscript's conditional mean above
empirical VaR (Eqs. D.16–D.17). This annual volume statistic is distinct
from the optimization's normalized finite-path CVaR in Eq. (28).
