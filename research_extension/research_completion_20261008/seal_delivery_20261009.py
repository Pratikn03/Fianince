"""Seal the checked review exports and source amendment; keep older seals intact."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import zipfile

W = Path(__file__).resolve().parent
R = W.parents[1]
L = R / 'research_extension/current_manuscript_lean_20261008'
H = R / 'research_extension/gap_closure_20261006/publication_completion'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def load(p):
    return json.loads(p.read_text())

def main():
    source = R / 'paper/Machine_Markets_JF_Submission.tex'
    formal = load(L / 'formal_verification_receipt.json')
    assert formal['status'] == 'NAMED_PROOFS_BUILD_AND_STRICT_AXIOM_AUDIT_PASS'
    assert formal['named_theorems'] == 150
    assert formal['full_manuscript_formalization_complete'] is False
    assert formal['manuscript_source_sha256'][str(source.relative_to(R))] == sha(source)
    assert formal['manuscript_coverage_sha256'] == sha(L / 'MANUSCRIPT_COVERAGE.json')
    for f, digest in formal['formal_source_sha256'].items():
        assert sha(L / f) == digest, f
    empirical = load(H / 'independent_empirical_verification.json')
    assert empirical['source_sha256'] == sha(source) and empirical['generated_fields'] == 458
    prose = load(H / 'submission_completion/source_recovery_prose_verification.json')
    assert prose['main_source_sha256'] == sha(source)
    fields = load(W / 'manuscript_completion_field_verification.json')
    assert fields['main_source_sha256'] == sha(source)
    assert fields['report_source_sha256'] == sha(W / 'Machine_Markets_Proof_Evidence_Update_20261008.tex')
    assert len(fields['numeric_fields']) == 12
    supplement = load(H / 'evidence_supplement_verification.json')
    assert supplement['rows'] == 243 and supplement['cells'] == 1575
    evidence = load(W / 'completion_evidence_verification.json')
    assert evidence['status'] == 'INDEPENDENT_INFERENCE_AND_ALL_MINUTE_SWEEP_CHECKS_PASS'
    assert evidence['inference_sha256'] == sha(W / 'inference_completion.json')
    assert evidence['book_sha256'] == sha(W / 'displayed_book_calibration.json')
    files = set()
    pdfs = []
    for filename, count in [('Machine_Markets_JF_Submission_ProofEvidence_20261009.pdf', 54),
                            ('Machine_Markets_Proof_Evidence_Update_20261009.pdf', 4)]:
        p = R / filename
        info = subprocess.check_output(['pdfinfo', str(p)], text=True)
        pages = int(re.search(r'^Pages:\s+(\d+)', info, re.M)[1])
        assert pages == count
        pdfs.append(dict(path=filename, pages=pages, sha256=sha(p)))
        files.add(p)
    for logname in ['main_pdf_build_20261009.log', 'report_pdf_build_20261009.log']:
        p = W / logname
        text = p.read_text()
        assert 'Output written on' in text
        assert not re.search(r'Overfull|undefined|Rerun', text), logname
        files.add(p)
    fls = R / 'research_extension/gap_closure_20261006/build/Machine_Markets_ProofEvidence_20261009.fls'
    project_inputs = {}
    for line in fls.read_text().splitlines():
        if not line.startswith('INPUT '):
            continue
        p = Path(line[6:])
        if not p.is_absolute():
            p = R / 'paper' / p
        p = p.resolve()
        if p.is_relative_to(R) and p.suffix in ['.tex', '.pdf'] and p.is_file():
            project_inputs[str(p.relative_to(R))] = sha(p)
            files.add(p)
    assert project_inputs[str(source.relative_to(R))] == sha(source)
    files.add(fls)
    receipt = dict(client_date='2026-10-09',
        status='REVIEW_PDFS_AND_SCOPED_PROOF_EVIDENCE_CHECKS_DELIVERED',
        pdfs=pdfs, main_source_sha256=sha(source), compiler_project_inputs=project_inputs,
        native_report_compile='success; existing open source checked with the desktop compiler',
        visual_review=dict(report_pages=[1, 2, 3, 4], main_edited_pages=[6, 36, 38, 43, 48]),
        formal_receipt_sha256=sha(L / 'formal_verification_receipt.json'),
        named_declarations=150, project_constants_scanned=formal['project_constants_scanned'],
        empirical_receipt_sha256=sha(H / 'independent_empirical_verification.json'),
        supplement_receipt_sha256=sha(H / 'evidence_supplement_verification.json'),
        prose_receipt_sha256=sha(H / 'submission_completion/source_recovery_prose_verification.json'),
        independent_evidence_verification=evidence, numeric_field_receipt_sha256=sha(W / 'manuscript_completion_field_verification.json'),
        full_manuscript_formalization_complete=False, independent_specialist_assessment_recorded=False,
        remaining_ai_work='All15 manuscript objects and the gate remain in MANUSCRIPT_COVERAGE.json; physical kernel/account composition and Gaussian testing are priorities.',
        limits=['Sequence-account proof assumes a nonincreasing kernel; physical-cohort construction/composition is unfinished.',
                'Arithmetic and Lean do not authenticate real fills, dynamic impact, measurement noise or account charges.',
                'Causal identification, full source rights and independent specialist review remain unresolved.',
                'Review exports do not constitute a submission-ready or publication-ready certification.'],
        previous_sealed_deliveries_preserved=True, publication_push_or_reviewer_message=False)
    path = W / 'completion_delivery_receipt_20261009.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    files.add(path)
    for p in (L / 'CurrentProofs').glob('*.lean'):
        files.add(p)
    for name in ['CurrentProofs.lean', 'AxiomAudit.lean', 'verify_formalization.py', 'lakefile.toml',
                 'lake-manifest.json', 'lean-toolchain', 'MANUSCRIPT_COVERAGE.md', 'MANUSCRIPT_COVERAGE.json',
                 'named_declarations.json', 'checked_theorem_types.json', 'formal_verification_receipt.json',
                 'formal_receipt_122_previous.json', 'formal_receipt_138_previous.json', 'build.log', 'axiom_audit.log']:
        files.add(L / name)
    for name in ['README.md', 'NOVELTY_ARGUMENT.md', 'Machine_Markets_Proof_Evidence_Update_20261008.tex',
                 'complete_inference.py', 'inference_completion.json', 'calibrate_displayed_book.py',
                 'calibrate_displayed_book_original_run.py', 'displayed_book_calibration.json',
                 'verify_completion_evidence.py', 'verify_completion_native.pl', 'verify_manuscript_fields.pl',
                 'completion_evidence_verification.json', 'manuscript_completion_field_verification.json',
                 'seal_delivery_20261009.py']:
        files.add(W / name)
    for name in ['verify_current_empirical.py', 'independent_empirical_verification.json',
                 'verify_evidence_supplement.py', 'evidence_supplement_verification.json',
                 'submission_completion/verify_source_recovery_prose.py',
                 'submission_completion/source_recovery_prose_verification.json']:
        files.add(H / name)
    for name in ['GAPS.md', 'REVISED_PLAN.md', 'NINE_PLUS_PLAN.md',
                 'AI_WORK_AND_AUTHOR_DEPENDENCIES_20261008.md', 'CURRENT_FORMAL_WORK_20261008.md']:
        files.add(R / name)
    manifest = {str(p.relative_to(R)): sha(p) for p in sorted(files)}
    destination = R / 'Machine_Markets_Proof_Evidence_Update_20261009.zip'
    with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in sorted(files):
            z.write(p, str(p.relative_to(R)))
        z.writestr('AMENDMENT_MANIFEST_20261009.json', json.dumps(manifest, indent=2) + '\n')
    with zipfile.ZipFile(destination) as z:
        assert z.testzip() is None
        assert set(z.namelist()) == set(manifest) | {'AMENDMENT_MANIFEST_20261009.json'}
        for name, digest in manifest.items():
            assert hashlib.sha256(z.read(name)).hexdigest() == digest, name
    package = dict(path=str(destination), sha256=sha(destination), bytes=destination.stat().st_size,
        entries=len(manifest)+1, all_payload_hashes_and_zip_crc_verified=True,
        scope='Source/evidence amendment; existing master/T9 datasets and pinned runtime required for full reproduction.')
    (W / 'amendment_package_receipt_20261009.json').write_text(json.dumps(package, indent=2) + '\n')
    print(json.dumps(package, indent=2))

if __name__ == '__main__':
    main()
