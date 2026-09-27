"""Fresh corrective checks and an explicitly scoped integrity receipt."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import platform
from pathlib import Path
import subprocess
import sys
from .statistical_repair import source_hashes, write_locked_json
from .render_statistical_artifacts import render
from .check_evidence import verify_seal

ROOT=Path(__file__).resolve().parents[2]
OUT=Path('research_extension/outputs/statistical_repair_20260926/verified')
STAGES=('grid','sweep_known','sweep_estimated','calibration','diagnostic','funded')
TIMING_KEYS={'time','runtime','runtime_seconds','elapsed_seconds','mean_execution_time_ms'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def without_timing(obj):
    if isinstance(obj,dict):
        return {k:without_timing(v) for k,v in obj.items() if k not in TIMING_KEYS}
    if isinstance(obj,list):
        return [without_timing(v) for v in obj]
    return obj


def compare_numerics(first,second):
    a,b=without_timing(first),without_timing(second)
    assert a==b, 'clean-copy numerical results differ'
    return dict(numerical_equal=True,excluded_timing_keys=sorted(TIMING_KEYS),
        normalized_sha256=hashlib.sha256(json.dumps(a,sort_keys=True,allow_nan=False).encode()).hexdigest())


def validate_ledger(root,ledger,manuscript):
    ids=[]
    for claim in ledger['claims']:
        assert claim['id'] not in ids
        ids.append(claim['id'])
        for key in ('paper','assumptions','statement','code','tests','denominator','allowed','forbidden'):
            assert claim[key], (claim['id'],key)
        assert r'\label{'+claim['paper']+'}' in manuscript, claim['paper']
        for key in ('code','tests'):
            for path in claim[key]:
                assert (root/path).is_file(), path
        for path in claim['results']:
            assert (root/ledger['result_root']/path).is_file(), path
    return dict(claims=len(ids),ids=ids,
        scope='Linked evidence existence and manuscript labels, not machine proof of every assertion')


def validate_results(base):
    data={stage:json.loads((base/stage/'results.json').read_text()) for stage in STAGES}
    expected=source_hashes()
    for stage,result in data.items():
        receipt=result if stage=='grid' else json.loads((base/stage/'manifest.json').read_text())
        assert receipt['status']=='complete',stage
        assert receipt['source_hashes']==receipt['source_hashes_after']==expected,(stage,'source')
        if stage!='grid':
            assert digest(base/stage/'results.json')==receipt['result_sha256'],stage
        if stage in ('grid','sweep_known','sweep_estimated'):
            for i,panel in enumerate(result['panel_records']):
                assert json.loads((base/stage/'panels'/f'{i:06d}.json').read_text())==panel,(stage,i)
    assert len(data['grid']['panel_records'])==600
    for mode in ('known','estimated'):
        sweep=data['sweep_'+mode]
        assert len(sweep['panel_records'])==300 and sweep['covariance_mode']==mode
        assert all(p['diagnostics']['certified'] is False for p in sweep['panel_records'])
    assert data['diagnostic']['total_attempted']==202
    assert data['calibration']['trials_per_mode']==20000
    assert data['funded']['n_replicates']==100
    return data


def verify(root=ROOT):
    base=root/OUT
    data=validate_results(base)
    art=json.loads((base/'artifacts/paper_artifacts.json').read_text())
    regenerated=render(data)
    for k,v in regenerated.items():
        assert art[k]==v,('rendered artifact drift',k)
    manuscript=(root/'paper/Machine_Markets_Final_Integrated_Paper.tex').read_text()
    assert art['section_tex'] in manuscript,'generated section does not match manuscript'
    assert art['funded_tex'] in manuscript,'generated funded section does not match manuscript'
    for path,expected in art['input_sha256'].items():
        assert digest(root/path)==expected,path
    ledger=json.loads((root/'research_extension/evidence_repair/statistical_claims.json').read_text())
    return dict(status='passed',ledger=validate_ledger(root,ledger,manuscript),
        denominators=regenerated['denominators'],numerical_certification=False,
        independent_human_review=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--clean-root',type=Path)
    parser.add_argument('--output-dir',type=Path)
    parser.add_argument('--seal',type=Path)
    args=parser.parse_args()
    aligned=verify()
    if args.seal:
        aligned['seal']=verify_seal(ROOT,args.seal)
    if not args.output_dir:
        print(json.dumps(aligned,indent=2)); return
    if not args.clean_root:
        parser.error('--clean-root required to record verification')
    dest=args.output_dir.resolve()
    dest.relative_to(ROOT)
    dest.mkdir(parents=True,exist_ok=False)
    receipts=[]
    def run(name,command,cwd=ROOT,expected=0):
        process=subprocess.run(command,cwd=cwd,capture_output=True,text=True)
        log=dest/(name+'.txt')
        log.write_text(process.stdout+'\n'+process.stderr)
        receipts.append(dict(name=name,command=command,cwd=str(cwd),exit_code=process.returncode,
            expected_exit=expected,log=str(log.relative_to(ROOT))))
        print(f'{name}: exit {process.returncode} (expected {expected})',flush=True)
        assert process.returncode==expected,(name,'inspect saved log')
        return process.stdout
    command=[sys.executable,'-m','pytest','-q','tests','research_extension/tests','reference_directory/test_mathematical_supplement.py']
    run('project_tests',command)
    run('project_tests_clean',command,args.clean_root)
    run('bare_pytest_collection_limitation',[sys.executable,'-m','pytest','-q'],expected=2)
    run('native_study_tests',[sys.executable,'tools/run_all_tests.py','--log-dir',str(dest/'native')])
    run('algebra',[sys.executable,'reference_directory/run_checks.py'])
    run('previous_corrective_alignment',[sys.executable,'-m','research_extension.evidence_repair.check_evidence'])
    run('historical_strict_release',[sys.executable,'tools/verify_master.py','--strict'],expected=1)
    run('diff_check',['git','diff','--check'])
    main_ref=run('main_ref',['git','rev-parse','main']).strip()
    assert main_ref=='1ec937cc512a12f8a36e887c20ce721bf675d87e'
    copies={}
    cleanbase=args.clean_root/'research_extension/outputs/statistical_repair_reproduction_verified'
    validate_results(cleanbase)
    for stage in STAGES:
        first=json.loads((ROOT/OUT/stage/'results.json').read_text())
        second=json.loads((cleanbase/stage/'results.json').read_text())
        copies[stage]=compare_numerics(first,second)
        copies[stage]['result_sha256']=digest(cleanbase/stage/'results.json')
    pdfs={}
    for stem in ('Machine_Markets_Final_Integrated_Paper','Machine_Markets_Mathematical_Supplement'):
        path=ROOT/'paper'/(stem+'.pdf')
        cleanpdf=args.clean_root/'tmp'/(stem+'.pdf')
        text=run(stem+'_text',['pdftotext','-layout',str(path),'-'])
        cleantext=run(stem+'_clean_text',['pdftotext','-layout',str(cleanpdf),'-'])
        assert text==cleantext,(stem,'PDF text/layout extraction mismatch')
        info=run(stem+'_info',['pdfinfo',str(path)])
        pages=int(next(x.split(':',1)[1] for x in info.splitlines() if x.startswith('Pages:')))
        pdfs[stem]=dict(pages=pages,pdf_sha256=digest(path),tex_sha256=digest(path.with_suffix('.tex')),
            clean_pdf_sha256=digest(cleanpdf),layout_text_identical=True,
            scope='Extracted text/layout identity, not byte or pixel identity')
    receipt=dict(created_utc=datetime.now(timezone.utc).isoformat(),python=platform.python_version(),
        main_commit=main_ref,branch=run('branch',['git','branch','--show-current']).strip(),
        commands=receipts,alignment=aligned,reproduction=copies,documents=pdfs,
        clean_copy=str(args.clean_root),clean_copy_origin='git archive HEAD plus current corrective sources and required earlier artifacts; shallow local Git metadata added for provenance-dependent tests; not a published corrective commit',
        historical_strict_release='FAILS as preserved; old release not silently resealed',
        bare_root_pytest='12 collection errors from study-local imports and archived duplicate modules; native suites run in separate processes',
        human_review='pending; internal AI-assisted code review is not independent human review',
        numerical_conic_certification='withheld; full outward constraint construction unverified')
    write_locked_json(dest/'verification.json',receipt)
    paths=set()
    old=json.loads((ROOT/'research_extension/outputs/evidence_repair_20260926/verification/final/correction_manifest.json').read_text())
    paths.update(ROOT/p for p in old['sha256'])
    for directory in (ROOT/'research_extension/evidence_repair',ROOT/'research_extension/mm_revision',ROOT/'tests',ROOT/OUT):
        paths.update(p for p in directory.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc')
    paths.update(p for p in dest.rglob('*') if p.is_file())
    manifest=dict(created_utc=receipt['created_utc'],
        scope='Listed current source, tests, paper, accepted corrective outputs and receipts; older receipts remain historical, not current scientific closure',
        sha256={str(p.relative_to(ROOT)):digest(p) for p in sorted(paths)})
    write_locked_json(dest/'correction_manifest.json',manifest)
    print(json.dumps(dict(status='recorded',files_sealed=len(paths),documents=pdfs),indent=2))


if __name__=='__main__':
    main()
