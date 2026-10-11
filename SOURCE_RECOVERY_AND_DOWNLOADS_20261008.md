# Source recovery and download status

**Browser-failure update, October 8, 2026:** The user's screenshot shows failed official FI-2010 transfers with both “File wasn't available on site” and “Check internet connection.” Automatic acquisition had also truncated. These observations establish failed transfers in the tested clients; they do not diagnose the user's internet connection or prove a global outage. The earlier request to retry the official download is withdrawn. **No further download is requested from the user now.**

Author declarations are now recorded: equal contributions, no external research funding received and no conflicts declared for both authors. Affiliations/status remain unknown. The user reports sending the paper to reviewers; reviewer identities, version and written assessment remain unknown/unrecorded.

## Recovered locally

- Four Antigravity/Gemini full finance-related transcripts, including the primary42MB session;18,817 JSONL records in total. Runtime-generation metadata was recovered through read-only SQLite/protobuf parsing. Private transcript copies remain on T9, outside the public reviewer package.
- The original January CSV was retrieved from siavashraz's public version1 release. Its1,195,785,420 bytes exactly match the current CSV SHA256, and the ZIP CRC passed. The provider declares Binance BTCUSDT.P perpetual data at250ms sampling and an MIT licence. This closes the missing provider-description link; independent exchange authentication and final rights remain separate. [Original uploader](https://www.kaggle.com/datasets/siavashraz/bitcoin-perpetualbtcusdtp-limit-order-book-data).
- The supplied equity CSV already exactly replays independent normalized FI-2010 source files. The primary publication documents the source company list, raw euro-price encoding and intentional public normalization. Mapping the local labels and reconstructed columns to physical quantities remains unverified. [Primary paper, Table1 and Sections3.2–3.3](https://pure.au.dk/ws/files/143396530/Ntakaris_et_al_2018_Journal_of_Forecasting.pdf).

## Official archive remains unavailable in the observed transfers

The filesystem scan found no archive with the published FI-2010 size; relevant project ZIP/tar archives also lacked the original benchmark archive. Some macOS-protected locations could not be read, so this is a scoped search result rather than a claim that no copy exists anywhere. The official automated download again stopped after roughly65KB with IncompleteRead; its server ignored the range request. The partial file is not an authenticated archive.

The [official FI-2010 Data page](https://etsin.fairdata.fi/dataset/73eb48d7-4dbc-4a10-a52a-da745b47a649/data) identifies `published/BenchmarkDatasets/BenchmarkDatasets.zip`. Its metadata lists **1,864,361,899 bytes** and SHA256:

`cea93692a270724fa91e8f124da641db727d757e5e0f0bb85067709e9932f664`

The full original ZIP checksum remains unverified. If a complete original copy becomes available later, it must match those bytes and checksum; an alternative or repackaged ZIP cannot close this particular check. The prior delivery receipt and sealed reviewer package are preserved as historical snapshots. Their manual-download request is superseded by `fi_download_availability_update_20261008.json`.

This archive authenticates the normalized benchmark bytes. Its download does not supply restricted original Nasdaq records, actual broker positions, account funding/margin histories or an independent review. Publicly downloadable proxy files cannot replace missing account records.

## Verified alternative recovered automatically

The [DeepLOB authors' repository](https://github.com/zcakhaa/DeepLOB-Deep-Convolutional-Neural-Networks-for-Limit-Order-Books) contains a working `data/data.zip`. The downloaded file is pinned to commit `ff14d7c2fd38bdfc143389786993d0f0236d4eb8`, has **56,278,154 bytes**, and SHA256 `7a5564290a504bdc104dccaf44aa6c0b3857bf1db6b0517b9b88577c2def3e5f`. Every ZIP member was streamed with CRC and SHA256 checking. It is saved to:

`/Volumes/T9/machine_markets_data/local_source_recovery_20261008/deeplob_author_data.zip`

- Three final-day files exactly match the recovered mirror files byte for byte.
- The seven-day training aggregate groups anonymous price blocks across days. After checking that ordering, all 40 order-book feature rows and all five label rows match the corresponding seven recovered daily files exactly as numeric text, with no rounding.
- Together, these checks corroborate the order-book and label inputs for **all 394,337 normalized events** used in the existing ten-day reconstruction.
- Seven other derived-feature rows differ in the training aggregate. Those differences are recorded, not silently removed. The aggregate is therefore **not an exact replacement for all 149 feature rows** in the daily files.

The existing replication uses the checked order-book inputs. Its normalized-input evidence now has a second public source. This alternative does not include every auction/normalization/cross-validation variant, authenticate the full official ZIP, identify companies within local anonymous blocks, or recover physical normalization factors. No new model fitting or learner training was performed. Primary FI-2010 attribution and CC BY 4.0 obligations still apply; a GitHub download does not expand data-reuse rights.

Receipt: `research_extension/gap_closure_20261006/publication_completion/submission_completion/fi_deeplob_alternative_acquisition.json`. Replay: `verify_deeplob_alternative.py` in the same directory.

## Recovered policy artifacts

Twenty real checkpoint files on T9 safely load as finite tensor dictionaries. They match the separate five-input simulated continuous-trading source. Independent feedforward evaluation reproduces all100 saved radius/seed records and10 summaries, with maximum difference3.56e-15. The saved universal small-radius R2-below0.70 conclusion is false: actor-small R2 ranges0.6539716–0.9987782. These files do not establish the distinct legacy real-LOB policy, optimizer/reward histories or actual account executions. No new training was performed.
