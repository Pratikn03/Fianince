"""Run the exact current local test inventory, without starting data studies."""
from pathlib import Path
import subprocess,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def run():
 paths=['research_extension/paper_revision_20261006/test_revision_evidence.py']
 paths += ['research_extension/gap_closure_20261006/'+name for name in ['economic_contracts/test_economic_contracts.py','risk_contracts/test_risk_contracts.py','model_diagnostics/test_model_diagnostics.py','cross_venue/test_joint_var.py','event_study/test_event_study.py','regime_model/test_switching_regression.py','input_gate/test_input_gate.py','publication_completion/test_resource_frontier.py','publication_completion/test_capital_frontier.py','publication_completion/test_natural_excitation.py']]
 subprocess.run([sys.executable,'-m','pytest','-q','-o','addopts=']+paths,cwd=ROOT,check=True)
if __name__=='__main__':run()
