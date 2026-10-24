# Running the registered tests in Google Colab

Both tests are registered: their specifications were pushed to `main` in commits of their own
before any of their data were downloaded. Each runs **once**. Whatever the result, push it.

## Test E1v2 — certify versus identify (run now)

1. Open <https://colab.research.google.com>, choose **File → Open notebook → GitHub**, paste
   `Pratikn03/Fianince` and open `thesis/evidence/E1v2_Certify_vs_Identify.ipynb`.
2. (Recommended, for saving the result automatically) Create a GitHub token with `repo` scope
   (GitHub → Settings → Developer settings → Personal access tokens). In Colab click the key icon
   on the left (**Secrets**), add a secret named `GITHUB_TOKEN`, paste the token and switch on
   notebook access. The notebook reads it from Secrets and never prints it or writes it to a file.
3. Run cells 1 and 2. Cell 1 asks to mount Google Drive (a cache, so a disconnect does not lose
   downloads). Cell 2 must print the specification hash `0b6c31c0…` and `counter: {'opens': 0, …}`.
4. Run cell 3. This opens the test (the counter becomes 1), downloads about 6,300 files from
   data.binance.vision and evaluates. Expect 20–40 minutes. If a cell stops because of the network,
   re-run the same cell: downloads are cached on Drive.
5. Run cell 4 to see the results and cell 5 to push them (with the token) or download
   `e1v2_result.zip` (set `PUSH = False`) and send it.

The four files that come back are `checks/prereg/E1v2_unlock.json` (counter 1),
`evidence/E1v2_results.json`, `checks/E1v2_numbers.tex` and `evidence/E1v2_download_log.json`.
The thesis text for E1 is then written from those files; `verify_thesis_numbers.py` switches from
"registered, not yet run" to re-evaluating the result from its file.

## Test E2 — prospective mechanism test (run on or after 2 February 2027)

Same steps with `thesis/evidence/E2_Prospective_Analysis.ipynb`. The analysis refuses to run before
2027-02-02, when the archive holds every date of the window (2026-10-24 to 2027-01-31). It downloads
about 6,000 files (klines, order-book depth, metrics) for 20 symbols; expect 40–90 minutes.

## If something goes wrong

* `assert ... changed after registration`: a registered file differs from its hash. Do not edit it;
  pull the repository again (cell 1).
* `already opened`: the counter is 1. The test was opened before; do not reset the counter. Report
  what happened instead.
* A symbol with too few valid days is excluded by the registered rule and listed in the results.
