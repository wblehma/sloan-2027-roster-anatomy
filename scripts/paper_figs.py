"""Publication figures for the Sloan paper (and the practitioner companion).

One visual system across all panels: offense = blue, defense = orange, polarity = blue (+) / red (−)
with a neutral-gray midpoint, hairline recessive grid, direct labels only where they carry the story.
Sources are the packaged files in results/ and data/ (loaded where a file exists; otherwise the
paper's reported tables, which are themselves transcribed in results/*.csv).

Run from the repository root:  python3 scripts/paper_figs.py
Writes PNGs to fig/paper/. Requires numpy, pandas, matplotlib.
"""
import json
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

RS = Path(__file__).resolve().parent.parent; RES = RS/'results'; DAT = RS/'data'; OUT = RS/'fig'/'paper'; OUT.mkdir(parents=True, exist_ok=True)

# ---- palette (validated: blue/orange adjacent ΔE 24.7 CVD; blue/red diverging poles 21.6) ----
OFF, DEF, NEG = '#2a78d6', '#eb6834', '#e34948'
OFF_LT, DEF_LT = '#9ec5f4', '#f3b79d'
MID = '#f0efec'
INK, INK2, MUTED, GRID, AXIS, SURF = '#0b0b0b', '#52514e', '#898781', '#e1e0d9', '#c3c2b7', '#ffffff'
DEEMPH = '#c3c2b7'
DIV = LinearSegmentedColormap.from_list('div', [NEG, MID, OFF])

plt.rcParams.update({
    'font.family': 'Helvetica Neue', 'font.size': 9, 'axes.titlesize': 10, 'axes.titleweight': 'medium',
    'axes.labelsize': 8.5, 'xtick.labelsize': 8, 'ytick.labelsize': 8, 'legend.fontsize': 8,
    'axes.edgecolor': AXIS, 'axes.linewidth': 0.6, 'xtick.color': MUTED, 'ytick.color': MUTED,
    'axes.labelcolor': INK2, 'text.color': INK, 'axes.titlecolor': INK,
    'xtick.major.size': 0, 'ytick.major.size': 0, 'xtick.major.pad': 4, 'ytick.major.pad': 4,
    'axes.grid': False, 'figure.facecolor': SURF, 'axes.facecolor': SURF, 'savefig.facecolor': SURF,
    'legend.frameon': False, 'figure.dpi': 110,
})
W = 7.0  # full text width, inches

def clean(ax, left=True, bottom=True, grid='y'):
    for s in ('top', 'right'): ax.spines[s].set_visible(False)
    ax.spines['left'].set_visible(left); ax.spines['bottom'].set_visible(bottom)
    if grid:
        ax.grid(axis=grid, color=GRID, lw=0.6); ax.set_axisbelow(True)

def title(ax, t, sub=None):
    ax.set_title(t, loc='left', pad=14 if sub else 8)
    if sub: ax.text(0, 1.02, sub, transform=ax.transAxes, fontsize=8, color=INK2, va='bottom')

def save(fig, name):
    fig.savefig(OUT/name, dpi=200, bbox_inches='tight', pad_inches=0.08); plt.close(fig); print('wrote', OUT/name)

def hbar(ax, y, x, color, h=0.55, left=0):
    """Thin horizontal bar growing from `left` (baseline)."""
    return ax.barh(y, x - left if np.ndim(x) == 0 else [v - left for v in x], left=left, height=h,
                   color=color, edgecolor=SURF, linewidth=1.5)

# ======================================================================================
# Fig 1 — Balance: talent-adjusted lift by roster shape (offense, defense)
# ======================================================================================
def fig1_balance():
    off = [('Both pass- & rush-strong', 1.75, '40.4%'), ('Pass-strong only', 1.13, '16.1%'),
           ('Rush-strong only', 0.75, '10.1%'), ('Neither', 0.39, '2.5%'),
           ('Both (top-2 talent quintiles)', 1.65, '44.0%'), ('Pass-only (top-2 talent)', 1.02, '21.8%'),
           ('Rush-only (top-2 talent)', 0.73, '14.9%')]
    dfn = [('Both pass-D & run-D strong', 1.27, '15.0%'), ('Pass-D only', 0.97, '10.1%'),
           ('Run-D only', 0.78, '8.5%'), ('Neither', 0.81, '8.4%')]
    fig, axes = plt.subplots(1, 2, figsize=(W, 3.3), gridspec_kw={'width_ratios': [1.25, 1]})
    for ax, rows, unit in zip(axes, [off, dfn], ['Offense', 'Defense']):
        labels = [r[0] for r in rows]; v = np.array([r[1] for r in rows]); y = np.arange(len(rows))[::-1]
        cols = [OFF if x >= 1 else NEG for x in v]
        ax.barh(y, v - 1, left=1, height=0.58, color=cols, edgecolor=SURF, linewidth=1.5)
        ax.axvline(1, color=INK2, lw=0.8)
        for yi, vi, r in zip(y, v, rows):
            ax.text(vi + (0.03 if vi >= 1 else -0.03), yi, f'{vi:.2f}', va='center', ha='left' if vi >= 1 else 'right', fontsize=8, color=INK)
        ax.set_yticks(y); ax.set_yticklabels(labels); ax.set_xlim(0.2, 2.05)
        ax.set_xlabel('talent-adjusted lift to top decile')
        clean(ax, left=False, grid='x'); ax.tick_params(axis='y', length=0)
        title(ax, unit, 'P(great | shape) ÷ talent-expected rate')
    fig.text(0, -0.04, 'Lift of 1.0 = exactly what raw talent predicts. Top-decile base rate 10.9%; n=5,698 team-seasons (2003–25). The "top-2 talent quintiles" rows hold total talent fixed and vary only its split.',
             fontsize=7.2, color=MUTED, va='top')
    fig.subplots_adjust(wspace=0.95)
    save(fig, 'fig1_balance.png')

