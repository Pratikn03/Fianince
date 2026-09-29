import importlib
import pytest


def test_plot_rows_keep_full_denominators_and_order():
    a=importlib.import_module('research_extension.mechanism_robustness_v1.artifacts')
    rows=[dict(rule='greedy',family=f,kind=k,n=54,strict_conflict=18)
          for f in ('shadow_only','active_shadow') for k in ('learning','interaction')]
    result=a.chart_rows({'rows':rows})
    assert len(result)==4
    assert all(r['denominator']==54 for r in result)
    assert result[0]['count']==18


def test_artifact_input_requires_completed_verification(tmp_path):
    a=importlib.import_module('research_extension.mechanism_robustness_v1.artifacts')
    with pytest.raises(RuntimeError):
        a.require_verification({'passed':False})
    with pytest.raises(RuntimeError):
        a.require_verification({'passed':True,'clean_copy_reproduction':False})
