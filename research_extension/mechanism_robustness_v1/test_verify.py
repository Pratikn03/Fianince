from fractions import Fraction as F
import importlib
import pytest
import subprocess
import sys
from .model import Engine,states,PAIRS,contains


@pytest.fixture
def v():
    return importlib.import_module('research_extension.mechanism_robustness_v1.verify')


def test_literal_enumeration_matches_simple_exact_uniform_benchmark(v):
    s=states()[0]
    got=v.literal_history(s,(False,False),(False,False),F(1),epsilon=F(1))
    # For two independent uniform asks, min ask 2 has probability 5/9.
    assert abs(got[3]-v.D(77)/v.D(18))<v.D('1e-25')


def test_epsilon_one_and_zero_learning_boundaries():
    s=states()[-1]
    e=Engine('softmax',F(1,2),epsilon=F(1))
    outcomes=[e.evaluate(s['active'],s['shadow'],p,(True,True)) for p in PAIRS]
    assert all(contains(r['total'][3],F(77,18)) for r in outcomes)
    e=Engine('softmax',F(1,2),alpha=F(0))
    a=e.evaluate(s['active'],s['shadow'],(True,False),(False,False))
    b=e.evaluate(s['active'],s['shadow'],(True,False),(True,True))
    assert all(contains(x-y,F(0)) for x,y in zip(a['total'],b['total']))


def test_numeric_walk_detects_disjoint_and_missing_values(v):
    good={'a':[{'rational':'1/2'},{'lo':'0','hi':'1','precision':40}]}
    other={'a':[{'rational':'1/2'},{'lo':'.2','hi':'.4','precision':60}]}
    assert v.compare_numeric(good,other)==2
    with pytest.raises(AssertionError):
        v.compare_numeric(good,{'a':[{'rational':'1/2'}]})
    other['a'][1]['lo']='2';other['a'][1]['hi']='3'
    with pytest.raises(AssertionError):
        v.compare_numeric(good,other)


def test_checks_survive_optimized_python():
    code="from research_extension.mechanism_robustness_v1.verify import compare_numeric; compare_numeric({'rational':'1'},{'rational':'2'})"
    proc=subprocess.run([sys.executable,'-O','-c',code],capture_output=True,text=True)
    assert proc.returncode!=0


def test_wrong_or_mixed_precision_is_rejected(v):
    with pytest.raises(RuntimeError):
        v.validate_precision({'precision':40,'x':{'lo':'0','hi':'1','precision':40}},60)
    with pytest.raises(RuntimeError):
        v.validate_precision({'precision':60,'x':{'lo':'0','hi':'1','precision':40}},60)