# ======================================================================================
# Fig 2/3 — Weight maps (heatmaps, diverging)
# ======================================================================================
def heatmap(ax, M, rows, cols, vmax=100):
    Mm = np.ma.masked_invalid(M)
    ax.imshow(Mm, cmap=DIV, vmin=-vmax, vmax=vmax, aspect='auto')
    ax.set_xticks(range(len(cols))); ax.set_xticklabels(cols, fontsize=8)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels(rows, fontsize=8)
    ax.xaxis.tick_top(); ax.tick_params(length=0)
    for s in ax.spines.values(): s.set_visible(False)
    # white grid gaps
    ax.set_xticks(np.arange(-.5, len(cols), 1), minor=True); ax.set_yticks(np.arange(-.5, len(rows), 1), minor=True)
    ax.grid(which='minor', color=SURF, lw=2); ax.tick_params(which='minor', length=0)
    for i in range(len(rows)):
        for j in range(len(cols)):
            v = M[i, j]
            if np.isnan(v): continue
            strong = abs(v) > 55
            ax.text(j, i, '0' if abs(v) < 0.5 else f'{v:.0f}', ha='center', va='center', fontsize=7.6,
                    color=SURF if strong else INK, fontweight='medium' if abs(v) >= 50 else 'normal')

def fig2_offense_map():
    fw = pd.read_csv(RES/'offense_factor_weights.csv')
    rows = ['QB1', 'QB2', 'RB1', 'RB2', 'RB3', 'WR1', 'WR2', 'WR3', 'WR4', 'TE1']
    cols = ['Yds', 'YPA/YPC', 'Pct', 'TD', 'INT', 'RushYds', 'RushYPC', 'Rec', 'RecYd', 'RecYPC']
    dimmap = {'YPA': 'YPA/YPC', 'YPC': 'YPA/YPC'}
    M = np.full((len(rows), len(cols)), np.nan)
    for _, r in fw.iterrows():
        slot = f"{r.slot}{int(r.n)}"; d = dimmap.get(r.dim, r.dim)
        if r.slot == 'RB' and r.dim == 'Yds': d = 'Yds'
        M[rows.index(slot), cols.index(d)] = r.weight
    fig, ax = plt.subplots(figsize=(W, 4.1))
    heatmap(ax, M, rows, cols)
    title(ax, 'Offense: partial weight of each slot × skill dimension  (0–100, sign preserved; QB ingredients-only)')
    ax.title.set_position((0, 1.09)); ax.title.set_y(1.10)
    ax.text(0, -0.09, 'Blue = helps the unit once talent and every other cell are held; red = hurts. Efficiency cells (QB1 YPA 100, RB YPC 80–85, RB1 TD 72) carry the offense; '
            'volume cells (passing yards 2, rushing yards −29 to −58, receptions −10 to −34) are ≈0 or negative. Source: results/offense_factor_weights.csv.',
            transform=ax.transAxes, fontsize=7.2, color=MUTED, va='top', wrap=True)
    save(fig, 'fig2_weightmap_offense.png')

def fig3_defense_map():
    rows = ['DL1', 'DL2', 'DL3', 'DL4', 'LB1', 'LB2', 'LB3', 'LB4', 'DB1', 'DB2', 'DB3', 'DB4', 'DB5']
    cols = ['Tkl', 'TFL', 'Sack', 'INT', 'FF', 'PD', 'QBH']
    M = np.array([
        [-8.6, 24.4, -19.1, -22.4, -10.8, -3.2, -30.3], [1.3, 52.7, 22.9, 37.6, -53.8, -27.1, -18.1],
        [-36.5, 40.6, 53.7, 18.0, -27.9, -15.4, -23.4], [-10.5, 19.5, 45.8, -21.7, -20.1, 12.3, -21.1],
        [-0.2, 17.9, 18.8, 76.7, -49.6, -38.3, -19.4], [4.9, 18.5, 53.9, 53.5, -58.4, -54.1, 1.5],
        [-57.7, 7.5, 29.8, 22.7, -14.9, 18.3, -37.9], [-51.3, 26.0, -10.3, 4.2, -22.7, -7.3, 9.1],
        [-44.4, 43.3, -25.1, 92.3, -36.4, 10.4, -16.9], [-69.3, 26.3, 14.3, 100.0, -24.1, 7.0, -5.0],
        [-78.2, 23.3, 6.3, 64.6, -1.6, -21.8, -25.2], [-71.1, 4.7, -2.4, 86.7, 4.0, -33.1, -11.2],
        [-70.6, 25.6, -9.3, 67.9, -12.4, -7.6, -30.4]])
    fig, ax = plt.subplots(figsize=(W * 0.8, 4.8))
    heatmap(ax, M, rows, cols)
    title(ax, 'Defense: partial weight of each slot × skill dimension  (0–100, sign preserved)')
    ax.title.set_y(1.08)
    ax.text(0, -0.07, 'Interceptions are heavy and roughly equal at every DB slot (65–100); tackle volume is the most negative signal in either study (−69 to −78 across the secondary). '
            'Pass rush peaks in the depth slots (DL3/DL4 sack 54/46), not DL1. Source: defense_mix_study.md §B.',
            transform=ax.transAxes, fontsize=7.2, color=MUTED, va='top', wrap=True)
    save(fig, 'fig3_weightmap_defense.png')

