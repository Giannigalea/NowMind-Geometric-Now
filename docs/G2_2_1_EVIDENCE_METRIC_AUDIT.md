# G2.2.1 Evidence Metric Audit

## Purpose

G2.2 reported a large evidence-inspection gap:

- `N_NowMindEpistemicGeometry`: approximately `669.2`
- `C_ChronologicalEpistemicPlanner`: approximately `15.2`

That comparison is preserved in `docs/G2_2_1_BASELINE_SNAPSHOT.md`, but it was
not an apples-to-apples runtime retrieval measure. The NowMind value included a
legacy planner-side history counter, while Chronological behaved like an indexed
record lookup.

G2.2.1 keeps the old number as `legacy_evidence_items_inspected` and adds
comparable retrieval counters.

## Metric Definitions

`stored_records`

The total number of memory records or reconstructions available to the retrieval
component before narrowing. This is a corpus-size measure, not a work measure.

`records_scanned`

The number of records actually examined after index/envelope narrowing. This is
the primary comparable retrieval-work metric for NowMind and Chronological.

`index_candidates_considered`

The number of records selected by trace metadata or planning-envelope indices
before final relevance filtering.

`records_returned`

The number of records returned from retrieval into current-cycle reconstruction
or planning.

`reconstructions_created`

The number of current `MemoryReconstruction` records supplied to planning.
G2.2.1 benchmark scenarios already construct synthetic reconstructions, so this
tracks the subset selected for the current Now rather than old `NowState`
material.

`effective_evidence_used`

The number of retrieved assumptions actually used by the selected current
`EpistemicPlan`.

`legacy_evidence_items_inspected`

The pre-G2.2.1 planner-side evidence counter retained only for before/after
comparison with the frozen G2.2 baseline.

## Retrieval Boundary

Allowed:

```text
MemoryTrace / MemoryReconstruction
   -> metadata index
   -> selected records
   -> current planning assumptions
```

Forbidden:

```text
old NowState / old TemporalNowState
   -> direct current reasoning input
```

The index may use proposition metadata such as source id, relation type, target
id, and useful composites. It must not inspect trial ids, scenario families,
expected answers, benchmark seeds, evaluator truth, or `ExperimentRecorder`
history.

## Interpretation

G2.2.1 uses corrected comparable retrieval metrics for new claims. The original
669.2 vs 15.2 result remains part of the record because it identified a real
accounting/scaling problem, but final G2.2.1 conclusions should compare
`records_scanned`, `index_candidates_considered`, `records_returned`,
`reconstructions_created`, and `effective_evidence_used`.
