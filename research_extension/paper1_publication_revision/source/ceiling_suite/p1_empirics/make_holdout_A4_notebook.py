"""Builds P1T_Holdout_A4_Colab.ipynb: the holdout notebook with amendment A4 (P1T_amendment_A4.md).

A4 changes only how one row label is read. In TWSE's MI_INDEX response for 2019-04-29, the weighted-index row of
the price-index table is labelled '加權股價指數' instead of '發行量加權股價指數'. The label was diagnosed from labels
only, with no values printed. The executor (p1t_executor.py) is unchanged and its SHA-256 is unchanged.
"""
import json
import make_holdout_notebook as mk

A4_LOAD = r'''
# Amendment A4 (P1T_amendment_A4.md; approved before any statistic was computed). TWSE's MI_INDEX response for
# 2019-04-29 labels the weighted index '加權股價指數' instead of '發行量加權股價指數'. That label is read as the registered
# name in the price-index table of that one day. The alias on any other day, or a day that already has the registered
# name, stops the run.
A4_DAY, A4_ALIAS, A4_TABLE = "20190429", "加權股價指數", "價格指數(臺灣證券交易所)"
A4_applied = set()
def a4_relabel(j, d):
    for t in j.get("tables", []):
        if not (t.get("title") or "").endswith(A4_TABLE):
            continue
        rows = t.get("data") or []
        hits = [row for row in rows if str(row[0]).strip() == A4_ALIAS]
        if not hits:
            continue
        if d != A4_DAY or len(hits) != 1 or any(str(row[0]).strip() == ex.INDEX_NAME for row in rows):
            raise SystemExit(f"Amendment A4: alias row on an unexpected day or table ({d}); stop before any statistic.")
        hits[0][0] = ex.INDEX_NAME
        A4_applied.add(d)
    return j
def load(sub, d):
    j = json.loads(gzip.open(os.path.join(ROOT, sub, d + ".json.gz")).read())
    return a4_relabel(j, d) if sub == "MI" else j
'''

A4_CHECK = 'assert A4_applied == {A4_DAY}, f"Amendment A4 applied to {sorted(A4_applied)}, expected [{A4_DAY}]"\n'


def analysis_a4():
    a = mk.ANALYSIS
    k = a.index('print("integrity gate passed:"')
    return a[:k] + A4_CHECK + a[k:]


def build():
    sha = mk.build()                                       # writes P1T_Holdout_Colab.ipynb (unchanged content)
    nb = json.load(open("P1T_Holdout_Colab.ipynb"))
    cell = nb["cells"][1]["source"]
    old_load = 'def load(sub, d): return json.loads(gzip.open(os.path.join(ROOT, sub, d + ".json.gz")).read())\n'
    assert cell.count(old_load) == 1
    cell = cell.replace(old_load, A4_LOAD)
    k = cell.index('print("integrity gate passed:"')
    cell = cell[:k] + A4_CHECK + cell[k:]
    compile(cell, "cell", "exec")
    nb["cells"][1]["source"] = cell
    nb["cells"][0]["source"] = nb["cells"][0]["source"].replace(
        "# P1T holdout run (TWSE, 2019-01-02 to 2023-12-29): opened once",
        "# P1T holdout run with amendment A4 (TWSE, 2019-01-02 to 2023-12-29): opened once") + (
        "\n\n**Amendment A4.** The run with the first notebook stopped at the integrity gate before any statistic was "
        "computed. The cause was one index-row label on 2019-04-29. This notebook reads that label as the registered "
        "name, on that day only, and checks that it did so exactly once. Nothing is downloaded again. The executor is "
        "unchanged.")
    json.dump(nb, open("P1T_Holdout_A4_Colab.ipynb", "w"), ensure_ascii=False, indent=1)
    return sha


if __name__ == "__main__":
    print(build())
