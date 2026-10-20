# ============================================================================
# CELL A0 — ALPACA ACCESS (free paper-trading account; no funding needed)
# Put your keys in Colab's "Secrets" panel (key icon on the left) as ALPACA_KEY and ALPACA_SECRET, or paste them when
# asked. Keys stay in your Colab session; they are never written to Drive or to any result file.
# ============================================================================
import urllib.parse, getpass
try:
    from google.colab import userdata
    AK, AS = userdata.get("ALPACA_KEY"), userdata.get("ALPACA_SECRET")
except Exception:
    AK = AS = None
if not AK:
    AK = getpass.getpass("Alpaca API key ID: "); AS = getpass.getpass("Alpaca API secret: ")
DATA, TRADE = "https://data.alpaca.markets/v2", "https://paper-api.alpaca.markets/v2"
def aget(url, params=None, tries=5):
    q = url + ("?" + urllib.parse.urlencode(params) if params else "")
    for i in range(tries):
        try:
            req = urllib.request.Request(q, headers={"APCA-API-KEY-ID": AK, "APCA-API-SECRET-KEY": AS})
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(15); continue
            if e.code in (400, 403, 404, 422):
                return {"_error": e.code, "_body": e.read().decode()[:300]}
            time.sleep(3 * (i + 1))
        except Exception:
            time.sleep(3 * (i + 1))
    return {"_error": "network"}
t = aget(f"{DATA}/stocks/trades", {"symbols": "AAPL", "start": "2024-06-10T14:00:00Z", "end": "2024-06-10T14:01:00Z", "feed": "sip", "limit": 5})
ok_sip = "trades" in t and t["trades"].get("AAPL")
print("Historical SIP trades available on this account:", bool(ok_sip), "" if ok_sip else t)
assert ok_sip, "Your plan does not return historical SIP trades; tell Claude (an IEX-only test would cover ~2% of volume)."
UDIR = os.path.join(BASE, "data_us"); os.makedirs(UDIR, exist_ok=True)
