"""Audit only the schema of a public TWSE day-trading report after P1T's windows."""

import argparse
from datetime import date
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ENDPOINT = "https://www.twse.com.tw/rwd/zh/dayTrading/TWTB4U"


def public_schema(report_date):
    requested = date.fromisoformat(report_date)
    if requested < date(2024, 1, 1):
        raise ValueError("Choose a date after the P1T windows for this separate schema audit")
    ymd = requested.strftime("%Y%m%d")
    query = urlencode({"date": ymd, "response": "json", "selectType": "All"})
    request = Request(f"{ENDPOINT}?{query}", headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=20) as response:
        body = json.load(response)
    if body.get("stat") != "OK" or body.get("date") != ymd:
        raise ValueError("TWSE did not return a report for the requested session")
    tables = body.get("tables", [])
    if len(tables) != 2 or any(not t.get("fields") or not t.get("data") for t in tables):
        raise ValueError("Expected market and stock day-trading tables with data")
    return {"source": ENDPOINT, "date": requested.isoformat(),
            "tables": [{"fields": t["fields"], "row_count": len(t["data"])} for t in tables]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("date", help="ISO date after P1T's data windows")
    print(json.dumps(public_schema(parser.parse_args().date), ensure_ascii=False, indent=2))
