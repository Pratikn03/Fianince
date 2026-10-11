"""Exact-decimal single-asset linear-perpetual wallet/position reconciliation.

Private exports must be normalized with authenticated currency and event ordering.
Fees and funding are signed cash events; trade notional is never debited as principal.
"""
from decimal import Decimal as D
from pathlib import Path
import json
import argparse

def reconcile(initial_wallet_usdt, events, tolerance='0.00000001', initial_position_btc='0', initial_entry_usdt=None):
    wallet=D(str(initial_wallet_usdt)); position=D(initial_position_btc)
    if position and (initial_entry_usdt is None or D(initial_entry_usdt)<=0):
        raise ValueError('Nonzero opening position requires authenticated opening entry price')
    entry=D(initial_entry_usdt) if position else None
    fees=D(0); funding=D(0); realized=D(0); transfers=D(0)
    output=[]; discrepancies=[]; snapshots=0; last_key=None
    for event in events:
        key=(int(event['timestamp_ms']),int(event['sequence']))
        if last_key is not None and key<=last_key:
            raise ValueError('Events must have authenticated strictly increasing timestamp/sequence order')
        last_key=key
        kind=event['kind']; amount=D(0)
        if kind=='fill':
            if event['commission_asset']!='USDT':raise ValueError('Non-USDT fees need authenticated conversion')
            delta=D(event['signed_quantity_btc']); price=D(event['price_usdt']); fee=D(event['commission_usdt'])
            if delta==0 or price<=0:raise ValueError('Invalid fill quantity/price')
            pnl=D(0); new_position=position+delta
            if position==0:
                new_entry=price
            elif position*delta>0:
                new_entry=(abs(position)*entry+abs(delta)*price)/abs(new_position)
            else:
                closed=min(abs(position),abs(delta))
                pnl=closed*(D(1) if position>0 else D(-1))*(price-entry)
                new_entry=None if new_position==0 else (entry if position*new_position>0 else price)
            amount=pnl-fee; wallet+=amount; fees+=fee; realized+=pnl
            position,entry=new_position,new_entry
            if 'reported_realized_pnl_usdt' in event:
                residual=pnl-D(event['reported_realized_pnl_usdt'])
                if abs(residual)>D(tolerance):discrepancies.append(dict(key=key,field='realized_pnl',residual=str(residual)))
        elif kind in ['funding','transfer']:
            amount=D(event['wallet_delta_usdt']);wallet+=amount
            if kind=='funding':funding+=amount
            else:transfers+=amount
        elif kind=='snapshot':
            required=['mark_price_usdt','reported_wallet_usdt','reported_position_btc',
                      'reported_entry_usdt','reported_equity_usdt','reported_maintenance_usdt']
            if any(k not in event or event[k] is None for k in required):
                raise ValueError('Missing required wallet/position/equity/margin snapshot; no zero imputation')
            mark=D(event['mark_price_usdt']);unrealized=position*(mark-entry) if position else D(0)
            computed=dict(wallet_usdt=wallet,position_btc=position,entry_usdt=entry or D(0),equity_usdt=wallet+unrealized)
            for field,value in computed.items():
                residual=value-D(event['reported_'+field])
                if abs(residual)>D(tolerance):discrepancies.append(dict(key=key,field=field,residual=str(residual)))
            maintenance=D(event['reported_maintenance_usdt'])
            snapshots+=1
            event=dict(event,computed_unrealized_usdt=str(unrealized),computed_equity_usdt=str(wallet+unrealized),
                       reported_margin_headroom_usdt=str(wallet+unrealized-maintenance))
        else:raise ValueError('Unsupported cash/position event: '+kind)
        output.append(dict(timestamp_ms=key[0],sequence=key[1],kind=kind,wallet_usdt=str(wallet),
            position_btc=str(position),entry_usdt=None if entry is None else str(entry),wallet_delta_usdt=str(amount),
            **{k:v for k,v in event.items() if k.startswith('computed_') or k.startswith('reported_margin_')}))
    identity=wallet-D(str(initial_wallet_usdt))-(realized-fees+funding+transfers)
    assert identity==0
    return dict(status='RECONCILED' if not discrepancies and snapshots else 'DISCREPANCIES_OR_MISSING_SNAPSHOTS',
        events=len(output),snapshots=snapshots,discrepancies=discrepancies,records=output,
        ending_wallet_usdt=str(wallet),realized_pnl_usdt=str(realized),commission_usdt=str(fees),
        funding_wallet_cashflow_usdt=str(funding),net_transfers_usdt=str(transfers),cash_identity_residual_usdt=str(identity),
        historical_tier_authenticated=False,liquidation_rules_validated=False,
        limits='Signed USDT cash, single-asset linear contract, weighted-average entry convention. Reported maintenance is checked against equity but historical tier/liquidation provenance is separate.')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('normalized_export',type=Path);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();data=json.loads(args.normalized_export.read_text())
    if data.get('data_kind')!='authenticated_account_export':
        raise ValueError('Real-account runs require data_kind=authenticated_account_export; synthetic tests use the function directly')
    if not data.get('source_receipts'):raise ValueError('Missing original export/authentication receipts')
    if data.get('position_mode')!='ONE_WAY' or data.get('settlement_asset')!='USDT':
        raise ValueError('This verifier requires documented one-way USDT settlement; hedge/multi-asset modes need separate accounting')
    if 'initial_position_btc' not in data or 'initial_entry_usdt' not in data:
        raise ValueError('Missing authenticated opening position/entry state')
    result=reconcile(data['initial_wallet_usdt'],data['events'],initial_position_btc=data['initial_position_btc'],initial_entry_usdt=data['initial_entry_usdt'])
    result['source_receipts']=data['source_receipts']
    result['independent_exchange_authentication']=False
    args.output.write_text(json.dumps(result,indent=2)+'\n');print(result['status'])

if __name__=='__main__':main()
