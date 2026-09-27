"""Verification must distinguish numerical identity from volatile timing."""
import importlib
import importlib.util
import pytest


def module():
    name='research_extension.evidence_repair.verify_statistical_repair'
    assert importlib.util.find_spec(name), 'statistical verification missing'
    return importlib.import_module(name)


def test_clean_comparison_ignores_only_declared_timing():
    compare=module().compare_numerics
    a={'score':1.,'rows':[{'time':1.,'runtime_seconds':2.,'runtime':1.,'value':3.}]}
    b={'score':1.,'rows':[{'time':9.,'runtime_seconds':8.,'runtime':8.,'value':3.}]}
    assert compare(a,b)['numerical_equal']
    b['rows'][0]['value']=4.
    with pytest.raises(AssertionError,match='numerical'):
        compare(a,b)


def test_claim_ledger_requires_real_links(tmp_path):
    validate=module().validate_ledger
    ledger={'result_root':'results','claims':[dict(id='a',paper='missing',assumptions=['x'],
        statement='y',code=['absent.py'],tests=['test.py'],results=[],denominator='one',
        allowed='z',forbidden=['w'])]}
    with pytest.raises(AssertionError):
        validate(tmp_path,ledger,'')
