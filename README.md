# What Builds a Football Team — Open Data Package

**Paper:** *What Builds a Football Team: A 24-Season Anatomy of Roster Construction, Misallocation, and the Transfer Portal*
**Author:** Competition Factor
**Venue:** MIT Sloan Sports Analytics Conference — Football Track (Research Paper)
**Live ratings:** every player rating in this study is publicly browsable at **competitionfactor.com**

This repository contains the **derived study datasets** behind the paper. Together they reproduce
every table and figure in the paper. A worked proof is in
[`examples/verify_reproduction.py`](examples/verify_reproduction.py), which recomputes three
headline numbers (a factor weight, the running-back misallocation rate and penalty, and one
leave-one-season-out row) using nothing but the files in this repository.

---

## Data, not code: what is and is not here

This is a **data** release. The opponent-adjusted, per-game **player-rating engine** that produced
the underlying ratings is **proprietary and is not included** — it is the author's measurement
instrument, and its outputs are already publicly verifiable on competitionfactor.com.

What we release instead is the engine's output *as the study consumes it*: each player-season is
reduced to a **vector of binned quintile levels** (0 = weak … 4 = elite, ranked within
season × tier × position pool). These levels — **not** the raw component ratings — are the actual
input to every model in the paper, and they are sufficient to reproduce every result.

