# Computational workflow and interfaces

## Formal study chain

The manuscript's rolling chain is:

    observed historical dekad inflow -> per-dekad states and transition matrices
    previous observed state + current pseudo-hindcast -> prior + likelihood -> posterior
    posterior + future transition matrices -> inflow-state paths and risks
    risks + engineering limits -> feasible end-storage targets
    Bellman recursion -> chosen target -> observed-inflow execution -> next storage

The Historical-like and Extreme-dry generated runoff sequences enter **offline
robustness evaluation** after method calibration. They do not train the
historical prior. Forecast error generation and runoff scenario generation
are different computations with different roles.

## Public mode

| Output | Producer | Consumer | Unit |
| --- | --- | --- | --- |
| Daily `flow_cms` | `synthetic_inflow.generation.generate_daily` | `aggregate_dekad` | m³/s |
| `inflow_1e8m3` | `aggregate_dekad` | `fit_dekad_states`; held-out execution | 10^8 m³/dekad |
| `P_t` and representative inflows | `build_transition_matrices` and `StateDefinition` | `prior_from_previous`, `choose_target` | probability; 10^8 m³ |
| Synthetic `Qhat` | `pseudo_hindcast` | `forecast_support` | 10^8 m³ |
| Posterior `pi_t` | `bayes_update` | `choose_target` and `evaluate_risk` | dimensionless |
| Target and risk metrics | `choose_target` | `realize` and diagnostics | 10^8 m³; dimensionless |
| Realized supply, shortage, spill, storage | `realize` | `evaluation.py` | 10^8 m³ |

The public sample reserves its final generated year from threshold and
transition fitting. The observation of the current dekad is used for
pseudo-hindcast construction and later ex-post execution, but the
decision-facing functions receive only the forecast, preceding observation,
prior and posterior.

## Research implementation interface

The formal research implementation is not shipped. To connect an authorized
one, these inputs and outputs must be supplied explicitly:

1. **Historical prior provider:** 36 ordered period definitions, each with
   `K` nonnegative inflow intervals/representatives and a `K×K` transition
   matrix. Inputs are historical dekad volumes and evaluation-year exclusion;
   outputs are row-stochastic matrices and prior vectors.
2. **Forecast provider:** one forecast volume `Qhat_t>0` per rolling step,
   the prescribed or estimated log-error model, and a versioned record of
   how forecasts were constructed. Outputs are likelihood supports over
   exactly the same state definitions.
3. **Reservoir system provider:** initial storage, dekad demand, loss or
   evaporation model, level–storage conversion, seasonal upper bounds,
   critical rule-curve levels, required releases and outlet limits, with
   explicit volume and time units.
4. **Risk/solver provider:** nonstationary path probabilities, candidate
   target engineering checks, the three threshold comparisons, fallback
   choice, Bellman recursion, and a rolling execution record. The private
   Java system or an independently validated equivalent is required.
5. **Research evaluator:** the actual observed and generated scenarios,
   archived pseudo-hindcasts, experimental splits, benchmark settings and
   numerical figure/table data.

No call in `--mode research` resolves these absent providers to public demo
functions. It terminates before producing output.
