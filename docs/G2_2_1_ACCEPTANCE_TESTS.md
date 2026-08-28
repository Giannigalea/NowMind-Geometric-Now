# G2.2.1 Acceptance Tests

All prior tests remain mandatory.

## Retrieval
- indexed/reference retrieval agree semantically;
- index uses trace metadata only;
- no old NowState indexing;
- no ExperimentRecorder/evaluator indexing;
- retrieval metrics are consistent.

## Stale target
- memory A may guide initial search;
- observing A empty disconfirms the current assumption;
- disconfirmed A is not selected forever;
- historical trace remains;
- frontier search can reacquire B.

## Hidden changes
- hidden obstacle change does not leak before perception;
- after perception, affected plan invalidates/replans;
- hidden target move does not leak;
- target changes only after observation.

## Verification
- verification may be selected when outcomes alter the decision;
- verification is skipped when it cannot justify its cost;
- useful/wasted classification is evaluator-side.

## Anti-overfit
- runtime does not import benchmark family metadata;
- runtime behavior is independent of trial ID/name.

## Holdout
- holdout seed differs;
- holdout trial IDs differ;
- config saved;
- full metrics generated.

## Invariants
- memory-as-observation = 0;
- prediction-as-fact = 0;
- old Nows inaccessible;
- all G1/G2/G2.1/G2.2 tests remain green.
