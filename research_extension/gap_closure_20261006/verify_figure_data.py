"""Check rendered plot artists against named data fields, then save fresh figures."""
from pathlib import Path
import hashlib,json,shutil,sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
from matplotlib.figure import Figure
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];REV=ROOT/'research_extension/paper_revision_20261006'
sys.path.insert(0,str(REV));import diagnostics
cb=json.loads((REV/'results/coinbase_reanalysis.json').read_text());tr=json.loads((REV/'results/transient_checks.json').read_text())
original_save=Figure.savefig;checked={};backup=HERE/'baseline/figures_before_semantic_check';backup.mkdir(exist_ok=True)
for p in (REV/'figures').glob('*'):
 if not (backup/p.name).exists():shutil.copy2(p,backup/p.name)

def save_checked(fig,path,*args,**kwargs):
    path=Path(path);ax=fig.axes[0]
    if path.stem=='timing_comparison':
        groups=[('x_observed',-.22),('x_forward',0),('return_observed',.22)]
        data_lines=[line for line in ax.lines if line.get_marker()=='o']
        assert len(data_lines)==3 and len(ax.containers)==3
        series=[]
        for (key,offset),line,container in zip(groups,data_lines,ax.containers):
            mean=np.array([cb[a]['variants'][key]['Q']['mean'] for a in ['BTC','ETH','ADA']]);ci=np.array([cb[a]['variants'][key]['Q']['ci95'] for a in ['BTC','ETH','ADA']])
            np.testing.assert_allclose(line.get_xdata(),np.arange(3)+offset);np.testing.assert_allclose(line.get_ydata(),mean)
            segments=container.lines[2][0].get_segments()
            for i,seg in enumerate(segments):np.testing.assert_allclose(seg[:,1],ci[i])
            series.append({'field':f'[BTC,ETH,ADA].variants.{key}.Q','means':mean.tolist(),'ci95':ci.tolist()})
        checked[path.stem]={'scope':'Saved diagnostic means/date intervals, not structural inference','series':series}
    elif path.stem=='transient_loss':
        assert len(ax.lines)==4;series=[]
        for (theta,values),line in zip(tr['paths'].items(),ax.lines):
            np.testing.assert_allclose(line.get_xdata(),np.arange(41));np.testing.assert_allclose(line.get_ydata(),values[:41]);series.append({'field':'paths.'+theta,'values':values[:41]})
        checked[path.stem]={'scope':'Abstract fixed-spectrum operator norms, not market calibration','series':series}
    else:raise ValueError('Unexpected figure')
    return original_save(fig,path,*args,**kwargs)
Figure.savefig=save_checked
diagnostics.figures()
Figure.savefig=original_save
report={'status':'Artists verified against named fields; fresh figures generated for manuscript','figures':checked,'source_sha256':hashlib.sha256((REV/'diagnostics.py').read_bytes()).hexdigest(),'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (REV/'figures').glob('*')},'PNG_byte_matches_prior':{p.name:p.read_bytes()==(backup/p.name).read_bytes() for p in (REV/'figures').glob('*.png')}}
(HERE/'figure_data_receipt.json').write_text(json.dumps(report,indent=2)+'\n');print('Two plot artist checks passed; PNG identity:',report['PNG_byte_matches_prior'])
