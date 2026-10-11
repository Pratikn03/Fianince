"""Independent decimal settlement arithmetic and backward wallet requirements."""
from pathlib import Path
from decimal import Decimal as D
import csv,io,zipfile,json,hashlib

H=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    acq=json.loads((H/'public_account_input_acquisition.json').read_text())
    results=json.loads((H/'public_funding_calibration.json').read_text())
    files={r['kind']:r for r in acq['files']}
    def read(kind):
        r=files[kind];p=Path(r['path']);assert sha(p)==r['sha256']
        with zipfile.ZipFile(p) as z:
            assert z.testzip() is None
            return list(csv.DictReader(io.StringIO(z.read(z.namelist()[0]).decode())))
    marks=read('markPriceKlines');rates=read('fundingRate')
    ref=results['one_btc_held_reference'];enter=ref['entry_ms'];end=ref['exit_ms']
    by_minute={int(r['open_time']):r for r in marks}
    source_rows=[r for r in rates if enter<int(r['calc_time'])<=end]
    expected=[]
    for r in source_rows:
        bar=by_minute[int(r['calc_time'])//60000*60000]
        rate=D(r['last_funding_rate']);expected.append((int(r['calc_time']),rate*D(bar['open']),
            min(rate*D(bar['low']),rate*D(bar['high'])),max(rate*D(bar['low']),rate*D(bar['high']))))
    assert len(expected)==35
    assert sum((r[1] for r in expected),D(0))==D(ref['long_funding_cost_usdt_reference'])
    assert -sum((r[1] for r in expected),D(0))==D(ref['short_funding_cost_usdt_reference'])
    for j in [0,1]:assert sum((r[j+2] for r in expected),D(0))==D(ref['long_funding_cost_ohlc_range_usdt'][j])
    count=0
    for case in results['scenarios']:
        sign=D(1 if case['side']=='long' else -1)
        fee=D(case['assumed_commission_rate']);mu=D(case['assumed_maintenance_rate'])
        entry=D(ref['entry_mark_reference']);exit=D(ref['exit_mark_reference'])
        requirements=[]
        for r in marks:
            t=int(r['open_time'])
            if not enter<=t<=end:continue
            price=D(r['low'] if sign>0 else r['high'])
            funding=sum((x[1] for x in expected if x[0]<=t+59999),D(0))
            # Solve reported-model equity>=maintenance backwards for opening wallet.
            uncollateralized_equity=sign*(price-entry)-fee*entry-sign*funding
            requirements.append(mu*price-uncollateralized_equity)
        requirement=max(D(0),max(requirements),entry/D(case['assumed_initial_leverage'])+fee*entry,
            fee*(entry+exit)-sign*(exit-entry)+sign*sum((x[1] for x in expected),D(0)))
        assert requirement==D(case['required_initial_usdt_reference'])
        assert max(D(0),max(requirements))==D(case['maintenance_only_usdt_reference'])
        count+=1
    assert count==64
    receipt=dict(status='INDEPENDENT_DECIMAL_FUNDING_AND_64_WALLET_ENVELOPES_PASS',
        calibration_sha256=sha(H/'public_funding_calibration.json'),verifier_sha256=sha(Path(__file__)),
        exact_settlement_cost_rows=35,declared_account_scenarios=count,private_account_validated=False,
        limits='Arithmetic of declared1BTC exposures/fees/maintenance and minute-mark proxy; no personal execution, historical tier or continuous-time liquidation validation.')
    (H/'public_funding_verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'])
if __name__=='__main__':main()
