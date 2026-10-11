"""Localized evidence correction after exact equity transformation replay."""
from pathlib import Path
import json,hashlib,re
HERE=Path(__file__).resolve().parent;H=HERE.parent;ROOT=HERE.parents[3]
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run():
 source=ROOT/'paper/Machine_Markets_JF_Submission.tex';s=source.read_text();baseline=HERE/'baseline_source_33fb.tex'
 if not baseline.exists():
  assert sha(source)=='33fb287424918a2774a9124ad7a2242f1cc1c0f88350f224541edf6b053d1a41'
  baseline.write_text(s)
  (HERE/'prior_publication_delivery_receipt.json').write_bytes((H/'publication_delivery_receipt.json').read_bytes())
 old=load(ROOT/'research_extension/paper_revision_20261006/results/equity_reanalysis.json');fullpath=HERE/'equity_source_sensitivity.json';full=load(fullpath);replay=load(HERE/'equity_representation_replay.json')
 assert replay['exact_csv_bytes_match'] and full['source_events']==394337 and full['retained_sessions']==50
 rows=[]
 for k,v in old['per_stock'].items():rows.append(f"Legacy label {k} & {old['stock_counts'][k]:,} & {v['n_sessions']} & {v['Q_mean']:.7f} & {v['S_mean']:.7f} & {v['max_rho']:.7f} \\\\")
 rows.append(r'\midrule')
 for k,v in full['by_block'].items():rows.append(f"Full price block {k} & {v['n_raw']:,} & {v['n_sessions']} & {v['Q']['mean']:.7f} & {v['S']['mean']:.7f} & {v['max_rho']:.7f} \\\\")
 table=r'''\begin{table}[htbp]\centering\small
\caption{Existing equity-source representation sensitivity. Legacy labels reproduce the supplied CSV; full price blocks use an explicit endpoint and four largest finite price gaps in each normalized source day. Company identities, physical currency/volume units and primary-archive byte authentication remain open. Both constructions retain negative fits.}
\label{tab:equity_benchmark}
\begin{tabular}{lrrrrr}\toprule
Construction & Rows & Sessions & Mean $Q$ & Mean $S$ & Maximum $\rho$ \\\midrule
'''+ '\n'.join(rows)+r'''
\bottomrule\end{tabular}\end{table}'''
 at=s.index(r'\label{tab:equity_benchmark}');a=s.rfind(r'\begin{table}',0,at);b=s.index(r'\end{table}',at)+len(r'\end{table}');s=s[:a]+table+s[b:]
 at=s.index(r'\subsection{Supplied Equity Representation}');a=s.index('\n',at)+1;b=s.index(r'\begin{table}',a)
 paragraph=r'''The supplied CSV is now reproduced byte for byte from ten independently retrieved DecPre files by replaying its preserved notebook transformation. Its six-largest-jump/five-interval rule omits an endpoint, retaining 272,941 of 394,337 source events and dropping 121,396 (30.7848 percent). Legacy labels 2--5 also map to different inferred price blocks across days; they are not authenticated company identities.

We retain the legacy 49-session calculation as a representation audit and reconstruct full coverage using four largest finite price gaps plus an explicit endpoint. All 394,337 events and 50 eligible date/block sessions are retained; EMA 100, burn 500 and top-quote OFI use the declared per-column decimal conversion. The smallest selected gap is at least 12.3055 times the largest omitted gap in this sample, but this does not authenticate identities. The full price-block 1 mean is $Q=0.0001936$, with exploratory ten-day reference $[-0.0000045,0.0003918]$ spanning zero. Every block and interval is retained in the Internet Appendix evidence ledger. The mirror does not authenticate the Fairdata archive's full checksum or original currency/normalization denominators, and these diagnostics do not identify a crypto-versus-equity regulatory effect.

'''
 s=s[:a]+paragraph+s[b:]
 s=s.replace('Its transformed stock/day representation still requires original-archive reconstruction.','Its supplied transformation has been exactly replayed against independently retrieved normalized files; primary-archive hash, stock identities and physical units remain unauthenticated.')
 s=s.replace('50 stock/day labels; 49 fitted sessions','50 legacy labels; 49 legacy fits')
 s=s.replace('Upstream mapping unresolved','Mirror replay matched; mapping open')
 source.write_text(s)
 ledger=load(H/'generated_field_ledger.json');ledger['fields']=[r for r in ledger['fields'] if not (r['table']=='tab:equity_benchmark' and str(r['row']).startswith('full_'))]
 for k,v in full['by_block'].items():
  for key,value,pointer,rendered in [('n_raw',v['n_raw'],['by_block',k,'n_raw'],f"{v['n_raw']:,}"),('n_sessions',v['n_sessions'],['by_block',k,'n_sessions'],str(v['n_sessions'])),('Q_mean',v['Q']['mean'],['by_block',k,'Q','mean'],f"{v['Q']['mean']:.7f}"),('S_mean',v['S']['mean'],['by_block',k,'S','mean'],f"{v['S']['mean']:.7f}"),('max_rho',v['max_rho'],['by_block',k,'max_rho'],f"{v['max_rho']:.7f}")]:
   ledger['fields'].append(dict(table='tab:equity_benchmark',row='full_'+k,key=key,value=value,rendered=rendered,source=str(fullpath.relative_to(ROOT)),pointer=pointer,source_sha256=sha(fullpath)))
 ledger.setdefault('initial_generator_source_sha256',ledger.get('current_source_sha256'))
 ledger['current_source_sha256']=sha(source)
 ledger['equity_source_repair']=dict(main_source_sha256=sha(source),exact_mirror_replay=True,legacy_labels_not_company_ids=True,full_coverage_sensitivity=True)
 (H/'generated_field_ledger.json').write_text(json.dumps(ledger,indent=2)+'\n')
 (HERE/'equity_manuscript_update_receipt.json').write_text(json.dumps(dict(status='LOCALIZED_EQUITY_SOURCE_REPAIR_CURRENT_SOURCE_CHECKS_REQUIRED',prior_source_sha256=sha(baseline),current_source_sha256=sha(source),main_table_universe=14,equity_rows=10,generated_fields=len(ledger['fields']),replay_receipt_sha256=sha(HERE/'equity_representation_replay.json'),full_coverage_receipt_sha256=sha(fullpath)),indent=2)+'\n');print('Localized equity source repair;',len(ledger['fields']),'generated fields')
if __name__=='__main__':run()
