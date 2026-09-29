"""Finite H2 expectation with exact updates and outward numerical enclosures.

No original project inference/economic module is imported. Decimal exp is
correctly rounded to nearest, NOT directed: expand its endpoint results by
one representable neighbor before using them in interval arithmetic.
"""
from dataclasses import dataclass
from decimal import (Decimal as D, Context, ROUND_FLOOR, ROUND_CEILING,
                     ROUND_HALF_EVEN, Underflow, Subnormal, Clamped)
from fractions import Fraction as F
from functools import cache
from itertools import permutations, product

ASKS = (2, 4, 6)
PAIRS = tuple(product((False, True), repeat=2))
ATOMS = tuple((p/2,F(v),F(v+z)) for v in (0,4)
              for z,p in ((-2,F(1,4)),(2,F(1,2)),(6,F(1,4))))


@cache
def contexts(precision):
    if type(precision) is not int or precision < 20:
        raise ValueError('precision must be an integer >= 20')
    result = tuple(Context(prec=precision, rounding=r) for r in
                   (ROUND_FLOOR,ROUND_CEILING,ROUND_HALF_EVEN))
    for c in result:
        for signal in (Underflow,Subnormal,Clamped):
            c.traps[signal] = True
    return result


@dataclass(frozen=True)
class Interval:
    lo: D
    hi: D
    precision: int

    def __post_init__(self):
        contexts(self.precision)
        if not self.lo.is_finite() or not self.hi.is_finite() or self.lo > self.hi:
            raise ValueError('finite ordered endpoints required')

    @classmethod
    def rational(cls, x, precision):
        if type(x) is int:
            x = F(x)
        if not isinstance(x,F):
            raise TypeError('exact rational required')
        down,up,_ = contexts(precision)
        n,d = D(x.numerator),D(x.denominator)
        return cls(down.divide(n,d),up.divide(n,d),precision)

    def coerce(self, x):
        if isinstance(x,Interval):
            if x.precision != self.precision:
                raise ValueError('mixed precision operands')
            return x
        return self.rational(x,self.precision)

    def __add__(self, x):
        x=self.coerce(x); down,up,_=contexts(self.precision)
        return Interval(down.add(self.lo,x.lo),up.add(self.hi,x.hi),self.precision)

    __radd__ = __add__

    def __neg__(self):
        # Decimal unary minus otherwise uses the ambient context.
        return Interval(self.hi.copy_negate(),self.lo.copy_negate(),self.precision)

    def __sub__(self,x):
        return self + (-self.coerce(x))

    def __rsub__(self,x):
        return self.coerce(x) + (-self)

    def __mul__(self,x):
        x=self.coerce(x); down,up,_=contexts(self.precision)
        corners=tuple(product((self.lo,self.hi),(x.lo,x.hi)))
        return Interval(min(down.multiply(a,b) for a,b in corners),
                        max(up.multiply(a,b) for a,b in corners),self.precision)

    __rmul__=__mul__

    def __truediv__(self,x):
        x=self.coerce(x); down,up,_=contexts(self.precision)
        if x.lo <= 0 <= x.hi:
            raise ZeroDivisionError('denominator interval contains zero')
        corners=tuple(product((self.lo,self.hi),(x.lo,x.hi)))
        return Interval(min(down.divide(a,b) for a,b in corners),
                        max(up.divide(a,b) for a,b in corners),self.precision)

    def exp(self):
        _,_,nearest=contexts(self.precision)
        if self.lo == self.hi == 0:
            return Interval(D(1),D(1),self.precision)
        lo=nearest.next_minus(nearest.exp(self.lo))
        hi=nearest.next_plus(nearest.exp(self.hi))
        return Interval(lo,hi,self.precision)

    def mid(self):
        _,_,nearest=contexts(self.precision)
        return nearest.divide(nearest.add(self.lo,self.hi),D(2))


def contains(x, q):
    if isinstance(x,F):
        return x == q
    return F(x.lo) <= q <= F(x.hi)


def sign(x):
    if isinstance(x,F):
        return 'positive' if x>0 else 'negative' if x<0 else 'zero'
    if x.lo>0:
        return 'positive'
    if x.hi<0:
        return 'negative'
    return 'zero' if x.lo==x.hi==0 else 'unresolved'


def states():
    zero=(F(0),)*3
    focal_a=(F(0),F(1),F(0)); focal_s=(F(0),F(0),F(1))
    rows=[dict(id='baseline',family='baseline',offset=F(0),spread=F(0),
               ordering=None,active=(focal_a,zero),shadow=(focal_s,zero))]
    for family in ('shadow_only','active_shadow'):
        for c,d in product((F(-1,100),F(0),F(1,100)),(F(1,1000),F(1,100),F(1,10))):
            for order in permutations((-1,0,1)):
                q=tuple(c+d*x for x in order)
                rows.append(dict(id=f'{family}:{c}:{d}:{order}',family=family,
                                 offset=c,spread=d,ordering=order,
                                 active=(focal_a,q if family=='active_shadow' else zero),
                                 shadow=(focal_s,q)))
    return rows


