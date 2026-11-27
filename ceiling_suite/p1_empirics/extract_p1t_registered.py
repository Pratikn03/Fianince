"""Extract the registered P1T holdout results (amendment A4 run of 8 November 2026) from the printed Colab output
into JSON, so figures can use the registered numbers without retyping them. Reads only the printed output file."""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / 'results' / 'p1t_holdout_A4_printed_output.txt'
OUT = HERE / 'results' / 'p1t_holdout_registered_A4.json'


def _block(text, key):
    i = text.index(key) + len(key)
    j = text.index('{', i)
    depth = 0
    for k in range(j, len(text)):
        depth += {'{': 1, '}': -1}.get(text[k], 0)
        if depth == 0:
            return json.loads(text[j:k + 1])
    raise ValueError(key)


def main():
    t = SRC.read_text()
    out = {
        'source': SRC.name,
        'primary_block20': _block(t, 'REGISTERED PRIMARY (holdout, Foreign):'),
        'robustness_blocks': _block(t, 'robustness blocks:'),
        'reverse_causality': _block(t, 'reverse causality:'),
        'stability': {k: {'D': v[0], 'ci95': v[1], 'verdict': v[2]}
                      for k, v in _block(t, 'stability:').items()},
    }
    OUT.write_text(json.dumps(out, indent=1))
    p = out['primary_block20']
    print(f"registered primary D = {p['D']:.4f} {[round(x, 4) for x in p['ci95']]}; wrote {OUT.name}")


if __name__ == '__main__':
    main()
