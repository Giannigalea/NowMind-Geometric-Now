# G2.2 Benchmark Specification

## Purpose

Create benchmark tasks that cannot generally be solved from a full current snapshot because the agent does not receive one.

Memory, observation, and information gathering must matter.

## Shared trial truth

Every system receives the same trial world and event schedule.

Only Oracle receives omniscient truth.

## Trial pairing

Use the same trial IDs/seeds across N/C/R/O so pairwise comparison is possible.

## Minimum scale

Target:
- 5,000 trials if practical;
- minimum 3,000 with justification.

Include at least six difficulty bands.

## History scaling cohorts

Explicit cohorts:
- H0 = 0 historical records
- H10 = 10
- H50 = 50
- H100 = 100
- H500 = 500
- H1000 = 1,000 if practical

Ensure some scenarios include large numbers of irrelevant historical records.

## Core scenario families

Use E1-E24 from the task specification.

## Fair chronological control

The Chronological planner:
- may index records;
- may keep per-entity temporal indices;
- may use the same A* implementation;
- may use equivalent confidence/risk policy;
- must not be forced into naive linear scans unless that is its chosen documented implementation.

The benchmark should test representational consequences, not poor coding.

## Key comparison

The most informative comparison is not simply:

```text
Who reaches the goal?
```

Also compare:

```text
How much historical information is inspected?
How often is uncertain historical information promoted to current certainty?
How often is verification chosen appropriately?
How does performance scale with history length?
```

## Ceiling detection

If N and C remain tied across accuracy and scaling, report that explicitly.

Do not create arbitrary new tasks solely to separate them.
