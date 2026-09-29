from decimal import Decimal, localcontext
from fractions import Fraction as F
from itertools import product
import importlib
import pytest

MODULE = 'research_extension.mechanism_robustness_v1.model'


@pytest.fixture
def m():
    return importlib.import_module(MODULE)


def test_grid_is_complete_unique_and_non_tied(m):
    states = m.states()
    assert len(states) == 109
    assert len({s['id'] for s in states}) == 109
    assert len(m.rules()) == 6
    for family in ('shadow_only', 'active_shadow'):
        selected = [s for s in states if s['family'] == family]
        assert len(selected) == 54
        assert len({s['shadow'][1] for s in selected}) == 54
        assert all(len(set(s['shadow'][1])) == 3 for s in selected)
        assert all(s['active'][1] == (s['shadow'][1] if family == 'active_shadow'
                                     else (F(0),)*3) for s in selected)


def test_stage_hand_benchmarks_and_no_trade(m):
    for ask, expected in [(2,(-F(1,4),F(5,2),F(9,4),F(7,8))),
                          (4,(F(1,2),F(3,2),F(2),F(1,2))),
                          (6,(F(3,2),F(1,2),F(2),F(1,2)))]:
        p0,p1,cs,w,t = m.stage((ask,ask))
        assert (p0+p1,cs,w,t) == expected
    assert m.settlement((4,6),4,2) == (F(0),)*5
    assert m.settlement((6,6),4,6) == (F(1),F(1),F(0),F(2),F(1))


def test_original_witness_exact_and_frozen_null(m):
    s=m.states()[0]; e=m.Engine('greedy')
    for mask,expected in [((False,True),(F(1023,16000),-F(87,8000))),
                          ((False,False),(F(0),F(0)))]:
        a=e.evaluate(s['active'],s['shadow'],(False,False),mask)
        b=e.evaluate(s['active'],s['shadow'],(True,False),mask)
        assert (b['total'][0]-a['total'][0],b['total'][3]-a['total'][3]) == expected


def test_selected_update_and_mandatory_frozen_refresh(m):
    s=m.states()[0]
    assert m.update(s['shadow'],(0,2),(F(-2),F(1)),(False,True)) == \
        (s['shadow'][0],(F(0),F(0),F(1,2)))
    e=m.Engine('greedy')
    a=e.evaluate(s['active'],s['shadow'],(False,False),(False,False))
    b=e.evaluate(s['active'],s['shadow'],(True,True),(False,False))
    assert a['periods'][1] == b['periods'][1]


@pytest.mark.parametrize('name,tau',[('greedy',None),('softmax',F(1,2))])
def test_placebo_and_accounting(m,name,tau):
    e=m.Engine(name,tau); s=m.states()[-1]; active=s['shadow']
    cells=[e.evaluate(active,s['shadow'],p,(True,True)) for p in m.PAIRS]
    for r in cells:
        residual=sum(r['total'][:3])-r['total'][3]
        assert m.contains(residual,F(0))
        assert m.contains(r['total'][3]-4-sum(r['minimum_ask2'])/4,F(0))
        for x,y in zip(r['total'],cells[0]['total']):
            assert m.contains(x-y,F(0))


def test_smooth_policy_floor_normalization_shift_and_permutation(m):
    e=m.Engine('softmax',F(1,4)); q=(F(-1,100),F(1,10),F(1))
    p=e.policy(q)
    assert m.contains(sum(p),F(1))
    assert all(x.lo >= Decimal(1)/Decimal(30) - Decimal('1e-27') for x in p)
    shifted=e.policy(tuple(x+123 for x in q))
    assert p==shifted
    assert e.policy(q[::-1]) == p[::-1]
    uniform=e.policy((F(0),)*3)
    assert all(m.contains(x,F(1,3)) for x in uniform)
    high=m.Engine('softmax',F(10**8)).policy(q)
    assert all(abs(float(x.mid())-1/3)<1e-8 for x in high)


@pytest.mark.parametrize('tau',[F(0),F(-1),.5,float('nan')])
def test_invalid_temperature_rejected_before_calculation(m,tau):
    with pytest.raises((TypeError,ValueError)):
        m.Engine('softmax',tau)


def test_strict_inputs_and_no_mutation(m):
    e=m.Engine('greedy'); s=m.states()[0]
    before=repr(s)
    e.evaluate(s['active'],s['shadow'],(True,False),(True,True))
    assert repr(s)==before
    with pytest.raises(TypeError):
        e.policy((0.,0.,0.))
    with pytest.raises(TypeError):
        e.evaluate(s['active'],s['shadow'],(1,0),(False,True))


def test_interval_encloses_exact_arithmetic_and_exp(m):
    for a,b in product((F(-7,3),F(-1,7),F(0),F(2,3)),repeat=2):
        x,y=m.Interval.rational(a,40),m.Interval.rational(b,40)
        for result,target in ((x+y,a+b),(x-y,a-b),(x*y,a*b)):
            assert m.contains(result,target)
        if b:
            assert m.contains(x/y,a/b)
    x=m.Interval.rational(F(1),40).exp()
    # Independent rational Taylor enclosure for e, not Decimal exp as oracle.
    term=F(1); lower=F(1)
    for n in range(1,100):
        term/=n; lower+=term
    upper=lower+term/F(99)  # geometric majorant for the tail after n=99
    assert F(x.lo)<lower<upper<F(x.hi)
    with pytest.raises(ZeroDivisionError):
        m.Interval.rational(F(1),40)/m.Interval(Decimal('-1'),Decimal('1'),40)


def test_interval_ignores_ambient_decimal_precision(m):
    x=m.Interval.rational(F(1,7),40)
    with localcontext() as c:
        c.prec=4
        assert m.contains(x+x,F(2,7))
        assert m.contains(-x,-F(1,7))


def test_classification_never_turns_rounding_into_strict_sign(m):
    assert m.sign(F(0))=='zero'
    assert m.sign(m.Interval(Decimal('-1e-30'),Decimal('1e-30'),40))=='unresolved'
    assert m.sign(m.Interval(Decimal('1e-30'),Decimal('2e-30'),40))=='positive'
