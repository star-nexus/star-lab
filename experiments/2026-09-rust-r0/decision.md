# Decision

Freeze `78cc8da3a03ffedaea58642abae8fcb710db997d` as the normalized R0 oracle.
Keep `entities()` as a set API; use a shared immutable ascending-ID tuple for
ordered consumers. Cache membership order, not computed component values.
Invalidate by relevant membership changes, world reset and explicit cache clear.
Sort only dirty/due active subsets at those boundaries.

Preserve fixed path-neighbor/heap ties, stable system installation priority,
synchronous subscription/depth-first event order, explicit selected-ID order,
registration order and message FIFO. Preserve all movement weakening rules.
Old experiments continue to use their original immutable source tags.

Rejected: expecting Rust containers to imitate incidental Python set layout;
sorting all resident units on every tick; sorting responses only and hiding
simulation/event differences. Python remains default; this phase does not deliver
a Rust backend or change any performance frontier. Revisit contracts only through
an explicit rules/oracle version change, never by weakening the comparator.
