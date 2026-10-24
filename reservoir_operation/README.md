# Reservoir Drought Operation

## Scientific purpose

The manuscript makes the end-of-dekad storage target an endogenous choice.
This project demonstrates posterior-weighted inflow paths, risk screening,
finite-grid target selection, and realized water balance. Its standalone input
is a prescribed **toy distribution**. The integrated workflow supplies
probabilities calculated by the public Bayesian module. Neither route uses
case-study observations or the original Java solver.

## Mathematical background

All water volumes are in 10^8 m³. For start storage S, inflow Q, loss L,
and candidate end-storage target S', potentially available water is
S+Q-L-S' (manuscript Eq. 2). Effective supply is bounded by demand and
nonnegative availability (Eq. 4); shortage is demand minus supply (Eq. 5).
`system.realize` records supply, spill and actual end storage after the
current inflow is observed. A target can be missed under low inflow.

The current manuscript defines a look-ahead path as
`(k_t,...,k_(t+h-1))`, with probability equal to the current posterior
times `h-1` transition probabilities (Eq. `eq:path_probability`).
The public baseline uses `h=2`: the **current and next dekad**, giving
`K²` paths when all transition entries are positive. For each path,
current shortage uses the current inflow state. The projected following
period starts at the candidate target, as specified by Eq.
`eq:path_storage_initial`. A transparent teaching continuation rule
supplies water only above critical storage. Thus current and next-dekad
shortages enter the demand-normalized path loss (Eq.
`eq:path_shortage_loss`). Critical risk checks the candidate target and
the following projected end storage.

`risk.evaluate_risk` computes expected shortage ratio, critical-storage
violation probability and worst-tail CVaR at beta=0.90 (Eqs. 26–28).
Candidates pass only when all three meet their thresholds and the toy
physical check passes (Eq. 31). `decision.choose_target` maximizes the
expected current benefit plus a one-stage Bellman continuation and terminal
storage value (Eqs. 32–34). The continuation stage performs its own
one-period risk screen; if no target passes at either stage, the example
uses the minimum maximum-standardized violation fallback (Eq. 35).
This is a small illustrative search, not a copy of the research solver.

## Computational modules

| Module | Responsibility |
| --- | --- |
| `system.py` | Storage and stage bounds, realized water balance and stage benefit |
| `risk.py` | Posterior path probabilities, two-period risk ratios, weighted CVaR and feasibility |
| `decision.py` | Candidate grid, two-stage Bellman values, stage risk screens and fallback |
| `simulation.py` | Rolling choose–observe–execute loop |
| `evaluation.py` | Shortage, supply rate, critical-storage hits and annual shortage CVaR |
| `demo.py` | Standalone example with prescribed toy inflow states and probabilities |

## Inputs and outputs

`RollingInput` takes actual inflow, current stage, representative current
inflows, their probability vector, one transition matrix, next-period
representative inflows, and a next-period stage. All volumes use 10^8 m³.
Probabilities are dimensionless and each row sums to one. Inputs in
`demo.py` were invented solely for explanation.

The run writes `candidate_screening.csv`, `decisions.csv`,
`operation.csv`, and `summary.json` to
`outputs/reservoir_operation/`. The operation CSV reports start storage,
inflow, loss, target, supply, shortage, spill and actual end storage.

## Installation and execution

From the repository root, with Python 3.10+ and no third-party package:

    python -B -m reservoir_operation.demo

Use `--output-dir` to change the destination. No private Java class,
reservoir characteristic curve or observed data file is required.

## Example results and validation

With the toy input, target 1.0 × 10^8 m³ has expected two-period shortage
ratio 0.5 and critical-storage violation probability 1.0, so it is
screened out. Target 5.0 × 10^8 m³ passes and is selected in period 1.
The six-period sample has no realized shortage. These values are
generated-sample diagnostics only.

Run:

    python -B -m unittest discover -s reservoir_operation/tests -v

Tests check water conservation, supply/demand denominator, weighted-tail
CVaR, critical-risk rejection, `K²` path enumeration with current-period
shortage, a known finite-grid optimum, and least-violation fallback.

## Implementation scope and limits

The example has one reservoir, composite demand, a fixed upper bound, one
loss value per period, a finite storage grid and a two-stage horizon. The
risk path uses the candidate target as the following-period start, per the
manuscript; realized execution separately records missed targets. A fixed
future supply rule makes path calculation transparent. The code excludes
the actual level–storage–area curve, seasonal flood limits, sector demands,
required releases, outlet capacity, evaporation function, full Java
optimization and all manuscript numerical comparisons. Its outputs cannot
reproduce reported case-study results.
