# Decision

Keep the R1 checkpoint and continue R2 typed gameplay migration. The Python game
remains default. Native readiness reports `gameplay_ready=false` explicitly.
Do not wire the current clock-only step as a playable game or call it a faster ENV.

Use a mutex around the single native owner, acquired while detached from Python.
Invalid scene reset is transactional; a poisoned owner fails permanently. Keep
full initial cold state for incremental porting, replacing each hot component with
one typed authoritative representation as its system is migrated. Do not keep two
writable copies or synchronize every Python Unit per tick.

Preserve CPython used sampling methods and domain separation. Do not substitute
Rust thread_rng, reseed after map preparation, or consume combat draws by worker
finish order. R4 introduces an actual bounded worker pool only after parity.
