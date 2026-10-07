from pathlib import Path
import json,hashlib
HERE=Path(__file__).resolve().parent
original=json.loads((HERE/'covariance_results.json').read_text());centered=json.loads((HERE/'centering_sensitivity.json').read_text());assets={}
for asset,r in original['assets'].items():
    cases={}
    for label,source in [('global',r['bandwidth_cases']),('within_segment',centered['assets'][asset])]:
        for bandwidth,result in source.items():cases[label+'_'+bandwidth]=dict(result,centering=label)
    assets[asset]={'cases':cases}
out={'scope':'All fixed HAC/centering cases retained, six starts each; independent full stable/SPD parameterization; asymptotic references only','assets':assets,'inputs':{name:hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in ['covariance_results.json','centering_sensitivity.json']}}
(HERE/'covariance_complete.json').write_text(json.dumps(out,indent=2)+'\n')
assert sum(len(r['cases']) for r in assets.values())==24
print('Combined24 fixed covariance cases')