def rules():
    return [('greedy',None)]+[('softmax',t) for t in (F(1,10),F(1,4),F(1,2),F(1),F(2))]


def settlement(quotes,value,customer):
    best=min(quotes)
    if customer<best:
        return (F(0),)*5
    shares=tuple(F(q==best,quotes.count(best)) for q in quotes)
    return (*(share*(best-value) for share in shares),customer-best,customer-value,F(1))


@cache
def stage(quotes):
    return tuple(sum(p*settlement(quotes,v,c)[j] for p,v,c in ATOMS) for j in range(5))


def update(shadow,actions,rewards,mask,alpha=F(1,2)):
    tables=[list(q) for q in shadow]
    for i,a in enumerate(actions):
        if mask[i]:
            tables[i][a]=(1-alpha)*tables[i][a]+alpha*rewards[i]
    return tuple(tuple(q) for q in tables)


class Engine:
    def __init__(self, name, tau=None, precision=40, epsilon=F(1,10),alpha=F(1,2)):
        if name not in ('greedy','softmax'):
            raise ValueError('unknown rule')
        if name=='softmax':
            if not isinstance(tau,F):
                raise TypeError('rational temperature required')
            if tau<=0:
                raise ValueError('positive temperature required')
        elif tau is not None:
            raise ValueError('temperature not applicable to greedy')
        if any(not isinstance(x,F) for x in (epsilon,alpha)):
            raise TypeError('rational parameters required')
        if not 0<=epsilon<=1 or not 0<=alpha<=1:
            raise ValueError('parameter outside [0,1]')
        contexts(precision)
        self.name,self.tau,self.precision,self.epsilon,self.alpha=name,tau,precision,epsilon,alpha
        # Per-engine caches do not leak engines across different precision runs.
        self._policy=cache(self._policy)
        self.terminal=cache(self.terminal)

    def number(self,q):
        return q if self.name=='greedy' else Interval.rational(q,self.precision)

    def policy(self,table):
        if not isinstance(table,tuple) or len(table)!=3 or any(not isinstance(q,F) for q in table):
            raise TypeError('three rational table entries required')
        return self._policy(table)

    def _policy(self,table):
        eps=self.epsilon
        if self.name=='greedy':
            count=table.count(max(table))
            return tuple(eps/3+((1-eps)/count if q==max(table) else 0) for q in table)
        weights=tuple(self.number((q-max(table))/self.tau).exp() for q in table)
        # Canonical summation keeps the enclosure invariant to action relabeling.
        normalizer=sum(sorted(weights,key=lambda x:(x.lo,x.hi)))
        return tuple(self.number(eps/3)+self.number(1-eps)*w/normalizer for w in weights)

    def terminal(self,tables):
        laws=tuple(self.policy(q) for q in tables)
        values=[self.number(F(0)) for _ in range(6)]
        for a,b in product(range(3),repeat=2):
            weight=laws[0][a]*laws[1][b]
            pay=stage((ASKS[a],ASKS[b]))
            for j in range(5):
                values[j]+=weight*self.number(pay[j])
            if a==0 or b==0:
                values[5]+=weight
        return tuple(values)

    def evaluate(self,active,shadow,profile,mask):
        for pair in (profile,mask):
            if not isinstance(pair,tuple) or len(pair)!=2 or any(type(x) is not bool for x in pair):
                raise TypeError('boolean pairs required')
        if len(active)!=2 or len(shadow)!=2:
            raise ValueError('two dealers required')
        for table in (*active,*shadow):
            self.policy(table)
        initial=tuple(shadow[i] if profile[i] else active[i] for i in range(2))
        first=self.terminal(initial)
        laws=tuple(self.policy(q) for q in initial)
        second=[self.number(F(0)) for _ in range(6)]
        for a,b in product(range(3),repeat=2):
            for p,v,c in ATOMS:
                weight=laws[0][a]*laws[1][b]*self.number(p)
                reward=settlement((ASKS[a],ASKS[b]),v,c)
                tables=update(shadow,(a,b),reward,mask,self.alpha)
                terminal=self.terminal(tables)
                for j in range(6):
                    second[j]+=weight*terminal[j]
        periods=(first[:5],tuple(second[:5]))
        total=tuple(x+y for x,y in zip(*periods))
        if not contains(sum(total[:3])-total[3],F(0)):
            raise ArithmeticError('accounting identity not enclosed')
        exposure=(first[5],second[5])
        if not contains(total[3]-4-sum(exposure)/4,F(0)):
            raise ArithmeticError('welfare allocation identity not enclosed')
        return dict(total=total,periods=periods,minimum_ask2=exposure)