Concretely, in the player-season files we deliberately **exclude the raw component "book" ratings**
(the per-dimension elos that make up the spider chart), because publishing them would let someone
reverse-engineer the engine's internals. We keep the player's **name, season, team, and quintile
levels** (public sports facts and the study's true input), plus a single **overall percentile**
(`overall_pctile`, rank of the player's overall rating within season × tier). The overall percentile
is monotonic in the raw overall rating within any one roster, so it preserves every within-roster
ranking the study needs (e.g. "is the most-used back the best-rated back?") without exposing the
engine. We verified this equivalence: best-rated identification by overall percentile matches
identification by the raw rating in 100% of backfields.

**License (recommended, pending author confirmation):** the data are released under
**Creative Commons Attribution 4.0 (CC BY 4.0)** — free to share and adapt with attribution. See
[`LICENSE`](LICENSE). *This is a recommendation; confirm before public release.*

---

## Repository layout

```
data/        derived study datasets (player-season levels, team panels, transfers, coaches)
results/     the paper's result tables, as machine-readable CSV
examples/    verify_reproduction.py — recomputes 3 paper numbers from data/ + results/
```

---

## `data/` — file-by-file schema

### Player-season binned level vectors

**`offense_player_season_levels.csv`** (53,704 rows) — one row per player-season-book.
Columns: `cpid` (canonical player id), `name`, `season`, `team` (canonical school key), `tier`
(P4 / FBS / FCS), `book` (qb/rb/wr/te), `slot` (usage rank within the unit, 1 = most-used),
`usage` (season attempts/carries+catches — the usage measure that defines the slot),
`overall_pctile` (player's overall-rating percentile within season × tier),
then `<DIM>_level` columns (0–4, blank where the dimension does not apply to that book):
`Eff, Yds, YPA, YPC, YFS, Pct, TD, INT, RushYds, RushYPC, Rec, RecYd, RecYPC`.
QB dims = Eff/Yds/YPA/Pct/TD/INT/RushYds/RushYPC; RB = Yds/YPC/YFS/TD/Rec/RecYd/RecYPC;
WR & TE = Rec/Yds/YPC/TD. (`Eff` and `YFS` are the arithmetic composites the paper drops in the
primary fit; they are retained here so the composite check is reproducible.)

**`defense_player_season_levels.csv`** (49,857 rows) — one row per player-season-group.
Columns: `cpid`, `name`, `season`, `team`, `tier`, `group` (DL/LB/DB), `slot` (usage rank by
tackles, 1 = most tackles), `usage_tackles`, `overall_pctile`, `group_source`
(`roster` = position from roster data, `inferred` = filled by classifier — see paper Limitations),
then seven `<DIM>_level` columns (0–4): `Tkl, TFL, Sack, INT, FF, PD, QBH`.

### Team-season panels

**`offense_team_season_panel.csv`** (5,698 rows) — one row per team-season; the panel every
offensive model fits. Key columns: `cteam`, `season`, `tier`; outcome `off_sum` (season-end
pass_o + rush_o unit strength), `off_pct` (percentile within season × tier), `off_pct_allD1`,
`top_decile` (1 = "great"); slot level features `qb1_YPA … te1_TD` (quintile levels, matching the
player files); order-invariant corps counts `rb_ngood_*`, `rb_nelite_*`, `rb_max_*`, `wr_ngood_*`,
etc.; talent controls `talent_sum`, `talent_pct`, `talent_q`, and per-book slot-fill counts `*_n`.
Contains **no** raw component elos.

**`defense_team_season_panel.csv`** (5,698 rows) — defensive mirror. `cteam`, `season`, `tier`;
outcomes `def_sum`, `def_pct`, `def_pct_allD1`, `pass_d_pct`, `rush_d_pct`, `top_decile`; slot level
features `dl1_Sack … db5_INT`; corps counts; talent controls.

**`offense_team_talent_decomposition.csv`** / **`defense_team_talent_decomposition.csv`**
(5,127 rows each) — the talent-vs-composition split used in §4.1/§4.2. Columns: `cteam`, `season`,
`tier`, `off_end`/`def_end` (raw unit elo), `pred_neutral` (talent-only prediction),
`comp_effect` (composition lift over talent), `resid_full`, `shortfall_vs_neutral`, `talent_index`,
`tal_resid`.

### Transfer / portal datasets

**`transfer_backtest.csv`** (810 rows) — the pre-registered out-of-time portal backtest
(§4.9, Table 8). One row per transfer move (2024–25 test classes). Columns: `cpid`, `name`, `pos`,
`dest` (destination school), `season`, `proj_mag` (projected mix score), `fit_gain`, `fit_talent`,
`fit_scheme`, `team_resid`, `player_beat`, `realized_mag`, `book_elo` (overall rating, public),
`player_dev` (RTM-adjusted development-z outcome).

**`offense_transfer_persistence.csv`** (723) / **`defense_transfer_persistence.csv`** (822) —
year-over-year portability sets behind Table 7. Per transfer: `cpid`, `name`, `pos`/`grp`, source
and destination, `season`, `newscore`, `player_dev`, and unit-residual context.

**`counterfactual_panel.csv`** (244 rows) — destination-team no-move counterfactual (§3, §4.9).
Columns include `cpid`, `name`, `pos`, `dest`, `season`, `newscore`, `cteam`, `off_pct` (realized),
`cf` (counterfactual expected unit percentile without the incoming transfer), `surprise`
(actual − counterfactual), `imp`, `nin`, `masstot`, `massshare`.

**`preseason_projection_panel.csv`** (2,917 rows) — the preseason forecasting panel (§4.10,
Table 9). One row per FBS team Y→Y+1. Columns: `cteam`, `season`, `tier`, `off_pct` (realized),
`talent_pct`, `prior_off`, `ret_talent` (returning-core talent, departures excluded), `n_return`,
`in_tal`, `n_in` (incoming transfers), `oc_change`, `hc_change`, `oc_in_fe` (incoming OC shrunk
fixed effect), `oc_fe_known`, `prog_loo` (program leave-one-out mean), `pred` (projection), `dec`,
`abserr`, `swing`, `pred_swing`.

### Coaching datasets (§2, §4.8)

**`coaches_fbs.csv`** (3,264 rows) — program-season coordinator panel: `school`, `season`,
`head_coach`, `off_coordinator`, `def_coordinator`, `source`, `confidence`.

**`coach_changes.csv`** (1,655 rows) — derived staff-change events: `school`, `season`,
`change_type` (HC/OC/DC), `from`, `to`, `prev_season`.

**`coordinator_effects_offense.csv`** (365) / **`coordinator_effects_defense.csv`** (375) —
per-coordinator shrunk fixed effects behind Figure 4: `oc`/`dc`, `n` (seasons), `eff` (shrunk
effect over roster+program expectation, elo), `raw` (unshrunk).

---

## `results/` — the paper's tables, as data

| File | Paper table / figure |
|---|---|
| `offense_factor_weights.csv` | **Table 3** — offense slot × dimension weight map (`slot,n,dim,weight,tadj,tadj_n`) |
| `defense_factor_weights.csv` | **Table 4** — defense group × slot × dimension weight map (`slot,dim,weight,tadj,flag`) |
| `offense_failure_table.csv` | **§4.4** — offense failure / sink cells (`cell,n,lift,tadj,sink_weight`) |
| `defense_failure_table.csv` | **§4.4** — defense failure cells |
| `loso_robustness.csv` | **Table 3b** — rotating leave-one-season-out (23 refits) |
| `balance_interaction.csv` | **Table 2** — balance: the central talent-controlled interaction |
| `asymmetry_map.csv` | **Table 5** — weak-penalty vs elite-bonus asymmetry map |
| `depth_curves.csv` | **Table 6** — where the quality signal dies, by unit |
| `portability_persistence.csv` | **Table 7** — year-over-year persistence, transfer vs returning |
| `portal_backtest_summary.csv` | **Table 8** — portal backtest: player win, team null |
| `preseason_variant_comparison.csv` | **Table 9** — preseason projection variant comparison |

`offense_factor_weights`, `defense_factor_weights`, `offense_failure_table`,
`defense_failure_table`, and `loso_robustness` are the direct machine outputs of the study's fits
on the packaged panels. `balance_interaction`, `asymmetry_map`, `depth_curves`,
`portability_persistence`, `portal_backtest_summary`, and `preseason_variant_comparison` are the
paper's reported summary tables transcribed to CSV (the source of truth being the paper); their
underlying panels ship in `data/`, so each remains reproducible from this repository.

### How each paper table maps to the data

- **Table 1** (study universe) — row counts and coverage: `offense_team_season_panel.csv`,
  `defense_team_season_panel.csv`, `coaches_fbs.csv`.
- **Table 2** (balance) — recompute from `*_team_season_panel.csv` (pass/rush split × outcome);
  reported in `results/balance_interaction.csv`.
- **Table 3 / 3b / 4** — `results/offense_factor_weights.csv`, `results/loso_robustness.csv`,
  `results/defense_factor_weights.csv`; refit from the team panels (see the example script).
- **Table 5, §4.4 failure** — `results/asymmetry_map.csv`, `results/*_failure_table.csv`; from the
  player-level and team panels.
- **Table 6** (depth) — `results/depth_curves.csv`; from the player-level files + team outcomes.
- **Table 7** (portability) — `results/portability_persistence.csv`; from the transfer-persistence
  files.
- **Table 8** (portal) — `results/portal_backtest_summary.csv`; from `transfer_backtest.csv` +
  `counterfactual_panel.csv`.
- **Table 9** (preseason) — `results/preseason_variant_comparison.csv`; from
  `preseason_projection_panel.csv`.
- **Figure 4** (coordinators) — `coordinator_effects_offense.csv`, `coordinator_effects_defense.csv`.

---

## Reproduce it yourself

```bash
python3 examples/verify_reproduction.py
```

Requires `pandas`, `numpy`, `scikit-learn`. The script recomputes, from the packaged files only:
(1) the heaviest offensive weight cell — QB1 passing efficiency = 100.0, ridge R² = 0.512;
(2) running-back misallocation — 30% of backfields, 0.79× greatness penalty;
(3) one leave-one-season-out held-out composition ΔR² (2015 = 0.439). All three match the paper.

---

## Citation

```
Competition Factor. "What Builds a Football Team: A 24-Season Anatomy of Roster Construction,
Misallocation, and the Transfer Portal." MIT Sloan Sports Analytics Conference, 2026.
Derived data: competitionfactor.com.
```

## Notes and caveats

- **Scope:** FBS + FCS (P4 / G5-FBS / FCS), 2003–2025, N = 5,698 team-seasons.
- **Levels are within-peer:** "elite" = top quintile of *starting-caliber players at that position,
  that season, that tier* — not an absolute standard.
- **Defense position tags:** 22–29% of defensive slot players' groups are classifier-inferred
  (`group_source = inferred`); every defensive headline replicates on the roster-only subset, but
  the noise is real (paper Limitations).
- **Box-derived:** ratings cannot see snap counts, coverage responsibility, or blocking; the
  RB-TD depth and defensive-misallocation reads carry explicit "needs play-by-play" caveats.
