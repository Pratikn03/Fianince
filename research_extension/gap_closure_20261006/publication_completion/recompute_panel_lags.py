"""Full original-panel lag controls from existing verified archives; no fill/lookahead."""
from pathlib import Path
import sys,json,zipfile,hashlib
import numpy as np
import pandas as pd
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT))
from empirical_pipeline.feedback_var import q_long_memory_robust

def run():
    manifest=json.loads((HERE.parent/'cross_venue/original_panel_restoration_manifest.json').read_text())
    out=HERE/'panel_lag_reproduction.json'
    done=json.loads(out.read_text())['rows'] if out.exists() else []
    lookup={(r['symbol'],r['date']):r for r in done}
    for r in manifest['rows']:
        key=(r['symbol'],r['date'])
        if key in lookup:continue
        p=Path(r['path']);assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']
        with zipfile.ZipFile(p) as z:
            with z.open(z.namelist()[0]) as f:raw=pd.read_csv(f,header=None,usecols=[0,4,7,10])
        sec=raw[0].to_numpy(np.int64)//1000
        f=pd.DataFrame(dict(sec=sec,p=raw[4].to_numpy(),flow=(2*raw[10]-raw[7]).to_numpy())).drop_duplicates('sec').sort_values('sec')
        f['bin']=f.sec//10
        bins=f.groupby('bin').agg(p=('p','last'),flow=('flow','sum'),n=('sec','nunique'));bins=bins[bins.n==10].copy()
        bins['segment']=bins.index.to_series().diff().ne(1).cumsum().to_numpy();segments=[]
        for segment,g in bins.groupby('segment'):
            if len(g)-150<500:continue
            logp=np.log(g.p.to_numpy())*1e4;x=logp-pd.Series(logp).ewm(alpha=2/31,adjust=False).mean().to_numpy()
            x=x[150:];flow=g.flow.to_numpy()[150:]
            fits={str(L):q_long_memory_robust(x,flow,L) for L in [1,5,15,30,60,90]}
            segments.append(dict(segment=int(segment),n=len(x)-1,fits=fits))
        lookup[key]=dict(symbol=key[0],date=key[1],archive_sha256=r['sha256'],segments=segments)
        payload=dict(protocol='Existing original768 archives; first duplicate retained, no filling; complete ten-second bins; EMA300 reset per gap/date, burn150, segment>=500 states. L denotes ten-second bars, L=1 equals baseline VAR. Date uncertainty retrospective.',rows=sorted(lookup.values(),key=lambda v:(v['symbol'],v['date'])))
        out.write_text(json.dumps(payload,indent=2)+'\n')
        if len(lookup)%48==0:print('Panel lag reproduction',len(lookup),'/768',flush=True)
    assert len(lookup)==768
    print('Full original panel lag reproduction completed',flush=True)

if __name__=='__main__':run()
