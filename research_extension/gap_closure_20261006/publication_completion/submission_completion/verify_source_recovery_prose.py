"""Bind the new source/declaration and saved-network prose to recovered evidence."""
from pathlib import Path
import json
import hashlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run():
    main = ROOT / 'paper/Machine_Markets_JF_Submission.tex'
    evidence = HERE.parent / 'Machine_Markets_Current_Evidence_Supplement_20261008.tex'
    text, appendix = main.read_text(), evidence.read_text()
    author = json.loads((HERE / 'author_declarations_20261008.json').read_text())
    assert all(a['contribution'] == 'Equal contribution' and a['external_research_funding'] == 'none received'
               and a['conflicts_of_interest'] == 'none declared' for a in author['authors'])
    for wording in ['Both authors contributed equally.', 'No external research funding was received.',
                    'The authors declare no conflicts of interest.']:
        assert wording in text
    january = json.loads((HERE / 'january_original_uploader_authentication.json').read_text())
    assert january['exact_match'] and january['declared_licence'] == 'MIT'
    assert january['csv_sha256'] == '5d3f14a2d252a884e3c9b81a6f3767c7161296ecc8fdd1280c7d46a1cea19847'
    for wording in ['siavashraz', 'BTCUSDT.P', 'MIT']:
        assert wording in text and wording in appendix
    policy = json.loads((HERE / 'recovered_checkpoint_response_verification.json').read_text())
    assert policy['checkpoints'] == 20 and policy['radius_rows'] == 100 and policy['summaries'] == 10
    assert policy['max_absolute_error'] < 1e-12
    for key, literal in [('actor_small_radius_r2_min', '0.6540'), ('actor_small_radius_r2_max', '0.9988')]:
        assert f'{policy[key]:.4f}' == literal and literal in text and literal in appendix
    assert not policy['saved_conclusion_all_small_radius_r2_below_point7_supported']
    assert 'static' in text.lower() and 'not a proof of exponential-memory' in text
    out = dict(status='AUTHOR_SOURCE_AND_RECOVERED_NETWORK_PROSE_BOUND_TO_RECEIPTS',
               main_source_sha256=sha(main), evidence_source_sha256=sha(evidence),
               declaration_sha256=sha(HERE / 'author_declarations_20261008.json'),
               january_receipt_sha256=sha(HERE / 'january_original_uploader_authentication.json'),
               checkpoint_receipt_sha256=sha(HERE / 'recovered_checkpoint_response_verification.json'),
               numeric_network_fields=6,
               limits=['Recorded declarations and scoped provider/network checks; not independent review or full market calibration.'])
    (HERE / 'source_recovery_prose_verification.json').write_text(json.dumps(out, indent=2) + '\n')
    print(out['status'])


if __name__ == '__main__':
    run()
