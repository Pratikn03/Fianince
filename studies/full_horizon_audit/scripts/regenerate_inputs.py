#!/usr/bin/env python3
"""Rebuild complete v1 measurements and verify ALL saved summaries and taps."""
from pathlib import Path
import json,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parents[1]

def main():
    archive=np.load(ROOT/'data/legacy_measurements.npz')
    old={name:archive[name] for name in archive.files};archive.close()
    cases=json.loads((ROOT/'data/configurations.json').read_text())
    cfg=json.loads((ROOT/'provenance/legacy_config.json').read_text())
    Hmax=max(cfg['horizons']);N=len(old['case_ids'])
    full=np.empty((N,Hmax));errors={'early_taps':0.,'sums':0.,'terminals':0.,'standard_error':0.}
    true=np.empty((len(cases),Hmax))
    for c in cases:
        eta=np.asarray(c['eta']);q=np.asarray(c['q']);y=eta*q
        for j in range(Hmax):
            true[c['case_id'],j]=y.sum();y=(1-eta)*y
    for i,(case,noise,rep) in enumerate(zip(old['case_ids'],old['noise_ids'],old['repetition_ids'])):
        c=cases[int(case)]
        se=cfg['relative_noise_sigma'][int(noise)]*(1-c['a'])/np.sqrt(cfg['sample_mean_replicates'])
        rng=np.random.default_rng(np.random.SeedSequence([cfg['seed'],int(case),int(noise),int(rep)]))
        k=true[int(case)]+rng.normal(0,se,Hmax);full[i]=k
        errors['early_taps']=max(errors['early_taps'],float(abs(k[:32]-old['first_tap_means'][i]).max()))
        sums=np.array([k[:h].sum() for h in cfg['horizons']])
        terminal=k[np.array(cfg['horizons'])-1]
        errors['sums']=max(errors['sums'],float(abs(sums-old['partial_sums'][i]).max()))
        errors['terminals']=max(errors['terminals'],float(abs(terminal-old['terminal_taps'][i]).max()))
        errors['standard_error']=max(errors['standard_error'],abs(se-float(old['tap_standard_errors'][i])))
    assert all(v<1e-12 for v in errors.values()),errors
    np.savez_compressed(ROOT/'data/full_measurements.npz',taps=full,
        case_ids=old['case_ids'],noise_ids=old['noise_ids'],repetition_ids=old['repetition_ids'],
        tap_standard_errors=old['tap_standard_errors'],true_kernels=true)
    record={'datasets':N,'taps_per_dataset':Hmax,'total_taps':int(full.size),
            'comparison_max_absolute_errors':errors,'all_previous_saved_inputs_matched':True,
            'full_array_sha256':hashlib.sha256(full.tobytes()).hexdigest()}
    (ROOT/'results/input_reconstruction.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record,indent=2))
if __name__=='__main__':main()
