from fractions import Fraction as F
from decimal import Decimal as D
import importlib
import json
import pytest
from .model import Interval


@pytest.fixture
def r():
    return importlib.import_module('research_extension.mechanism_robustness_v1.run')


def test_create_only_output_and_round_trip(r,tmp_path):
    p=tmp_path/'result.json'
    r.write_json(p,{'f':F(-1,7),'x':Interval(D('-1'),D('2'),40)})
    assert r.decode_number(json.loads(p.read_text())['f'])==F(-1,7)
    assert r.decode_number(json.loads(p.read_text())['x'])==Interval(D('-1'),D('2'),40)
    before=p.read_bytes()
    with pytest.raises(FileExistsError):
        r.write_json(p,{'bad':True})
    assert p.read_bytes()==before


def test_game_finds_known_costly_equilibrium_and_planner(r):
    from .model import Engine,states,PAIRS
    e=Engine('greedy');s=states()[0]
    cells={(p,m):e.evaluate(s['active'],s['shadow'],p,m) for p in PAIRS for m in PAIRS}
    result=r.game(cells,F(1,20))
    assert result['certified_pure_equilibria']==[(True,False)]
    assert result['certified_planner_profiles']==[(False,False)]
    assert result['unresolved_equilibrium_profiles']==[]


def test_summary_retains_null_opposite_and_unresolved(r):
    data=[{'total':(F(1),F(0),F(0),F(-1),F(0))},
          {'total':(F(0),F(0),F(0),F(0),F(0))},
          {'total':(F(-1),F(0),F(0),F(1),F(0))},
          {'total':(Interval(D('-1'),D('1'),40),F(0),F(0),F(-1),F(0))}]
    summary=r.classify_contrasts(data)
    assert summary['n']==4
    assert summary['strict_conflict']==1
    assert summary['opposite_conflict']==1
    assert summary['sign_pairs']=={'positive/negative':1,'zero/zero':1,
                                  'negative/positive':1,'unresolved/negative':1}


def test_lock_detects_protocol_drift(r,tmp_path):
    p=tmp_path/'PROTOCOL.md';p.write_text('protocol')
    lock={'protocol_sha256':r.digest(p)}
    r.check_protocol(tmp_path,lock)
    p.write_text('different')
    with pytest.raises(RuntimeError,match='protocol'):
        r.check_protocol(tmp_path,lock)


def test_seal_verification_fails_closed(r,tmp_path):
    p=tmp_path/'manifest.json';p.write_text(json.dumps({'files_sha256':{}}))
    with pytest.raises(RuntimeError):
        r.check_seal(tmp_path,'0'*64)
    with pytest.raises(RuntimeError):
        r.check_seal(tmp_path,r.digest(p))


def test_interval_overlap_not_float_midpoint_agreement(r):
    assert r.compatible(Interval(D('0'),D('1'),40),Interval(D('.2'),D('.3'),60))
    assert not r.compatible(Interval(D('0'),D('1'),40),Interval(D('2'),D('3'),60))


def test_preflight_failure_has_receipt(r,tmp_path,monkeypatch):
    def failure(*args):
        raise RuntimeError('injected preservation failure')
    monkeypatch.setattr(r,'preservation',failure)
    output=tmp_path/'run'
    with pytest.raises(RuntimeError,match='preservation'):
        r.run(output,40,r.HERE.parents[1])
    receipt=json.loads((output/'failure.json').read_text())
    assert receipt['phase']=='preflight'
    assert receipt['cells_computed']==receipt['cells_persisted']==0


def test_interrupted_second_state_preserves_completed_cells(r,tmp_path,monkeypatch):
    original=r.Engine.evaluate;calls=0
    def failing(self,*args,**kwargs):
        nonlocal calls
        calls+=1
        if calls==18:
            raise RuntimeError('injected state interruption')
        return original(self,*args,**kwargs)
    monkeypatch.setattr(r.Engine,'evaluate',failing)
    output=tmp_path/'run'
    with pytest.raises(RuntimeError,match='interruption'):
        r.run(output,40,r.HERE.parents[1])
    receipt=json.loads((output/'failure.json').read_text())
    assert receipt['cells_computed']==receipt['cells_persisted']==17
    partial=json.loads((output/'partial.json').read_text())
    assert len(partial['completed_states'])==1
    assert len(partial['partial_state']['cells'])==1
