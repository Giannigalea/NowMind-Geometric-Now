# G2.2 Epistemic Geometry Specification

## Core distinction

G2.2 models the difference between:

```text
world truth
what is currently observable
what is remembered
what is hypothesized
```

The system plans over its **epistemic geometry**, not omniscient world truth.

## Visibility

Current observations must be generated through a sensor model.

Cells outside sensor visibility are:

```text
UNKNOWN
```

not free and not blocked.

## Epistemic cell representation

A planning cell may have current evidence such as:

```python
@dataclass(frozen=True)
class EpistemicCell:
    pose: Pose2D
    observed_occupancy: OccupancyState
    observation_confidence: float | None
    memory_candidates: tuple[MemoryReconstruction, ...]
    future_candidates: tuple[FutureHypothesis, ...]
```

Memory/hypotheses remain separate from observed occupancy.

## Information actions

At minimum support either:
- `SCAN`;
- or explicit vantage-point planning.

`SCAN` should:
- consume cost/time;
- reveal cells permitted by sensor rules;
- create new current observations;
- not modify physical world truth.

## Belief is not observation

Do not introduce a field that treats memory-only evidence as observed current occupancy.

Prefer explicit conditional reasoning.

## Planning options

Planner should be able to return options like:

```text
Plan A
known safe
cost 14

Plan B
conditional on remembered corridor open
cost 8
memory confidence 0.74

Plan C
verify corridor first
verification cost 2
then branch
```

## Verification outcome

After an information action:
- obtain fresh observation;
- create fresh TemporalNow;
- invalidate or confirm planning assumptions;
- replan if needed.

## Hidden dynamic change

World changes outside visibility do not automatically alter current epistemic geometry.

They become known only after perception.

## Exploration

If no current location/path is supported:
- preserve uncertainty;
- choose information-gathering/exploration when policy allows;
- do not invent geometry.

## Transparent utility

Use a documented deterministic policy with components such as:
- movement cost;
- scan cost;
- unknown-cell risk;
- memory-confidence risk;
- expected detour.

Keep coefficients configurable and recorded in benchmark config.

## No Bayesian-optimality claim

Unless a formally correct Bayesian model is implemented, do not call the planner Bayes-optimal.

Use terms such as:
- epistemic cost;
- assumption penalty;
- verification value.

## Research invariant

The key invariant is:

```text
information can guide action without being promoted to fact.
```
