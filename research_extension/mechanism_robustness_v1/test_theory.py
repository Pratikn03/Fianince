import importlib
from fractions import Fraction as F
from .model import Engine,states,contains


def test_direct_period_profit_formula_and_learning_welfare_formula():
    theory=importlib.import_module('research_extension.mechanism_robustness_v1.theory_check')
    s=states()[0];e=Engine('softmax',F(1,10))
    a=e.evaluate(s['active'],s['shadow'],(False,False),(False,True))
    b=e.evaluate(s['active'],s['shadow'],(True,False),(False,True))
    predicted=theory.formulas(e,s)
    assert contains(predicted['t0_profit']-(b['periods'][0][0]-a['periods'][0][0]),F(0))
    assert contains(predicted['t1_welfare']-(b['periods'][1][3]-a['periods'][1][3]),F(0))
