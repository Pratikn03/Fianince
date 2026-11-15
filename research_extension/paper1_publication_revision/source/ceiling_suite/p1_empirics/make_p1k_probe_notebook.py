"""Builds P1K_Probe_Colab.ipynb: a schema probe for the draft P1K test. It reads one burned day (2012-01-02) for
three stocks and prints column names, row counts and dtypes only. It prints no flow, price or return value and
computes no statistic. The KRX login comes from Colab Secrets (KRX_ID, KRX_PW); nothing is typed into the notebook."""
import json, pathlib

MD = """# P1K schema probe (burned day only)

Checks that Korea's detailed investor-category data can be read, before any test is designed around them.

**Before running:** create a free account on the KRX Data Marketplace (data.krx.co.kr) if you do not have one.
In Colab, open the key icon on the left (Secrets) and add two secrets, `KRX_ID` and `KRX_PW`, with notebook access
switched on. Never paste them into a cell or into chat.

The notebook reads one burned day (2 January 2012) for three stocks and prints column names and row counts only.
It prints no values and computes nothing. Send back the printed output.
"""

CODE = r'''
import os, subprocess, sys, json
subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'pykrx==1.2.9'], check=True)
from google.colab import userdata
os.environ['KRX_ID'] = userdata.get('KRX_ID')
os.environ['KRX_PW'] = userdata.get('KRX_PW')
from pykrx import stock

DAY = '20120102'
TICKERS = ['005930', '000660', '005380']   # three large KOSPI stocks
report = {'day': DAY, 'tickers': TICKERS, 'checks': {}}

def shape(df):
    return {'rows': int(len(df)), 'columns': [str(c) for c in df.columns], 'dtypes': [str(t) for t in df.dtypes]}

for t in TICKERS:
    out = {}
    try:
        out['flows_detail'] = shape(stock.get_market_trading_value_by_date(DAY, DAY, t, detail=True))
    except Exception as e:
        out['flows_detail'] = {'error': type(e).__name__ + ': ' + str(e)[:200]}
    try:
        out['ohlcv'] = shape(stock.get_market_ohlcv_by_date(DAY, DAY, t))
    except Exception as e:
        out['ohlcv'] = {'error': type(e).__name__ + ': ' + str(e)[:200]}
    try:
        out['market_cap'] = shape(stock.get_market_cap_by_date(DAY, DAY, t))
    except Exception as e:
        out['market_cap'] = {'error': type(e).__name__ + ': ' + str(e)[:200]}
    report['checks'][t] = out

try:
    members = stock.get_index_portfolio_deposit_file('1028', DAY)   # KOSPI 200
    report['kospi200_constituents_on_day'] = len(members)
except Exception as e:
    report['kospi200_constituents_on_day'] = 'error: ' + type(e).__name__ + ': ' + str(e)[:200]

print(json.dumps(report, indent=1, ensure_ascii=False))
print('\nOnly column names and row counts were printed. No values were read into the output.')
'''

nb = {"nbformat": 4, "nbformat_minor": 5,
      "metadata": {"kernelspec": {"name": "python3", "display_name": "Python 3"}, "language_info": {"name": "python"}},
      "cells": [{"cell_type": "markdown", "metadata": {}, "source": MD.splitlines(keepends=True)},
                {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
                 "source": CODE.lstrip("\n").splitlines(keepends=True)}]}
if __name__ == "__main__":
    compile(CODE, "cell", "exec")
    out = pathlib.Path(__file__).resolve().parent / "P1K_Probe_Colab.ipynb"
    out.write_text(json.dumps(nb, indent=1, ensure_ascii=False))
    print("wrote", out.name)
