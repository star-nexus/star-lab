# E1 Closeout Note

The uninstrumented same-session A/B run `20260907-034626` closed E1 as `DO_NOT_KEEP`.

The treatment produced a material mixed-workload benefit at 50% moving but essentially no full-motion benefit:

```text
50% non-cull saving   0.615 ms/frame
100% non-cull saving  0.034 ms/frame
```

The 100% result misses the preregistered 0.50 ms/frame floor by roughly 15x. Production remains `17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a`.

This note exists to make the negative result difficult to accidentally reopen without new evidence. The next active UnitRender question is E2: explain the movement-dependent increase in cull cost per candidate.
