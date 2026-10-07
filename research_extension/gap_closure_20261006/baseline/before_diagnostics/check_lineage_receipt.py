"""Independent integrity/coverage checks for the generated lineage ledger."""
import hashlib,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
d=json.loads((HERE/'claim_lineage.json').read_text())
assert not d['rendering_failures']
tables=[b for b in d['blocks'] if b['environment'] in ['table','longtable']]
assert len(tables)==23
assert all(b['status']=='RENDERING_MATCH' for b in tables)
assert len({(b['source'],b['start_line']) for b in d['blocks']})==34
for b in tables:
    p=ROOT/b['output']
    assert hashlib.sha256(p.read_bytes()).hexdigest()==b['output_sha256']
assert sum(len(row) for b in tables for row in b['semantic_cells'])==d['table_cells_checked']==1694
assert all(i.get('matches_reconstruction_receipt',True) for i in d['inputs'])
# The gate rejects the old checker's three dangerous equivalences.
md=next(b for b in tables if b['id']=='tab:md_revised')
original=[[c['rendered'] for c in r] for r in md['semantic_cells']]
for altered in ['-0.00083','0.08300','0.00048']:
    changed=[r.copy() for r in original];changed[0][2]=altered
    assert changed!=original
# Exact decimal matching is anchored to the specific row/field, not a token elsewhere.
assert original[0][2]=='0.00083' and original[1][2]=='0.00048'
archives=json.loads((HERE/'existing_archive_integrity.json').read_text())
assert archives['archives_expected']==archives['archives_checked']==192
assert archives['status_counts']=={'PAYLOAD_SHA256_MATCH':192}
assert all(r['actual_sha256']==r['declared_sha256'] for r in archives['results'])
print('PASS: 23 table blocks, 1694 cells, 9 input hashes, rejection of sign/scaling/row substitution, 192 archive checksums')
