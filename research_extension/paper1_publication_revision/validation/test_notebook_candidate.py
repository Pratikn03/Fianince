from pathlib import Path
import json
import nbformat
import pytest

HERE=Path(__file__).resolve().parent.parent

def test_registered_schema_defect_is_recorded_without_modifying_the_file():
    obj=json.loads((HERE/'source/ceiling_suite/p1_empirics/P1F_A1_Colab.ipynb').read_text())
    assert 'outputs' in obj['cells'][0] and obj['cells'][0]['cell_type']=='markdown'
    with pytest.raises(nbformat.ValidationError):nbformat.validate(obj)

def test_review_copy_has_valid_schema_and_all_code_cells_blocked():
    obj=json.loads((HERE/'P1F_A1_Schema_Review_Only.ipynb').read_text())
    nbformat.validate(obj)
    assert obj['metadata']['p1f_revision_review']['registered'] is False
    code=[c for c in obj['cells'] if c['cell_type']=='code']
    assert len(code)==4
    assert all(c['source'].startswith('raise RuntimeError("UNREGISTERED REVIEW COPY:') for c in code)
    assert all(c['outputs']==[] and c['execution_count'] is None for c in code)
