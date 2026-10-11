"""Observed public funding/marks; declared exposures and fee/margin sensitivities."""
from pathlib import Path
import csv
import io
import zipfile
import json
import hashlib
from decimal import Decimal as D
from datetime import datetime, timezone
import numpy as np

HERE = Path(__file__).resolve().parent
BOOK = Path('/Volumes/T9/machine_markets_data/research_completion_20261008/minute_displayed_book.npz')
START = int(datetime(2023, 1, 9, tzinfo=timezone.utc).timestamp()*1000)
END = int(datetime(2023, 1, 21, tzinfo=timezone.utc).timestamp()*1000)

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def rows(record):
    p = Path(record['path'])
    assert sha(p) == record['sha256']
    with zipfile.ZipFile(p) as z:
        assert z.testzip() is None
        assert len(z.namelist()) == 1
        return list(csv.DictReader(io.StringIO(z.read(z.namelist()[0]).decode())))

def qtiles(values):
    a = np.asarray(values, dtype=float)
    return dict(n=len(a), p10=float(np.quantile(a, .1)), median=float(np.median(a)),
                p90=float(np.quantile(a, .9)), minimum=float(a.min()), maximum=float(a.max()))

def main():
    acq = json.loads((HERE/'public_account_input_acquisition.json').read_text())
    files = {r['kind']:r for r in acq['files']}
    bars = {}
    coverage = {}
    for kind in ['markPriceKlines', 'indexPriceKlines']:
        records = rows(files[kind])
        times = [int(r['open_time']) for r in records]
        assert len(times) == len(set(times)), kind
        assert all(b-a == 60000 for a,b in zip(times,times[1:])), kind
        assert all(int(r['close_time']) == int(r['open_time'])+59999 for r in records)
        selected = {int(r['open_time']):r for r in records if START <= int(r['open_time']) < END}
        assert len(selected) == 12*1440
        assert all(D(r['low']) <= min(D(r['open']),D(r['close'])) <=
            max(D(r['open']),D(r['close'])) <= D(r['high']) for r in selected.values())
        bars[kind] = selected
        coverage[kind] = dict(month_rows=len(records), selected_rows=len(selected),
            unique_timestamps=True, exact_minute_continuity=True, ohlc_valid=True)
    funding = [r for r in rows(files['fundingRate']) if START <= int(r['calc_time']) < END]
    assert len(funding) == 36
    assert all(int(r['funding_interval_hours']) == 8 for r in funding)
    ftime = [int(r['calc_time']) for r in funding]
    assert len(set(ftime)) == 36
    # Actual settlement timestamps have millisecond jitter; compare UTC8-hour bins.
    fbin = [t//(8*3600000) for t in ftime]
    assert all(b-a == 1 for a,b in zip(fbin,fbin[1:]))
    event_rows = []
    for r in funding:
        t = int(r['calc_time']); minute=t//60000*60000
        mark=bars['markPriceKlines'][minute]; rate=D(r['last_funding_rate'])
        bounds=sorted([rate*D(mark['low']), rate*D(mark['high'])])
        event_rows.append(dict(timestamp_ms=t, rate=str(rate), interval_hours=8,
            minute_open_ms=minute, mark_open=str(D(mark['open'])), mark_low=str(D(mark['low'])),
            mark_high=str(D(mark['high'])), long_cost_per_btc_reference=str(rate*D(mark['open'])),
            long_cost_per_btc_ohlc_range=[str(x) for x in bounds]))
    # One declared BTC position enters a minute after Jan9 midnight settlement.
    enter=START+60000; exit_time=END-1
    held=[r for r in event_rows if enter < r['timestamp_ms'] <= exit_time]
    assert len(held) == 35
    total=sum((D(r['long_cost_per_btc_reference']) for r in held), D(0))
    bounds=[sum((D(r['long_cost_per_btc_ohlc_range'][j]) for r in held),D(0)) for j in [0,1]]
    rates=[D(r['last_funding_rate']) for r in funding]
    # Compare existing last-minute book midpoints to same-minute mark/index close.
    with np.load(BOOK, allow_pickle=False) as book:
        timestamps=book['ms']; assert np.all(book['valid'])
        # These numeric arrays are the source verifier's stored bid/ask prices.
        bid=book['bid_price']; ask=book['ask_price']
        mids=(bid[:,0]+ask[:,0])/2
        join=[]
        for t,mid in zip(timestamps,mids):
            minute=int(t)//60000*60000
            mark=float(bars['markPriceKlines'][minute]['close'])
            index=float(bars['indexPriceKlines'][minute]['close'])
            join.append((10000*(float(mid)-mark)/mark,10000*(mark-index)/index))
    scenarios=[]
    entry_price=D(bars['markPriceKlines'][enter]['open'])
    exit_price=D(bars['markPriceKlines'][END-60000]['close'])
    for side in [1,-1]:
        for fee in [D('.0002'),D('.0004')]:
            entry_fee=fee*entry_price; exit_fee=fee*exit_price
            for mu in [D('.005'),D('.01'),D('.025'),D('.05')]:
                cum=D(0); idx=0; max_need=D(0); max_at=None
                for minute,bar in sorted(bars['markPriceKlines'].items()):
                    if minute<enter:continue
                    # All settlements within the minute are posted before its adverse extreme.
                    # Event marks and intraminute ordering are therefore scenario assumptions.
                    while idx<len(held) and held[idx]['timestamp_ms']<=minute+59999:
                        cum+=D(held[idx]['long_cost_per_btc_reference']);idx+=1
                    price=D(bar['low'] if side==1 else bar['high'])
                    need=mu*price-D(side)*(price-entry_price)+entry_fee+D(side)*cum
                    if need>max_need:max_need,max_at=need,minute
                for leverage in [2,5,10,20]:
                    initial_requirement=entry_price/D(leverage)+entry_fee
                    final_requirement=entry_fee+exit_fee-D(side)*(exit_price-entry_price)+D(side)*total
                    capital=max(D(0),max_need,initial_requirement,final_requirement)
                    scenarios.append(dict(side='long' if side==1 else 'short', position_btc='1',
                        assumed_commission_rate=str(fee), assumed_maintenance_rate=str(mu),
                        assumed_initial_leverage=leverage, required_initial_usdt_reference=str(capital),
                        maintenance_only_usdt_reference=str(max_need), maintenance_binding_minute_ms=max_at,
                        terminal_wallet_change_usdt=str(D(side)*(exit_price-entry_price)-entry_fee-exit_fee-D(side)*total)))
    result=dict(status='PUBLIC_FUNDING_MARKS_AND_DECLARED_ACCOUNT_SENSITIVITY_CALCULATED',
        source_acquisition_sha256=sha(HERE/'public_account_input_acquisition.json'),
        script_sha256=sha(Path(__file__)), source_coverage=coverage,
        funding=dict(events=36, positive=sum(x>0 for x in rates), negative=sum(x<0 for x in rates),
            zero=sum(x==0 for x in rates), interval_hours_observed=[8], rate_summary=qtiles(rates),
            rows=event_rows),
        one_btc_held_reference=dict(entry_ms=enter, exit_ms=exit_time, funding_events=len(held),
            entry_mark_reference=str(entry_price), exit_mark_reference=str(exit_price),
            long_funding_cost_usdt_reference=str(total), short_funding_cost_usdt_reference=str(-total),
            long_funding_cost_ohlc_range_usdt=[str(x) for x in bounds]),
        book_mark_comparison=dict(selected_books=len(join),book_cache_sha256=sha(BOOK),
            midpoint_minus_mark_close_bps=qtiles([r[0] for r in join]),
            mark_close_minus_index_close_bps=qtiles([r[1] for r in join]),
            timing='Last recorded book versus same-minute closing marks; retrospective comparison, not causal or executable price authentication.'),
        scenarios=scenarios, private_account_validated=False, historical_fee_or_margin_tier_authenticated=False,
        contract_boundary='Linear perpetual wallet plus unrealized P&L; no asset-principal cash exchange on entry. The manuscript counterparty principal-fill theorem is a different account contract.',
        limits=['Funding minute OHLC is a range proxy, not the exact account settlement mark.',
                'Fixed1BTC exposure and entry/exit at marks are declared examples, not actual positions/fills.',
                'Fee, leverage and maintenance grids are assumptions; no historical personal tier or liquidation rule is authenticated.',
                'No dynamic structural impact or independent measurement-error variance is identified.'])
    (HERE/'public_funding_calibration.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['source_coverage','one_btc_held_reference','private_account_validated']},indent=2))

if __name__ == '__main__':main()
