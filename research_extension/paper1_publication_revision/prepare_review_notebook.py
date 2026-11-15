"""Repair notebook schema in a separately named, execution-blocked review copy."""
from pathlib import Path
import hashlib,json
import nbformat

HERE=Path(__file__).resolve().parent
source=HERE/'source/ceiling_suite/p1_empirics/P1F_A1_Colab.ipynb'
raw=source.read_bytes();notebook=json.loads(raw)
guard='raise RuntimeError("UNREGISTERED REVIEW COPY: live execution is blocked; a documented amendment is required.")\n'
for i,cell in enumerate(notebook['cells']):
    cell['id']=f'p1f-review-{i}'
    if cell['cell_type']=='markdown':
        cell.pop('outputs',None);cell.pop('execution_count',None)
    elif cell['cell_type']=='code':
        code=cell['source']
        if isinstance(code,list):code=''.join(code)
        cell['source']=guard+code
        cell['outputs']=[];cell['execution_count']=None
notebook['cells'].insert(0,{'cell_type':'markdown','id':'p1f-review-status','metadata':{},'source':
    '# P1F A1 — unregistered schema-repair review copy\n\n'
    'The registered notebook is preserved unchanged. This copy removes invalid Markdown-cell fields. '
    'Every code cell is intentionally blocked before execution. It has not run a study or opened a counter. '
    'The separate candidate executor also changes statistical implementation and failed several offline calibration diagnostics. '
    'A documented amendment and further validation are required before any corrected confirmatory run. '
    'This notebook is for reviewing the format repair, not for running the registered study.'})
notebook['metadata']['p1f_revision_review']={'registered':False,'execution':'blocked',
    'source_sha256':hashlib.sha256(raw).hexdigest(),'change':'schema repair and per-cell execution guards only'}
obj=nbformat.from_dict(notebook);nbformat.validate(obj)
out=HERE/'P1F_A1_Schema_Review_Only.ipynb'
out.write_text(json.dumps(notebook,indent=2,ensure_ascii=False)+'\n')
print('Validated the separate schema repair; every code cell is execution-blocked.')