# ======================================================================================
# Fig 4 — Positional leverage (permutation ΔR²), offense & defense
# ======================================================================================
def fig4_leverage():
    o = json.load(open(RES/'diag.json'))['leverage']; d = json.load(open(RES/'def_diag.json'))['leverage']
    fig, axes = plt.subplots(1, 2, figsize=(W, 3.4), gridspec_kw={'width_ratios': [1, 1.15]})
    for ax, lev, unit, c in zip(axes, [o, d], ['Offense', 'Defense'], [OFF, DEF]):
        order = sorted(lev, key=lambda k: -lev[k][0]); y = np.arange(len(order))[::-1]
        vals = np.array([lev[k][0] for k in order]); err = np.array([lev[k][1] for k in order])
        cols = [c if (unit == 'Defense' or k == 'qb1') else OFF_LT for k in order]
        ax.barh(y, vals, height=0.6, color=cols, edgecolor=SURF, linewidth=1.5)
        ax.errorbar(vals, y, xerr=err, fmt='none', ecolor=INK2, elinewidth=0.8, capsize=0)
        ax.axvline(0, color=AXIS, lw=0.6)
        ax.set_yticks(y); ax.set_yticklabels([k.upper() for k in order]); ax.tick_params(axis='y', length=0)
        clean(ax, left=False, grid='x')
        title(ax, unit)
    axes[0].text(o['qb1'][0] + o['qb1'][1] + 0.001, len(o) - 1, '3× the next slot', va='center', fontsize=8, color=INK2)
    axes[0].text(o['wr1'][1] + 0.001, list(sorted(o, key=lambda k: -o[k][0]))[::-1].index('wr1'), 'WR1 ≈ 0', va='center', fontsize=8, color=INK2)
    axes[0].set_xlim(0, 0.05)
    axes[1].text(0.98, 0.03, 'top/2nd ratio 1.75× (offense 3×)\ndepth slots DB4, DL3 outrank DB1, DL1\nflat, no QB analog',
                 transform=axes[1].transAxes, fontsize=7.6, color=INK2, ha='right', va='bottom', linespacing=1.25)
    axes[1].set_xlim(-0.011, 0.027)
    fig.text(0.5, -0.02, 'out-of-sample ΔR² when the slot\'s features are shuffled (bars ± SE)', ha='center', fontsize=8.5, color=INK2)
    fig.subplots_adjust(wspace=0.4)
    save(fig, 'fig4_leverage.png')

# ======================================================================================
# Fig 5 — LOSO robustness
# ======================================================================================
def fig5_loso():
    L = pd.read_csv(RES/'loso_robustness.csv')
    fig, ax = plt.subplots(figsize=(W, 2.9))
    ax.bar(L.season, L.dR2, width=0.7, color=OFF, edgecolor=SURF, linewidth=1)
    m = L.dR2.mean(); ax.axhline(m, color=INK2, lw=0.8)
    ax.text(2025.7, m + 0.008, f'mean +{m:.2f}', va='bottom', fontsize=8, color=INK2)
    for s, lab in [(2003, '+0.12\n(n=186)'), (2015, '+0.44'), (2020, '+0.21\nCOVID')]:
        r = L[L.season == s].iloc[0]; ax.text(s, r.dR2 + 0.012, lab, ha='center', va='bottom', fontsize=7.4, color=INK2, linespacing=1.1)
    ax.set_xticks(range(2003, 2026, 2)); ax.set_xlim(2002.3, 2027.3); ax.set_ylim(0, 0.5)
    ax.set_ylabel('held-out ΔR²  (mix − controls)')
    clean(ax, left=False)
    title(ax, 'Composition lift is present in every one of 23 held-out seasons',
          'rotating leave-one-season-out; each bar refit on the other 22 seasons. Spearman of refit vs full weight map ≥ 0.993 every time; QB1 YPA the heaviest cell in all 23.')
    save(fig, 'fig5_loso.png')

