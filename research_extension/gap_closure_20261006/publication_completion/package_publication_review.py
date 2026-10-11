"""Assemble a local review snapshot with exact content hashes, excluding raw data."""
from pathlib import Path
import json,hashlib,subprocess,zipfile,tempfile,shutil
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];BASE=HERE.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run():
 destination=Path('/Volumes/T9/machine_markets_data/publication_review_package_20261008');destination.mkdir(parents=True,exist_ok=True)
 staging=Path(tempfile.mkdtemp(prefix='review_snapshot_',dir=destination));files=set();suffixes={'.py','.json','.tex','.md','.csv','.bib'}
 for dirname in ['research_extension/gap_closure_20261006','research_extension/paper_revision_20261006','empirical_pipeline','simulations']:
  for p in (ROOT/dirname).rglob('*'):
   if not p.is_file() or p.suffix not in suffixes or p.stat().st_size==0:continue
   rel=p.relative_to(ROOT)
   if any(s in rel.parts for s in ['baseline','data','cache','__pycache__','logs','build']):continue
   if 'fi2010' in rel.parts or p.name.startswith('fairdata_'):continue
   if p.name in ['current_pdf_text.txt','publication_package_receipt.json']:continue
   files.add(p)
 for p in ROOT.glob('*.md'):files.add(p)
 for p in ROOT.glob('*.py'):files.add(p)
 for p in (ROOT/'paper').glob('*.tex'):files.add(p)
 for name in ['fig_capital_information_20261008.pdf','fig_verified_panel_20261008.pdf','fig_verified_pseudospectrum_20261008.pdf']:files.add(ROOT/'paper/figures'/name)
 for name in ['Machine_Markets_JF_Submission.pdf','Machine_Markets_External_Review_Freeze.pdf','Machine_Markets_JF_Submission_PublicationRevision_20261008.pdf','Machine_Markets_Central_Result_Review_20261008.pdf','Machine_Markets_Current_Evidence_Supplement_20261008.pdf','Machine_Markets_Economic_Supplement_20261007.pdf','Machine_Markets_Input_Gate_Supplement_20261008.pdf','Machine_Markets_Regime_Supplement_20261007.pdf']:files.add(ROOT/name)
 files.add(BASE/'baseline/original_user_freeze_3739d00e.pdf')
 files.add(ROOT/'research_extension/outputs/high_power_table16_results.json')
 for name in ['research_extension/outputs/real_lob_rl_results.json','research_extension/outputs/real_lob_guard_benchmark.json','research_extension/learned_agents/real_lob_replay_env.py','research_extension/learned_agents/train_real_lob_deep_rl.py','agentic_guard/real_lob_benchmark.py']:files.add(ROOT/name)
 for name in ['publication_complete_checks_87.txt','publication_january_forecast_verification.txt','Machine_Markets_PublicationRevision_20261008_final_pass3.txt','Machine_Markets_Central_Result_Review_20261008_final_pass3.txt','Machine_Markets_Current_Evidence_Supplement_20261008_final_pass3.txt']:files.add(BASE/'logs'/name)
 records=[]
 for p in sorted(files):
  assert p.is_file(),p
  rel=p.relative_to(ROOT);dest=staging/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
  records.append(dict(path=str(rel),bytes=p.stat().st_size,sha256=sha(p)));assert sha(dest)==records[-1]['sha256']
 # Verify the actual extracted snapshot, not only the live checkout.
 r=subprocess.run(['python3.11','research_extension/gap_closure_20261006/publication_completion/run_review_checks.py'],cwd=staging,capture_output=True,text=True)
 (destination/'package_test_log.txt').write_text(r.stdout+r.stderr);assert r.returncode==0,r.stdout+r.stderr
 r2=subprocess.run(['python3.11','research_extension/gap_closure_20261006/publication_completion/verify_evidence_supplement.py'],cwd=staging,capture_output=True,text=True)
 (destination/'package_supplement_log.txt').write_text(r2.stdout+r2.stderr);assert r2.returncode==0,r2.stdout+r2.stderr
 # Verifiers write fresh receipts in staging. Seal the final staged contents.
 for row in records:row['sha256']=sha(staging/row['path']);row['bytes']=(staging/row['path']).stat().st_size
 manifest=dict(status='LOCAL_REVIEW_SNAPSHOT_NO_SCIENTIFIC_CERTIFICATION',files=records,excluded=['Raw and cache data','Temporary signed download tokens and private credentials','Unrelated third-party Fairdata source copies','Historical baseline directories except exact original user PDF'],external_input_manifest='research_extension/gap_closure_20261006/publication_completion/required_input_manifest.json',test_scope='87 checks pass in this staged snapshot;10 supplement tables and named prose verify against included outputs',limits=['Full raw reproduction requires separately authenticated external inputs; equity transformation remains open.','Manifest does not hash itself; package SHA256 is in the external package receipt.'])
 (staging/'REVIEW_CONTENT_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
 archive=destination/'Machine_Markets_Publication_Review_Package_20261008.zip';tmp=archive.with_suffix('.zip.tmp')
 with zipfile.ZipFile(tmp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted(staging.rglob('*')):
   if p.is_file():z.write(p,str(p.relative_to(staging)))
 with zipfile.ZipFile(tmp) as z:
  assert z.testzip() is None
  for row in records:assert hashlib.sha256(z.read(row['path'])).hexdigest()==row['sha256']
 tmp.replace(archive)
 receipt=dict(status='SEALED_LOCAL_REVIEW_PACKAGE_VERIFIED',package_path=str(archive),package_sha256=sha(archive),bytes=archive.stat().st_size,file_count=len(records)+1,staging_path=str(staging),staged_checks_exit_code=r.returncode,staged_supplement_exit_code=r2.returncode,manifest_sha256=sha(staging/'REVIEW_CONTENT_MANIFEST.json'),limits=manifest['limits'])
 (HERE/'publication_package_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':run()
