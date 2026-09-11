# Analysis — skill set order

## Observation and hypothesis

Two hash seeds produce different available_skills lists in the old handler.
Hypothesis: iteration over a set, rather than simulation or RNG state, causes it.

## Instrumentation and evidence

The probe changes only Python hash seed and source commit. It constructs one
unit with four named skills and records the actual handler output. Old lists
differ; corrected lists both equal arrow_evasion,charge,hide,rockslide. All1047
full tests pass. See results/probe.json and results/pytest.log.

## Root cause and rejected explanations

The list comprehension directly iterated UnitSkills.available_skills. This field
was omitted from the initial normalization audit; gameplay RNG is not involved.
The first R0 replay scenarios did not expose multi-skill ordering. Existing tags
are reproducible but must not be described as universally hash-independent.

## Limits

This is one proven ordering gap. It is not a proof that every optional feature is
normalized, and makes no performance or complete-migration claim.