# ======================================================================================
# Fig 6 — Receiving corps: deep-threat dose-response & possession anti-pattern
# ======================================================================================
def fig6_wrmix():
    x = [0, 1, 2, 3]; xl = ['0', '1', '2', '3+']
    pocket = [(-20.8, -28, -14), (6.4, 4, 9), (22.1, 17, 28), (38.5, 28, 50)]
    dual = [(-17.7, -27, -1), (-9.2, -22, 7), (4.8, -4, 13), (19.6, 6, 31)]
    poss = [(19.5, 9, 28), (8.8, 6, 12), (-12.5, -18, -7), (-4.3, -22, 22)]
    fig, axes = plt.subplots(1, 2, figsize=(W, 3.2))
    ax = axes[0]
    for ser, c, lab, dx in [(pocket, OFF, 'pocket QB1', -0.06), (dual, DEF, 'dual-threat QB1', 0.06)]:
        m = [s[0] for s in ser]; lo = [s[0] - s[1] for s in ser]; hi = [s[2] - s[0] for s in ser]
        xs = np.array(x) + dx
        ax.errorbar(xs, m, yerr=[lo, hi], fmt='none', ecolor=c, elinewidth=1.2, capsize=0, alpha=0.9)
        ax.plot(xs, m, color=c, lw=2, solid_capstyle='round', label=lab)
        ax.plot(xs, m, 'o', ms=7, mfc=c, mec=SURF, mew=1.5)
    ax.text(3.2, 38.5, '+38.5', va='center', fontsize=8, color=INK2); ax.text(3.22, 19.6, '+19.6', va='center', fontsize=8, color=INK2)
    ax.axhline(0, color=AXIS, lw=0.6); ax.set_xticks(x); ax.set_xticklabels(xl); ax.set_xlim(-0.4, 3.6)
    ax.set_xlabel('deep threats among the top-4 receivers'); ax.set_ylabel('unit residual beyond talent & program (elo)')
    ax.legend(loc='upper left', handlelength=1.4); clean(ax, left=False)
    title(ax, 'More field-stretchers keep helping')
    ax = axes[1]
    m = [s[0] for s in poss]; lo = [s[0] - s[1] for s in poss]; hi = [s[2] - s[0] for s in poss]
    ax.errorbar(x, m, yerr=[lo, hi], fmt='none', ecolor=OFF, elinewidth=1.2, capsize=0)
    ax.plot(x, m, color=OFF, lw=2, solid_capstyle='round'); ax.plot(x, m, 'o', ms=7, mfc=OFF, mec=SURF, mew=1.5)
    ax.axhline(0, color=AXIS, lw=0.6); ax.set_xticks(x); ax.set_xticklabels(xl); ax.set_xlim(-0.4, 3.6)
    ax.set_xlabel('possession receivers among the top-4  (given ≥1 deep threat)')
    ax.annotate('2+ possession = anti-pattern', xy=(2, -12.5), xytext=(1.05, -28), fontsize=8, color=INK2,
                arrowprops=dict(arrowstyle='-', color=INK2, lw=0.7))
    ax.text(3, 24, 'n=164\n(thin)', ha='center', fontsize=7.2, color=MUTED, linespacing=1.1)
    clean(ax, left=False); title(ax, 'A second possession receiver hurts')
    for a in axes: a.set_ylim(-45, 55)
    fig.text(0, -0.03, 'Means with 95% season-block bootstrap CIs; D1 2003–25 (n = 1,676 / 1,747 / 1,116 / 588 by deep-threat count). Both effects survive OC-scheme control with 10–20% shrinkage.',
             fontsize=7.2, color=MUTED, va='top')
    fig.subplots_adjust(wspace=0.3)
    save(fig, 'fig6_wr_mix.png')

# ======================================================================================
# Fig 7 — Asymmetry map: weak penalty vs elite bonus
# ======================================================================================
def fig7_asymmetry():
    off = [('QB1 YPA', -13.1, 14.2), ('QB1 INT', -8.3, 9.6), ('QB1 Pct', -6.4, 7.8), ('QB1 TD', -6.5, 10.5),
           ('RB1 TD', -8.1, 12.6), ('RB1 YPC', -4.0, 8.5), ('RB2 YPC', -2.1, 7.7), ('WR1 YPC', -3.8, 5.8)]
    dfn = [('DB1 INT', 0.4, 10.3), ('DL2 TFL', 0.3, 9.7), ('DB2 INT', -0.9, 9.3), ('DL3 Sack', 2.2, 11.6),
           ('DL1 Sack', 3.0, 9.4), ('DB1 PD', 2.9, 4.0)]
    rows = off + [None] + dfn
    fig, ax = plt.subplots(figsize=(W, 4.6))
    y = len(rows) - 1
    ys = {}
    for r in rows:
        if r is None: y -= 1; continue
        name, weak, elite = r; ys[name] = y
        ax.barh(y + 0.17, elite, height=0.32, color=OFF, edgecolor=SURF, linewidth=1.2)
        ax.barh(y - 0.17, weak, height=0.32, color=NEG, edgecolor=SURF, linewidth=1.2)
        ratio = abs(weak) / abs(elite)
        ax.text(16.2, y, f'{ratio:.2f}', va='center', ha='left', fontsize=8, color=INK, fontweight='medium' if ratio > 0.8 or ratio < 0.12 else 'normal')
        y -= 1
    ax.axvline(0, color=INK2, lw=0.8)
    ax.set_yticks(list(ys.values())); ax.set_yticklabels(list(ys.keys()))
    ax.tick_params(axis='y', length=0); ax.set_xlim(-15, 19); ax.set_ylim(-0.8, len(rows) + 0.3)
    ax.set_xlabel('talent-controlled effect on unit percentile (points)')
    ax.text(16.2, len(rows) - 0.35, '|weak| / |elite|', fontsize=8, color=INK2, ha='left', va='center', fontweight='medium')
    ax.text(-14.6, len(rows) - 0.35, 'OFFENSE', fontsize=8, color=INK2, fontweight='medium', va='center')
    ax.text(-14.6, ys['DB1 INT'] + 1.0, 'DEFENSE', fontsize=8, color=INK2, fontweight='medium', va='center')
    ax.legend(handles=[Patch(color=OFF, label='elite bonus (top quintile)'), Patch(color=NEG, label='weak penalty (bottom quintile)')],
              loc='lower left', bbox_to_anchor=(0, -0.02), ncol=1)
    clean(ax, left=False, grid='x')
    title(ax, 'Where weakness sinks you vs where only upside pays',
          'the quarterback is near-symmetric (ratio ≈ 0.9); skill slots are upside-tilted (≈ 0.5); on defense a weak player is almost free (mean 0.27)')
    save(fig, 'fig7_asymmetry.png')

