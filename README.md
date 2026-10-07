# QuoteQuorum

QuoteQuorum is a GenLayer Intelligent Contract for owner-scoped market snapshots. A feed registers three to five HTTPS JSON providers with distinct hostnames and a spread bound. Validators independently fetch the values, preserve ordinary quote precision, calculate the statistical median (averaging the two middle values for four sources) and dispersion, and store source-bound digests. A feed is `OPEN` until one finalized consensus sample becomes `SAMPLED`.

Contract: `0x1c3E5eb136D86c39Ff8db6bC50AB6b4946564188` on Studionet.
Deployment transaction: `0x741995db73b4ae9d2423ab743bcf48fda8c94acf5538a39a90f41246a0c49d81`.
Reviewed source SHA-256: `ab2f14092f890780c0dd1be1495176742da373646d32143efa67db9859ebb4b2`.
Website: `https://quote-quorum-genlayer.pages.dev/`

Run `npm install`, `npm run contract:test`, `npm run contract:lint`, and `npm run build` from this directory. The lint command targets `contracts/quote_quorum.py`.
