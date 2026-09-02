# STAR Lab

**Engineering evidence, reproducibility, and scalability records for [STAR / StarBench](https://github.com/star-nexus/star).**

STAR Lab is intentionally separate from the production/runtime repository.

- `star-nexus/star` is the product and benchmark repository. Users should normally use `main` there.
- `star-nexus/star-lab` is the engineering research archive: reproducible problem reports, controlled experiments, raw evidence, root-cause analyses, engineering decisions, and the historical STAR Performance Frontier.

The core rule is simple:

> Every important engineering conclusion must be traceable from the claim, to raw evidence, to a reproducible experiment, to an exact `star` commit or immutable tag.

## Start here

1. Read [`PROTOCOL.md`](PROTOCOL.md) before adding a formal experiment.
2. Create new experiment packages from [`templates/`](templates/).
3. Preserve only evidence that supports a durable engineering conclusion.
4. Bind every formal experiment to exact `star-nexus/star` commit SHA(s); never rely on a moving branch name alone.
5. Update [`records/performance-frontier.md`](records/performance-frontier.md) only for validated frontier results.

## Repository layout

```text
star-lab/
├── README.md
├── PROTOCOL.md
├── templates/
│   ├── experiment-readme.md
│   ├── manifest.yaml
│   ├── analysis.md
│   └── decision.md
├── experiments/
├── investigations/
├── decisions/
└── records/
    └── performance-frontier.md
```

## Version roles

```text
star branch       = active work line
star checkpoint   = temporary comparison / debugging baseline
star annotated tag= validated immutable engineering milestone
star-lab          = reproducible evidence and decision history
```

STAR Lab is not a fork of STAR source history. It has its own Git history and references STAR source states through exact commit SHAs and tags.
