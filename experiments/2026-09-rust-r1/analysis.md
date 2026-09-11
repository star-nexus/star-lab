# Analysis

Observation: Python's mutable component graph and GIL are unsuitable as the
per-unit cross-language hot-loop boundary. The accepted migration first needs
independently owned state and a verified deterministic runtime foundation.

Hypothesis: importing initial owned data and detaching before locking the native
world permits future native compute without Python object access or GIL deadlock.

Instrumentation/evidence: initial-state export/import equality, atomic failing
reset, new lifecycle epochs, old returned data surviving reset, closed-instance
errors, 24/30Hz clock/pause/time-scale comparison, CPython random-state comparison,
and a Python thread advancing during a long native call. Twenty seed/domain
combinations cover 1400 mixed RNG operations each across MT twists and rejection
sampling. Imported advanced map RNG state is resumed instead of reseeded. Six
probe cases preserve full Python/native state and RNG evidence. All checks passed.

Implemented boundary: generic Bevy World owns external-ID-mapped component data;
RoTK owns scene and clock; PyO3 detaches before every native lock. Initial cold
component columns are retained pending typed gameplay ports. No Python world is
retained after preparation. No ownership or thread completion order generates IDs.

Limits: this does not migrate gameplay, claim CPU scaling, validate native
parallel schedules or prove portability of combat math. One platform/ABI release
wheel was tested. The test suite must be installed with native support; otherwise
native-specific tests skip and cannot be called a native gate pass.
