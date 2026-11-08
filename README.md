# What Builds a Football Team — Open Data Package

**Paper:** *What Builds a Football Team: A 24-Season Anatomy of Roster Construction, Misallocation, and the Transfer Portal*
**Author:** Competition Factor
**Venue:** MIT Sloan Sports Analytics Conference — Football Track (Research Paper)
**Live ratings:** every player rating in this study is publicly browsable at **competitionfactor.com**

This repository contains the **derived study datasets** behind the paper, plus the script and
images for every figure in it. Together they reproduce every table and figure in the paper. A worked proof is in
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
**Creative Commons Attribution-NonCommercial 4.0 (CC BY-NC 4.0)** — free to share and adapt with attribution. See
[`LICENSE`](LICENSE). *This is a recommendation; confirm before public release.*

---

## Repository layout

```
data/        derived study datasets (player-season levels, team panels, transfers, coaches)
results/     the paper's result tables (CSV) and fit diagnostics (JSON)
scripts/     paper_figs.py — draws every figure in the manuscript from data/ + results/
fig/paper/   the fourteen figures as embedded in the submitted paper (PNG)
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

## `results/` — the paper's tables and figure inputs, as data

Table and figure numbers follow the submitted manuscript: body Tables 1–2 and Figures 1–7;
Appendix Tables A1–A6 and Figures A1–A7.

| File | Paper table / figure |
|---|---|
| `offense_factor_weights.csv` | **Table A1 / Figure 2** — offense slot × dimension weight map (`slot,n,dim,weight,tadj,tadj_n`) |
| `defense_factor_weights.csv` | **Table A2 / Figure A1** — defense group × slot × dimension weight map (`slot,dim,weight,tadj,flag`) |
| `offense_failure_table.csv` | **§4.4, §4.8** — offense failure / sink cells (`cell,n,lift,tadj,sink_weight`) |
| `defense_failure_table.csv` | **§4.4** — defense failure cells |
| `loso_robustness.csv` | **Table A3 / Figure A2** — rotating leave-one-season-out (23 refits) |
| `balance_interaction.csv` | **§4.1 / Figure 1** — balance: the central talent-controlled interaction |
| `asymmetry_map.csv` | **Table A4 / Figure 4** — weak-penalty vs elite-bonus asymmetry map |
| `depth_curves.csv` | **Table A5 / Figure A4** — where the quality signal dies, by unit |
| `portability_persistence.csv` | **§4.7 / Figure A5** — year-over-year persistence, transfer vs returning |
| `portal_backtest_summary.csv` | **Table A6 / Figure 7** — portal backtest: player win, team null |
| `preseason_variant_comparison.csv` | **Table 2 / Figure A7** — preseason projection variant comparison |
| `diag.json`, `def_diag.json` | **Figure 3** — permutation-importance slot leverage (`leverage`: slot → [ΔR², SE]) and slot interactions, offense / defense |
| `e3_fe.json`, `def_e3.json` | **§4.8 / Figure 6** — coordinator-instrument summary (base vs +coordinator R², residual claimed, p10/p90 effect) |

`offense_factor_weights`, `defense_factor_weights`, `offense_failure_table`,
`defense_failure_table`, `loso_robustness`, and the four JSON diagnostics are the direct machine
outputs of the study's fits on the packaged panels. `balance_interaction`, `asymmetry_map`,
`depth_curves`, `portability_persistence`, `portal_backtest_summary`, and
`preseason_variant_comparison` are the paper's reported summary tables transcribed to CSV (the
source of truth being the paper); their underlying panels ship in `data/`, so each remains
reproducible from this repository.

### How each paper table and figure maps to the data

- **Table 1** (study universe) — row counts and coverage: `offense_team_season_panel.csv`,
  `defense_team_season_panel.csv`, `coaches_fbs.csv`.
- **Figure 1** (balance) — recompute from `*_team_season_panel.csv` (pass/rush split × outcome);
  reported in `results/balance_interaction.csv`.
- **Figure 2 / Table A1, Figure A1 / Table A2, Figure A2 / Table A3** (weight maps, LOSO) —
  `results/offense_factor_weights.csv`, `results/defense_factor_weights.csv`,
  `results/loso_robustness.csv`; refit from the team panels (see `examples/verify_reproduction.py`).
- **Figure 3** (positional leverage) — `results/diag.json`, `results/def_diag.json`; permutation
  importance on the team-panel ridge fit.
- **Figure 4 / Table A4, §4.4 failure** — `results/asymmetry_map.csv`, `results/*_failure_table.csv`;
  from the player-level and team panels.
- **Figure 5** (defense inversions) — correlations from `defense_team_season_panel.csv`; sack column
  of `results/defense_factor_weights.csv`.
- **Figure A3** (receiving-corps mix) — deep-threat / possession counts from
  `offense_player_season_levels.csv` joined to `offense_team_season_panel.csv`.
- **Figure A4 / Table A5** (depth) — `results/depth_curves.csv`; from the player-level files + team outcomes.
- **Figure A5, §4.7** (portability) — `results/portability_persistence.csv`; from the
  transfer-persistence files.
- **Figure A6, §4.8** (misallocation) — recomputed in `examples/verify_reproduction.py` from the
  offense player-level file + team panel.
- **Figure 6, §4.8** (coordinators) — `coordinator_effects_offense.csv`,
  `coordinator_effects_defense.csv`, `results/e3_fe.json`, `results/def_e3.json`.
- **Figure 7 / Table A6** (portal) — `results/portal_backtest_summary.csv`; from `transfer_backtest.csv` +
  `counterfactual_panel.csv`.
- **Table 2 / Figure A7** (preseason) — `results/preseason_variant_comparison.csv`; from
  `preseason_projection_panel.csv`.

---

## `scripts/` and `fig/` — the paper's figures

`scripts/paper_figs.py` draws all fourteen figures in the manuscript (Figures 1–7 and A1–A7) from
the files in `results/` and `data/`, and writes them to `fig/paper/`, where the committed PNGs are
the exact images embedded in the submitted paper. Figure file names carry their original study
numbering; the manuscript caption number is authoritative:

| Manuscript | File | Manuscript | File |
|---|---|---|---|
| Figure 1 | `fig1_balance.png` | Figure A1 | `fig3_weightmap_defense.png` |
| Figure 2 | `fig2_weightmap_offense.png` | Figure A2 | `fig5_loso.png` |
| Figure 3 | `fig4_leverage.png` | Figure A3 | `fig6_wr_mix.png` |
| Figure 4 | `fig7_asymmetry.png` | Figure A4 | `fig8_depth.png` |
| Figure 5 | `fig9_defense_inversion.png` | Figure A5 | `fig10_portability.png` |
| Figure 6 | `fig11_coordinators.png` | Figure A6 | `fig12_misallocation.png` |
| Figure 7 | `fig13_portal_backtest.png` | Figure A7 | `fig14_preseason.png` |

```bash
python3 scripts/paper_figs.py     # requires numpy, pandas, matplotlib
```

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
Misallocation, and the Transfer Portal." MIT Sloan Sports Analytics Conference, 2027.
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
