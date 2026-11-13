# Prospective evidence status

E1 and E2 are not completed studies. No E2 market messages have been recorded.
`E2_accessibility.json` records a headers-only direct WebSocket handshake, not
liquidation observations, historical backfill, or an empirical result.

The recorder uses the documented routed Market endpoint:
`wss://fstream.binance.com/market/ws/!forceOrder@arr`.
The exchange documents separate Public/Market/Private routes, daily disconnects
and heartbeat requirements. See the [official connection documentation](https://developers.binance.com/en/docs/products/derivatives-trading-usds-futures/websocket-market-streams/Connect)
and [market-stream reference](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/ws-streams/market).
The liquidation stream is sampled; it is not a complete liquidation ledger.

## Before recording

Complete and publish an E2 specification with hypotheses, market universe,
prospective dates, primaries, inference and power, pass rules and correction,
code version, recorder SHA256, endpoint, `mode`, `remote_branch`, and
`minimum_recording_months`. Hash the specification and commit/push the spec,
hash and zero unlock counter alone before recording. No complete E2 spec is
claimed by this change. Access terms still need to be confirmed for the study;
transport accessibility alone does not establish licensing.

Use a dedicated environment with `requirements-recorder.txt`. The recording
command requires explicit paths and a positive duration, and refuses modified
or unpushed specifications and changed recorder code:

```sh
python E2_recorder.py --record --spec prereg/E2.json --counter prereg/E2_unlock.json --output /absolute/path/outside/git --hours 24
```

The first collection opening changes the counter to one. Subsequent collector
sessions may append new prospective chunks under that same registered study;
they must not reset the counter or open an analysis test set again. An exclusive
counter lock prevents simultaneous recorders. A stale lock after a crash needs
manual incident review, not an automatic bypass.

The collector writes separate gzip chunks on daily rotation/reconnection and
checksums closed chunks. Its log distinguishes disconnection gaps from connected
periods without events: missing observations must never be called zero
liquidations. It stops below its storage floor or on access-denial HTTP codes;
there is no proxy or regional workaround. A lawful archive fallback would need
its own prospective registration. There is no background collector running.

Software tests cover synthetic chunk rotation, gzip/checksum integrity,
reconnection filenames and rejection of malformed JSON. The long-running live
collection loop has not been validated by an empirical recording session.