# ======================================================================================
# Fig 8 — Depth curves (small multiples)
# ======================================================================================
def fig8_depth():
    panels = [
        ('RB per-carry (YPC)', [5.7, 4.1, 0.4, 2.5, 3.4, 1.4], OFF, 3, None),
        ('RB finishing (TD)', [6.1, 5.9, 5.3, 5.3, 4.1, 2.5], OFF, None, None),
        ('WR per-catch (YPC)', [3.2, 3.5, 1.6, 0.4, 3.2, 6.1], OFF, 4, (5, 6)),
        ('WR finishing (TD)', [2.0, 2.6, 1.0, -0.1, 2.9, 2.7], OFF, 4, (5, 6)),
        ('DL pass rush (Sack)', [2.6, 4.8, 3.7, 3.3, -0.3], DEF, 5, None),
        ('DB coverage (INT)', [4.3, 3.6, 4.0, 3.9, 3.5], DEF, None, None),
        ('LB pass rush (Sack)', [2.5, 3.0, -0.6, 0.6, 1.7], DEF, 3, None),
    ]
    fig, axes = plt.subplots(2, 4, figsize=(W, 3.6), sharey=True)
    axes = axes.ravel()
    for ax, (name, v, c, dies, artifact) in zip(axes, panels):
        d = np.arange(1, len(v) + 1)
        if artifact:
            ax.axvspan(artifact[0] - 0.5, artifact[1] + 0.5, color=MID, zorder=0)
            ax.text(np.mean(artifact), 6.4, 'selection\nartifact', ha='center', fontsize=6.6, color=MUTED, linespacing=1.0)
        ax.axhline(0, color=AXIS, lw=0.6)
        ax.plot(d, v, color=c, lw=2, solid_capstyle='round'); ax.plot(d, v, 'o', ms=6, mfc=c, mec=SURF, mew=1.5)
        if dies:
            ax.plot([dies], [v[dies - 1]], 'o', ms=9, mfc='none', mec=INK, mew=1)
            ax.text(dies, v[dies - 1] - 1.6, 'dies', ha='center', fontsize=7, color=INK2)
        ax.set_xticks(d); ax.set_xlim(0.5, 6.5); ax.set_ylim(-2.2, 7.6)
        ax.set_title(name, fontsize=8.5, loc='left', pad=4)
        clean(ax, left=False, grid='y')
    axes[-1].axis('off')
    axes[-1].text(0, 0.9, 'Value of the Nth-deepest\ncontributor being ≥ good,\nholding talent and the\nshallower N−1 fixed\n(OLS partial, pp of\ntop-decile probability).\n\nBlue = offense,\norange = defense.\nCircled = where the\nsignal dies.',
                  transform=axes[-1].transAxes, fontsize=7.2, color=INK2, va='top', linespacing=1.25)
    for ax in axes[4:7]: ax.set_xlabel('depth N')
    axes[0].set_ylabel('marginal value (pp)'); axes[4].set_ylabel('marginal value (pp)')
    fig.suptitle('Where the quality signal dies: top-2 backs, top-3 receivers, but a 4-deep pass rush and a 5-deep secondary', x=0.01, ha='left', fontsize=10, fontweight='medium')
    fig.subplots_adjust(hspace=0.55, wspace=0.15, top=0.86)
    save(fig, 'fig8_depth.png')

