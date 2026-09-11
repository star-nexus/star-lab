# Analysis

Observation: query membership was a Python set, used directly by simulations,
observations and rendering. Visibility history also converted a faction set into
a list. Even without concurrency, the latter changed list order between processes.

Hypothesis: a Rust port compared to those unspecified orders would confuse
container implementation differences with rule regressions.

Instrumentation: every local action/tick records input, full decoded response,
ordered synchronous events, component/singleton state and recovery ledger.
RNG objects export complete MT state. Wall clock and datetime are injected before
STAR imports, preserving metadata without replacing simulation dt. Maps and sets
are canonicalized in diagnostic serialization; lists and numeric types are compared
strictly. First mismatch is reported by exact JSON path.

Evidence: six normalized traces (1843 operations total) replay identically with
hash seeds 123 versus 981. The original source first differs at operation21's
VisibilityTracker history faction list. That negative comparison remains archived.
The 919-test full regression passed, including cache invalidation, explicit
selection order, release order, event nesting and path tie contracts.

Root cause: set iteration was entering ordered public/history structures. The fix
adds a cached ordered entity view and explicit ordering at the remaining output
and active-queue boundaries. Empty-entity all/exclusion query invalidation is
covered too. Existing gameplay formulas and time semantics remain unchanged.

Limits: this is finite deterministic replay coverage, not a proof for every possible
input, all scenario extensions, real LLM timing, cross-platform floats or rendered
pixels. Native parity and full lifecycle testing remain required in R1–R5. No
latency/capacity conclusion is drawn from these traces. State-format coverage must
be extended if a new authoritative component is introduced.
