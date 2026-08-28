# G2.2.1 Holdout Rules

Preserve G2.2 benchmark v1 exactly:
- seed 20260823
- 3000 trials
- E1-E24
- D1-D6

Create a separate holdout:
- different seed;
- >=2000 trials;
- same grammar, independent generation;
- non-overlapping trial IDs.

Use v1 during development. Run holdout only after implementation is frozen as far as practical.

The Chronological control may use legitimate indexing/caching.

Runtime code must not inspect family names, trial IDs, expected answers, or benchmark seed.
