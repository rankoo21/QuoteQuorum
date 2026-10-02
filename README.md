# QuoteQuorum

QuoteQuorum is a GenLayer Intelligent Contract for owner-scoped market snapshots. A feed registers three to five HTTPS JSON providers with distinct hostnames and a spread bound. Validators independently fetch the values, normalize the snapshot, calculate the median and dispersion, and store source-bound digests. A feed is `OPEN` until one finalized consensus sample becomes `SAMPLED`.

Contract: `0xC603E6e434120F9ac6314B3C15F0b9f76A616C00` on Studionet.
Website: `https://quote-quorum-genlayer.pages.dev/`

Run `npm install`, `npm run contract:test`, `npm run contract:lint`, and `npm run build`.
