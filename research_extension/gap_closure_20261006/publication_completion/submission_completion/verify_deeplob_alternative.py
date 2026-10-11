"""Compare the pinned DeepLOB authors' normalized subset with recovered FI files.

This checks published representation agreement, not original Nasdaq quantities,
company identities, licences of a mirror, or the primary full archive checksum.
No fitted model or empirical estimate is changed.
"""
import contextlib
import hashlib
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
BASE = Path('/Volumes/T9/machine_markets_data/local_source_recovery_20261008')
MIRROR = Path('/Volumes/T9/machine_markets_data/fi_equity_mirror_20261008')
COMMIT = 'ff14d7c2fd38bdfc143389786993d0f0236d4eb8'
ZIP_SHA = '7a5564290a504bdc104dccaf44aa6c0b3857bf1db6b0517b9b88577c2def3e5f'


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        while data := stream.read(1024 * 1024):
            h.update(data)
    return h.hexdigest()


def run():
    import zipfile

    archive = BASE / 'deeplob_author_data.zip'
    assert sha(archive) == ZIP_SHA
    receipt = json.loads((HERE / 'fi_deeplob_alternative_acquisition.json').read_text())
    members = receipt['members']
    overlap = []
    with zipfile.ZipFile(archive) as z:
        for info in z.infolist():
            if info.is_dir():
                continue
            h = hashlib.sha256()
            with z.open(info) as stream:
                while data := stream.read(1024 * 1024):
                    h.update(data)
            expected = next(x for x in members if x['name'] == info.filename)
            assert h.hexdigest() == expected['sha256']
            if info.filename.startswith('Test_'):
                local = MIRROR / info.filename
                local_sha = sha(local)
                with local.open('rb') as stream:
                    events = len(stream.readline().split())
                overlap.append(dict(member=info.filename, local_path=str(local),
                                    local_bytes=local.stat().st_size,
                                    local_sha256=local_sha,
                                    normalized_events=events,
                                    matches=local_sha == h.hexdigest()))

        files = [MIRROR / 'Train_Dst_NoAuction_DecPre_CF_1.txt'] + [
            MIRROR / f'Test_Dst_NoAuction_DecPre_CF_{i}.txt' for i in range(1, 7)]
        boundaries = []
        for path in files:
            with path.open('rb') as stream:
                row = np.fromstring(stream.readline().decode(), sep=' ')
            cuts = np.argsort(np.abs(np.diff(row)))[-4:] + 1
            boundaries.append(np.sort(np.r_[0, cuts, len(row)]).astype(int).tolist())

        # Each source day has five anonymous price blocks. The aggregate groups
        # the same block over seven days before proceeding to the next block.
        # Exact matching of ALL feature/label tokens tests this inferred ordering.
        rows = 0
        tokens = 0
        mismatches = []
        numeric_diagnostics = []
        with contextlib.ExitStack() as stack:
            streams = [stack.enter_context(p.open('rb')) for p in files]
            source = stack.enter_context(z.open('Train_Dst_NoAuction_DecPre_CF_7.txt'))
            while line := source.readline():
                chunks = [stream.readline().split() for stream in streams]
                assert all(len(chunk) == bounds[-1]
                           for chunk, bounds in zip(chunks, boundaries))
                expected = [token for block in range(5)
                            for chunk, bounds in zip(chunks, boundaries)
                            for token in chunk[bounds[block]:bounds[block + 1]]]
                actual = line.split()
                rows += 1
                tokens += len(actual)
                if actual != expected:
                    mismatches.append(rows)
                    a = np.array(actual, dtype=np.float64)
                    e = np.array(expected, dtype=np.float64)
                    different = np.flatnonzero(a != e)
                    numeric_diagnostics.append(dict(
                        row_one_based=rows,
                        text_token_mismatches=sum(x != y for x, y in zip(actual, expected)),
                        numeric_mismatches=len(different),
                        max_absolute_difference=float(np.max(np.abs(a - e))),
                        examples=[dict(column_zero_based=int(i), aggregate=actual[i].decode(),
                                       separate_day=expected[i].decode())
                                  for i in different[:3]]))
            extra_rows = any(stream.read(1) for stream in streams)
        aggregate = dict(
            member='Train_Dst_NoAuction_DecPre_CF_7.txt',
            comparison='Exact whitespace-delimited feature/label tokens after '
                       'grouping each of five anonymous price blocks across '
                       'Train CF1 then Test CF1..6; no numeric rounding',
            anonymous_block_boundaries=boundaries,
            compared_rows=rows, compared_tokens=tokens,
            mismatched_rows=mismatches, extra_local_rows=extra_rows,
            mismatch_diagnostics=numeric_diagnostics,
            first_40_order_book_rows_match=not any(i <= 40 for i in mismatches),
            last_five_label_rows_match=not any(i >= 145 for i in mismatches),
            matches=rows == 149 and not mismatches and not extra_rows,
            local_parts=[str(path) for path in files],
            local_parts_sha256={path.name: sha(path) for path in files},
        )
    receipt['overlap_checks'] = overlap
    receipt['reordered_training_aggregate_check'] = aggregate
    receipt['covers_all_ten_days_under_verified_reordering'] = (
        all(x['matches'] for x in overlap) and aggregate['matches'])
    receipt['all_ten_days_order_book_and_label_inputs_match'] = (
        all(x['matches'] for x in overlap)
        and aggregate['first_40_order_book_rows_match']
        and aggregate['last_five_label_rows_match'])
    receipt['corroborated_normalized_events'] = (
        aggregate['compared_tokens'] // aggregate['compared_rows']
        + sum(x['normalized_events'] for x in overlap))
    receipt['verifier_sha256'] = sha(Path(__file__))
    receipt['repo_commit'] = COMMIT
    receipt['scope'] = ('NoAuction decimal-normalized ten-day observations. '
                        'Not all auction/normalization/cross-validation variants; '
                        'not the primary ZIP or physical company/unit authentication.')
    (HERE / 'fi_deeplob_alternative_acquisition.json').write_text(
        json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'overlap_byte_matches': sum(x['matches'] for x in overlap),
                      'aggregate': aggregate,
                      'all_149_rows_match': receipt['covers_all_ten_days_under_verified_reordering'],
                      'order_book_and_label_inputs_match': receipt['all_ten_days_order_book_and_label_inputs_match'],
                      'normalized_events': receipt['corroborated_normalized_events']},
                     indent=2))
    assert len(overlap) == 3 and all(x['matches'] for x in overlap)
    assert aggregate['compared_rows'] == 149 and not aggregate['extra_local_rows']
    assert aggregate['first_40_order_book_rows_match'] and aggregate['last_five_label_rows_match']


if __name__ == '__main__':
    run()
