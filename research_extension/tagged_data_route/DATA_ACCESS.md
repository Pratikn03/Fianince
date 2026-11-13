# Tagged-flow data for a direct test of Paper 1 (status, 11 November 2026)

Goal: a dataset in which each trade or order is tagged by trader class or account, fine enough to estimate several
classes' memories from their own flow, so that (1) the sufficiency theorem can be tested directly (same kernel,
same price dynamics, whatever the composition) and (2) price-only estimation can be compared with the tagged truth.

| Source | What is tagged | Access found so far | Next step |
|---|---|---|---|
| Korea Exchange (KRX) | Daily buy and sell by member firm (62 firms) and by investor type, per stock; used for 2007-2017 in arXiv:2004.11148 | Investor-type data are on data.krx.co.kr; member-by-stock history not confirmed; KRX launched a paid cloud download service in 2025 (contents for member data not stated) | Ask KRX data services what member-firm-by-stock history can be licensed, and at what cost |
| EUROFIDAI high-frequency database (Euronext Paris) | Buyer and seller flagged by the AMF as pure or mixed HFT, through 2017 (arXiv:2608.00858) | Sold per market and per year; price on request; no student tier listed | Request a quote and a sample; ask whether a coauthor's institution licence would cover the work |
| Osaka Exchange / Japan FSA | Orders by registered high-speed trader and strategy | Used by the FSA; outside access not stated; FSA data strategy office contact given in the November 2024 note | Ask whether the data or a JPX working-paper collaboration is open to outside researchers |
| China (2024-25 rules) | Exchanges classify high-frequency accounts | Not public | None for now |
| India (SEBI 2025) | Exchange-issued algorithm ID on each algorithmic order | Not public as found | None for now |

Each of these needs a request sent by the author. No data have been requested or received.
