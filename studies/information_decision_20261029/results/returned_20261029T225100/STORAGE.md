# Returned result storage

`account_results.csv.gz` contains the exact unmodified returned `account_results.csv`, compressed losslessly for repository transfer. The downloadable manuscript bundle retains the uncompressed CSV. Its decompressed SHA-256 is `1a87d45c573ccf97d08c6440f156441e630d1276f9948b104c5b1963552fb1e9`.

Read directly with `pandas.read_csv('account_results.csv.gz')`, or restore with `gzip -dk account_results.csv.gz`. All numerical values are unchanged. The original returned-run status and proof receipts are retained as historical execution records; `editorial_summary.json` describes the subsequent manuscript integration.
