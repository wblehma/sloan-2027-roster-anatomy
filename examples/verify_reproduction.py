"""
verify_reproduction.py
======================
Proves the OPEN-DATA PACKAGE is self-sufficient: it recomputes three headline numbers
from the paper using ONLY files in this repository (data/ + results/) -- no proprietary
rating engine, no hidden inputs. This script contains no engine code; it is ordinary
analysis over the packaged binned-level datasets.

Recomputed:
  (1) A factor weight   -> QB1 passing-efficiency (YPA) = 100.0, the heaviest cell of the
                            offensive weight map (paper Table 3), plus ridge R2 = 0.512.
  (2) Misallocation     -> 30% of backfields feed the wrong runner; those offenses reach
                            greatness at 0.79x their talent expectation (paper sec 4.8).
  (3) One LOSO row      -> re-fit the offensive weight map holding out one season and
                            reproduce that season's held-out composition dR2 (paper Table 3b).

Run from the repository root:   python3 examples/verify_reproduction.py
"""
import pandas as pd, numpy as np
from pathlib import Path
from sklearn.linear_model import RidgeCV, Ridge
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parent.parent
DATA, RES = ROOT/"data", ROOT/"results"

QB_INGR=['Yds','YPA','Pct','TD','INT','RushYds','RushYPC']          # ingredients-only (drop Eff composite)
RB=['Yds','YPC','TD','Rec','RecYd','RecYPC']                        # drop YFS composite
WR=['Rec','Yds','YPC','TD']; TE=['Rec','Yds','YPC','TD']
DIMS={'qb':QB_INGR,'rb':RB,'wr':WR,'te':TE}; NS={'qb':2,'rb':3,'wr':4,'te':1}

def build_X(df):
    X=pd.DataFrame(index=df.index); cols=[]
    for bk in ['qb','rb','wr','te']:
        for sl in range(1,NS[bk]+1):
            for d in DIMS[bk]:
                c=f'{bk}{sl}_{d}'; X[c]=df[c].fillna(df[c].mean()); cols.append(c)
    return X, cols

ok=True

# ---------------------------------------------------------------- (1) factor weight
print("="*68)
print("(1) FACTOR WEIGHT  -- QB1 YPA should be the heaviest cell (=100.0)")
df=pd.read_csv(DATA/'offense_team_season_panel.csv')
df['tal_dec']=np.clip(np.ceil(df.talent_pct*10),1,10).astype(int)
X,cols=build_X(df)
ctrl=pd.concat([pd.get_dummies(df.tal_dec,prefix='tal'),
                pd.get_dummies(df.season,prefix='s'),
                pd.get_dummies(df.tier,prefix='t')],axis=1).astype(float)
Xs=StandardScaler().fit_transform(pd.concat([X,ctrl],axis=1).values)
m=RidgeCV(alphas=np.logspace(-2,4,40)).fit(Xs,df.off_pct.values)
coef=dict(zip(list(X.columns)+list(ctrl.columns),m.coef_))
cc={c:coef[c] for c in cols}
mx=max(abs(v) for v in cc.values())
scaled={c:round(100*cc[c]/mx,1) for c in cc}
heaviest=max(scaled,key=lambda k:abs(scaled[k]))
r2=m.score(Xs,df.off_pct.values)
paper=pd.read_csv(RES/'offense_factor_weights.csv')
paper_qb1ypa=float(paper[(paper.slot=='QB')&(paper.n==1)&(paper.dim=='YPA')].weight.iloc[0])
print(f"    recomputed heaviest cell : {heaviest} = {scaled['qb1_YPA']}   ridge R2={r2:.3f}")
print(f"    packaged Table-3 QB1 YPA : {paper_qb1ypa}")
c1 = (heaviest=='qb1_YPA' and scaled['qb1_YPA']==paper_qb1ypa==100.0 and abs(r2-0.512)<0.005)
print(f"    MATCH: {c1}"); ok &= c1

# ---------------------------------------------------------------- (2) misallocation
print("="*68)
print("(2) MISALLOCATION -- 30% of backfields; great tadj = 0.79")
pl=pd.read_csv(DATA/'offense_player_season_levels.csv')
rb=pl[pl.book=='rb'].copy()
tf=pd.read_csv(DATA/'offense_team_season_panel.csv')
tf['tal_dec']=np.clip(np.ceil(tf.talent_pct*10),1,10).astype(int)
texp=tf.groupby('tal_dec')['top_decile'].mean(); tf['texp']=tf.tal_dec.map(texp)
g=rb.groupby(['team','season'])
most_used = g.apply(lambda d: d.loc[d['slot'].idxmin(),'cpid'], include_groups=False)   # slot 1 = most usage
best_rated= g.apply(lambda d: d.loc[d['overall_pctile'].idxmax(),'cpid'], include_groups=False)
mis=pd.DataFrame({'mu':most_used,'br':best_rated})
mis['misalloc']=(mis.mu!=mis.br).astype(int)
mis=mis.reset_index().rename(columns={'level_0':'team','level_1':'season'})
tf=tf.rename(columns={'cteam':'team'})
M=tf.merge(mis,on=['team','season'],how='left')   # all team-seasons; no-backfield -> NaN -> not misallocated
sel=M[M.misalloc==1]
prev=(M.misalloc==1).mean()                        # denominator = all 5,698 team-seasons
tadj=sel.top_decile.mean()/sel.texp.mean()
print(f"    recomputed prevalence    : {prev*100:.0f}%   great tadj = {tadj:.2f}   n={len(sel)}")
c2 = (round(prev*100)==30 and round(tadj,2)==0.79)
print(f"    paper: 30% / 0.79   MATCH: {c2}"); ok &= c2

# ---------------------------------------------------------------- (3) one LOSO row
print("="*68)
HOLD=2015
print(f"(3) LOSO ROW -- hold out {HOLD}, reproduce held-out composition dR2")
df=pd.read_csv(DATA/'offense_team_season_panel.csv')
df['tal_dec']=np.clip(np.ceil(df.talent_pct*10),1,10).astype(int)
X,_=build_X(df)
CTRL=pd.concat([pd.get_dummies(df.tal_dec,prefix='tal'),
                pd.get_dummies(df.tier,prefix='t')],axis=1).astype(float)   # LOSO: no season dummies
ALLX=pd.concat([X,CTRL],axis=1); y=df.off_pct.values; ALPHA=140.0
def r2_on(cols,tr,te):
    A=ALLX[cols]; sc=StandardScaler().fit(A[tr].values)
    mm=Ridge(alpha=ALPHA).fit(sc.transform(A[tr].values),y[tr])
    return mm.score(sc.transform(A[te].values),y[te])
tr=(df.season!=HOLD).values; te=(df.season==HOLD).values
dR2=r2_on(list(ALLX.columns),tr,te)-r2_on(list(CTRL.columns),tr,te)
loso=pd.read_csv(RES/'loso_robustness.csv')
paper_dR2=float(loso[loso.season==HOLD].dR2.iloc[0])
print(f"    recomputed held-out dR2  : {dR2:.3f}")
print(f"    packaged Table-3b dR2    : {paper_dR2:.3f}")
c3 = abs(dR2-paper_dR2)<0.01
print(f"    MATCH: {c3}"); ok &= c3

print("="*68)
print("ALL THREE REPRODUCED FROM PACKAGED FILES ONLY." if ok else "MISMATCH -- see above.")
raise SystemExit(0 if ok else 1)
