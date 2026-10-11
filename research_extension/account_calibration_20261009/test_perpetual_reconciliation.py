"""Hand-computed partial-close/reversal/currency/missing-record checks; synthetic."""
import unittest
from reconcile_linear_perpetual import reconcile

def fill(t,q,p,fee,pnl):
    return dict(timestamp_ms=t,sequence=0,kind='fill',signed_quantity_btc=q,price_usdt=p,
                commission_asset='USDT',commission_usdt=fee,reported_realized_pnl_usdt=pnl)

class ReconciliationTests(unittest.TestCase):
    def test_partial_close_reversal_and_settlement(self):
        events=[fill(1,'1','10000','4','0'),fill(2,'-.4','11000','1.76','400'),
            dict(timestamp_ms=3,sequence=0,kind='funding',wallet_delta_usdt='-.63'),
            fill(4,'-1','9000','3.6','-600'),
            dict(timestamp_ms=5,sequence=0,kind='snapshot',mark_price_usdt='9500',
                 reported_wallet_usdt='9790.01',reported_position_btc='-.4',reported_entry_usdt='9000',
                 reported_equity_usdt='9590.01',reported_maintenance_usdt='19'),
            fill(6,'.4','8800','1.408','80'),dict(timestamp_ms=7,sequence=0,kind='transfer',wallet_delta_usdt='125')]
        d=reconcile('10000',events)
        self.assertEqual(d['status'],'RECONCILED');self.assertEqual(d['ending_wallet_usdt'],'9993.602')
        self.assertEqual(d['realized_pnl_usdt'],'-120.0');self.assertEqual(d['commission_usdt'],'10.768')
        self.assertEqual(d['records'][3]['position_btc'],'-0.4');self.assertEqual(d['records'][3]['entry_usdt'],'9000')
        self.assertEqual(d['cash_identity_residual_usdt'],'0.000')
    def test_nonzero_opening_position_requires_entry(self):
        with self.assertRaises(ValueError):reconcile('10000',[],initial_position_btc='2')
        d=reconcile('10000',[fill(1,'-1','11000','4.4','1000')],initial_position_btc='2',initial_entry_usdt='10000')
        self.assertEqual(d['ending_wallet_usdt'],'10995.6')
        self.assertEqual(d['records'][0]['position_btc'],'1')
        self.assertEqual(d['records'][0]['entry_usdt'],'10000')
    def test_wallet_notional_is_not_principal(self):
        d=reconcile('1000',[fill(1,'1','20000','8','0')])
        self.assertEqual(d['ending_wallet_usdt'],'992')
        self.assertEqual(d['status'],'DISCREPANCIES_OR_MISSING_SNAPSHOTS')
    def test_non_settlement_fee_asset_requires_conversion(self):
        event=fill(1,'1','20000','8','0');event['commission_asset']='BNB'
        with self.assertRaises(ValueError):reconcile('1000',[event])
    def test_missing_snapshot_is_not_zero(self):
        with self.assertRaises(ValueError):reconcile('1000',[dict(timestamp_ms=1,sequence=0,kind='snapshot')])
    def test_duplicate_event_order_rejected(self):
        e=fill(1,'1','20000','8','0')
        with self.assertRaises(ValueError):reconcile('1000',[e,e])
    def test_adverse_report_is_retained(self):
        events=[fill(1,'1','10000','4','0'),dict(timestamp_ms=2,sequence=0,kind='snapshot',mark_price_usdt='9000',
            reported_wallet_usdt='996',reported_position_btc='1',reported_entry_usdt='10000',
            reported_equity_usdt='1',reported_maintenance_usdt='45')]
        d=reconcile('1000',events)
        self.assertEqual(d['status'],'DISCREPANCIES_OR_MISSING_SNAPSHOTS')
        self.assertEqual(d['discrepancies'][0]['residual'],'-5')
        self.assertEqual(d['records'][-1]['reported_margin_headroom_usdt'],'-49')

if __name__=='__main__':unittest.main()