# ======================================================================================
# Fig 9 — Defense inverts offense
# ======================================================================================
def fig9_defense_inversion():
    dims = [('INT', 0.15), ('TFL', 0.13), ('PD', 0.10), ('Sack', 0.10), ('QBH', 0.05), ('Tkl', -0.167)]
    fig, axes = plt.subplots(1, 2, figsize=(W, 2.9), gridspec_kw={'width_ratios': [1.2, 1]})
    ax = axes[0]
    y = np.arange(len(dims))[::-1]; v = [d[1] for d in dims]
    ax.barh(y, v, height=0.58, color=[OFF if x > 0 else NEG for x in v], edgecolor=SURF, linewidth=1.5)
    ax.axvline(0, color=INK2, lw=0.8)
    ax.set_yticks(y); ax.set_yticklabels([d[0] for d in dims]); ax.tick_params(axis='y', length=0)
    ax.text(-0.172, y[-1], '−0.17  ', va='center', ha='right', fontsize=8, color=INK)
    ax.text(0.155, y[0], '  +0.15', va='center', ha='left', fontsize=8, color=INK)
    ax.text(-0.01, y[-1] - 0.95, 'empty tackles mark bad defenses', ha='right', va='center', fontsize=7.6, color=INK2)
    ax.set_xlim(-0.24, 0.24); ax.set_ylim(-1.3, len(dims) - 0.4); ax.set_xlabel('correlation of corps dimension with team defense (clean subset)')
    clean(ax, left=False, grid='x'); title(ax, 'Tackle volume is a failure flag')
    ax = axes[1]
    slots = ['DL1', 'DL2', 'DL3', 'DL4']; w = [-19.1, 22.9, 53.7, 45.8]
    ax.bar(slots, w, width=0.6, color=DEF, edgecolor=SURF, linewidth=1.5)
    ax.axhline(0, color=INK2, lw=0.8)
    for i, x in enumerate(w): ax.text(i, x + (2.5 if x > 0 else -2.5), f'{x:.0f}', ha='center', va='bottom' if x > 0 else 'top', fontsize=8, color=INK)
    ax.set_ylim(-32, 68); ax.set_ylabel('sack partial weight (0–100 scale)')
    clean(ax, left=False); title(ax, 'Pass rush lives in the depth slots')
    fig.text(0, -0.04, 'Left: clean-subset correlations, defense_mix_study.md. Right: Fig. 3 sack column by DL usage-slot; the strongest single defensive marginal is "≥4 DL good-sack" (lift 2.12).',
             fontsize=7.2, color=MUTED, va='top')
    fig.subplots_adjust(wspace=0.35)
    save(fig, 'fig9_defense_inversion.png')

# ======================================================================================
# Fig 10 — Portability dumbbells
# ======================================================================================
def fig10_portability():
    rows = [('WR per-catch (YPC)', 0.863, 0.870, 1149, OFF), ('WR touchdowns', 0.847, 0.847, 1149, OFF),
            ('DL sack rate', 0.885, 0.852, 799, DEF), ('DL tackles-for-loss', 0.900, 0.860, 799, DEF),
            ('DB interceptions', 0.873, 0.839, 1374, DEF), ('LB tackles-for-loss', 0.879, 0.811, 657, DEF)]
    fig, ax = plt.subplots(figsize=(W, 2.8))
    y = np.arange(len(rows))[::-1]
    for yi, (name, ret, tr, n, c) in zip(y, rows):
        ax.plot([ret, tr], [yi, yi], color=DEEMPH, lw=2, solid_capstyle='round', zorder=1)
        ax.plot([ret], [yi], 'o', ms=8, mfc=SURF, mec=c, mew=1.8, zorder=2)
        ax.plot([tr], [yi], 'o', ms=8, mfc=c, mec=SURF, mew=1.5, zorder=3)
        ax.text(0.935, yi, f'{tr:.3f} vs {ret:.3f}   n={n:,}', va='center', fontsize=7.8, color=INK2)
    ax.set_yticks(y); ax.set_yticklabels([r[0] for r in rows]); ax.tick_params(axis='y', length=0)
    ax.set_xlim(0.78, 1.0); ax.set_xticks([0.80, 0.85, 0.90])
    ax.set_xlabel('year-over-year persistence of the player\'s level (r)')
    ax.legend(handles=[Line2D([], [], marker='o', ls='', mfc=SURF, mec=INK2, mew=1.8, ms=8, label='stayed at school'),
                       Line2D([], [], marker='o', ls='', mfc=INK2, mec=SURF, ms=8, label='transferred (new school, new QB/scheme)')],
              loc='lower left', bbox_to_anchor=(0, -0.42), ncol=2)
    clean(ax, left=False, grid='x')
    title(ax, 'Production travels: a transfer keeps his level almost exactly as well as a returner', 'blue = offense, orange = defense')
    save(fig, 'fig10_portability.png')

