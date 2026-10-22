"""Verify the new A1 result artifact; inherited chapter numbers use the paper verifier.

No computed numeric table is added to the thesis by A1. This check verifies
recomputation and prevents its parametric diagnostic being reported as a full
matching bound. It does not claim exhaustive coverage of inherited thesis prose.
"""

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
subprocess.run([sys.executable, str(ROOT / 'checks/check_dich_lower.py'), '--check'], check=True)
result = json.loads((ROOT / 'checks/R_dich_lower.json').read_text())
source = (ROOT / 'ch4_paper3.tex').read_text()
status = (ROOT / 'appA_status.tex').read_text()
assert result['diagnostics_pass'] is True
assert result['matching_energy_lower_bound_established'] is False
assert 'Part (iv) remains a \\Target{}' in source
assert result['uniform_statement_refuted'] is True
assert 'target; uniform version refuted' in status
print('Thesis A1 provenance/status check: PASS (limited scope; matching bound OPEN)')
