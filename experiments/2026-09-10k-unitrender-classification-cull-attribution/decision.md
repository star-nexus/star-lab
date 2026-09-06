# Decision — UnitRender E

**Status:** CLOSED — attribution complete  
**Formal decision:** `SPECIALIZED_ANIMATION_DISPLACEMENT_API_CANDIDATE_JUSTIFIED`  
**Production:** unchanged at `17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a`

## Selected next candidate

Implement one window-only active-animation position API that returns a world-pixel position **only when an attack or movement animation is active**. No-animation must return `None` instead of synthesizing the committed static pixel position.

The renderer must retain the current epsilon displacement comparison against the committed HexPosition so zero-displacement animation states preserve existing visual semantics.

The candidate must preserve:

- attack animation precedence over movement animation;
- movement interpolation formula and progress semantics;
- zero-displacement boundary behavior;
- static committed-hex grouping;
- rich/full-featured render behavior;
- shared/headless animation APIs unless explicitly required by tests.

A production KEEP decision requires targeted semantic regression plus uninstrumented same-session controlled A/B. Attribution alone is not KEEP.

## Cull

Cull remains `OPEN / NOT_CLOSED` as a separate hypothesis. Candidate volume does not explain the measured cull growth, and no cull optimization is authorized by this case.

## Do not do next

Do not:

- merge animated units by committed hex;
- deduplicate raster draws;
- change movement/attack animation state representation yet;
- optimize Fog/cull in the same candidate;
- alter RenderEngine submission;
- reinterpret diagnostic aggregate frame timing from this instrumented run.