# ======================================================================================
# Fig 11 — Coordinator fixed effects
# ======================================================================================
def fig11_coordinators():
    oc = pd.read_csv(DAT/'coordinator_effects_offense.csv'); dc = pd.read_csv(DAT/'coordinator_effects_defense.csv')
    e3 = json.load(open(RES/'e3_fe.json')); d3 = json.load(open(RES/'def_e3.json'))
    fig, axes = plt.subplots(1, 2, figsize=(W, 2.9), sharey=True)
    bins = np.arange(-130, 131, 10)
    for ax, df, c, lab, p10, p90, spread, n in [(axes[0], oc, OFF, 'Offensive coordinators', e3['oc_p10'], e3['oc_p90'], e3['oc_spread'], e3['n_oc3']),
                                                (axes[1], dc, DEF, 'Defensive coordinators', d3['dc_p10'], d3['dc_p90'], d3['dc_spread'], d3['n_dc3'])]:
        ax.hist(df.eff, bins=bins, color=c, edgecolor=SURF, linewidth=1)
        for q in (p10, p90): ax.axvline(q, color=INK2, lw=0.8)
        ax.text(p10 - 2, 48, f'p10 {p10:+.0f}', ha='right', fontsize=7.6, color=INK2)
        ax.text(p90 + 2, 48, f'p90 {p90:+.0f}', ha='left', fontsize=7.6, color=INK2)
        ax.text(0.97, 0.95, f'p10 to p90\nspread = {spread:.0f} elo', transform=ax.transAxes, ha='right', va='top', fontsize=8.5, color=INK, fontweight='medium', linespacing=1.2)
        ax.set_xlim(-135, 135); ax.set_xlabel('effect on unit strength (elo)')
        clean(ax, left=False); title(ax, f'{lab}  (n={n}, ≥3 seasons)')
    axes[0].set_ylabel('coordinators')
    fig.text(0.5, -0.04, 'per-coordinator fixed effect = elo above roster + program expectation', ha='center', fontsize=8, color=INK2)
    fig.text(0, -0.13, 'Train-only, shrunk (λ=4) per-coordinator fixed effects from the out-of-time model. The spread is 3–4× the largest composition interaction (~18–21 elo); coordinator + head coach claim 25% of residual variance on each side.',
             fontsize=7.2, color=MUTED, va='top')
    fig.subplots_adjust(wspace=0.12)
    save(fig, 'fig11_coordinators.png')

# ======================================================================================
# Fig 12 — Misallocation
# ======================================================================================
def fig12_misallocation():
    rows = [('RB  (30% of backfields)', 0.79, 1.23), ('WR  (43%)', 0.97, 1.08), ('QB  (30%, endogenous)', 0.60, 1.33)]
    fig, ax = plt.subplots(figsize=(W * 0.72, 2.5))
    y = np.arange(len(rows))[::-1]
    for yi, (name, g, b) in zip(y, rows):
        ax.barh(yi + 0.17, g - 1, left=1, height=0.32, color=OFF, edgecolor=SURF, linewidth=1.2)
        ax.barh(yi - 0.17, b - 1, left=1, height=0.32, color=NEG, edgecolor=SURF, linewidth=1.2)
        ax.text(g - 0.015, yi + 0.17, f'{g:.2f}×', va='center', ha='right', fontsize=8, color=INK)
        ax.text(b + 0.015, yi - 0.17, f'{b:.2f}×', va='center', ha='left', fontsize=8, color=INK)
    ax.axvline(1, color=INK2, lw=0.8)
    ax.set_yticks(y); ax.set_yticklabels([r[0] for r in rows]); ax.tick_params(axis='y', length=0)
    ax.set_xlim(0.45, 1.5); ax.set_xlabel('talent-adjusted rate when the most-used player is not the best-rated')
    ax.legend(handles=[Patch(color=OFF, label='reaches top decile'), Patch(color=NEG, label='falls to bottom decile')], loc='upper left', bbox_to_anchor=(0, -0.3), ncol=2)
    clean(ax, left=False, grid='x')
    title(ax, 'Feeding the wrong back is a measurable, costly decision', 'share of team-seasons in parentheses; robust to requiring a ≥15-rating gap')
    save(fig, 'fig12_misallocation.png')

# ======================================================================================
# Fig 13 — Portal backtest forest plot
# ======================================================================================
def fig13_portal():
    player = [('Old archetype recommender (offense)', -0.30, -0.46, -0.15, NEG, True),
              ('New mix score — offense, all', 0.51, 0.35, 0.66, OFF, True),
              ('   QB', 1.16, None, None, OFF, False), ('   RB', 0.59, None, None, OFF, False),
              ('   TE', 0.39, None, None, OFF, False), ('   WR', 0.16, None, None, OFF, False),
              ('New mix score — defense, all', 0.67, 0.48, 0.86, DEF, True),
              ('   DL', 0.76, 0.41, 1.09, DEF, True), ('   DB', 0.77, 0.50, 1.04, DEF, True), ('   LB', 0.45, 0.01, 0.90, DEF, True)]
    team = [('Offense vs no-move counterfactual', -0.001, -0.040, 0.041, OFF), ('Defense vs no-move counterfactual', 0.013, -0.038, 0.065, DEF)]
    fig, axes = plt.subplots(1, 2, figsize=(W, 3.6), gridspec_kw={'width_ratios': [1.5, 1]})
    ax = axes[0]; y = np.arange(len(player))[::-1]
    for yi, (name, est, lo, hi, c, hasci) in zip(y, player):
        if hasci: ax.plot([lo, hi], [yi, yi], color=c, lw=2, solid_capstyle='round')
        ax.plot([est], [yi], 'o' if hasci else 'o', ms=8, mfc=c if hasci else SURF, mec=SURF if hasci else c, mew=1.5)
        ax.text(1.27, yi, f'{est:+.2f}' + ('' if hasci else ' *'), va='center', fontsize=7.8, color=INK2)
    ax.axvline(0, color=INK2, lw=0.8)
    ax.set_yticks(y); ax.set_yticklabels([p[0] for p in player]); ax.tick_params(axis='y', length=0)
    ax.set_xlim(-0.6, 1.5); ax.set_xticks([-0.5, 0, 0.5, 1.0]); ax.set_xlabel('top- minus bottom-quartile transfer:\nRTM-adjusted development (z)')
    clean(ax, left=False, grid='x'); title(ax, 'Player level: ranks who develops, every position', '810 real 2024–25 transfers, fit on ≤2023; destination-clustered 95% CI')
    ax.text(0, -0.36, '* offense position point estimates are reported without CIs in the study.', transform=ax.transAxes, fontsize=7, color=MUTED)
    ax = axes[1]; y = np.arange(len(team))[::-1]
    for yi, (name, est, lo, hi, c) in zip(y, team):
        ax.plot([lo, hi], [yi, yi], color=c, lw=2, solid_capstyle='round'); ax.plot([est], [yi], 'o', ms=8, mfc=c, mec=SURF, mew=1.5)
        ax.text(est, yi + 0.22, f'{est:+.3f}', ha='center', va='bottom', fontsize=7.8, color=INK2)
    ax.axvline(0, color=INK2, lw=0.8)
    ax.set_yticks(y); ax.set_yticklabels(['Offense', 'Defense']); ax.tick_params(axis='y', length=0); ax.set_ylim(-1.2, 2.0)
    ax.set_xlim(-0.09, 0.09); ax.set_xlabel('quartile spread in destination-unit\nsurprise (percentile, 0–1)')
    clean(ax, left=False, grid='x'); title(ax, 'Team level: a clean null', 'surprise = actual − no-move counterfactual (R² 0.81)')
    fig.subplots_adjust(wspace=0.5)
    save(fig, 'fig13_portal_backtest.png')

# ======================================================================================
# Fig 14 — Preseason projection: calibration & accuracy
# ======================================================================================
def fig14_preseason():
    pred = [.09, .20, .29, .38, .46, .55, .63, .72, .82, .94]; act = [.10, .18, .29, .38, .47, .55, .63, .73, .82, .93]
    fig, axes = plt.subplots(1, 2, figsize=(W, 3.0), gridspec_kw={'width_ratios': [1, 1.3]})
    ax = axes[0]
    ax.plot([0, 1], [0, 1], color=AXIS, lw=0.8)
    ax.plot(pred, act, 'o', ms=8, mfc=OFF, mec=SURF, mew=1.5)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.set_xticks([0, .25, .5, .75, 1]); ax.set_yticks([0, .25, .5, .75, 1])
    ax.set_xlabel('mean projected percentile (decile bins)'); ax.set_ylabel('mean realized percentile')
    ax.set_aspect('equal'); clean(ax, left=False, grid='both')
    title(ax, 'Calibrated within 2 points at every decile', 'offense, rotating LOSO')
    ax = axes[1]
    groups = [('naive\n(prior year)', 10.1, DEEMPH), ('roster-only', 9.3, OFF), ('roster\n+ staff', 9.2, OFF), ('prior +\nprogram', 9.9, DEEMPH), ('+ DC/HC\nstaff', 9.7, DEF)]
    x = [0, 1, 2, 3.4, 4.4]
    ax.bar(x, [g[1] for g in groups], width=0.62, color=[g[2] for g in groups], edgecolor=SURF, linewidth=1.5)
    for xi, g in zip(x, groups): ax.text(xi, g[1] + 0.12, f'{g[1]:.1f}', ha='center', fontsize=8, color=INK)
    ax.set_xticks(x); ax.set_xticklabels([g[0] for g in groups], fontsize=7.6, linespacing=1.05)
    ax.set_ylim(0, 11.5); ax.set_ylabel('LOSO mean absolute error (percentile points)')
    ax.text(1, 11.1, 'OFFENSE', ha='center', fontsize=8, color=INK2, fontweight='medium'); ax.text(3.9, 11.1, 'DEFENSE', ha='center', fontsize=8, color=INK2, fontweight='medium')
    clean(ax, left=False); title(ax, 'Returning roster beats persistence by 9%; coaching hires add nothing', '68% band ±12 (offense) / ±13 (defense); the staff layer adds ΔR² only +0.003 / +0.006')
    fig.subplots_adjust(wspace=0.3)
    save(fig, 'fig14_preseason.png')

if __name__ == '__main__':
    for f in [fig1_balance, fig2_offense_map, fig3_defense_map, fig4_leverage, fig5_loso, fig6_wrmix, fig7_asymmetry,
              fig8_depth, fig9_defense_inversion, fig10_portability, fig11_coordinators, fig12_misallocation, fig13_portal, fig14_preseason]:
        f()
