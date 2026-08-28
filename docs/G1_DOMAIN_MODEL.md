# G1 Domain Model

## Separation of concerns

The most important design distinction in G1 is:

```text
WORLD PERSISTENCE != COGNITIVE PERSISTENCE
```

The world may remain the same object between cycles.
The cognitive Now may not.

## Suggested data flow

```text
WorldState_t
   |
   | observe()
   v
Observation_t
   |
   | build()
   v
PresentGeometry_t
   |
   | freeze
   v
NowState_t
   |
   | reason(query)
   v
Answer_t
```

## Suggested Python shapes

These are conceptual, not mandatory exact code.

```python
@dataclass(frozen=True)
class Entity:
    entity_id: str
    kind: str
    label: str | None = None
    attributes: Mapping[str, object] = field(default_factory=dict)
```

```python
class Provenance(Enum):
    OBSERVED_NOW = "observed_now"
    INFERRED_NOW = "inferred_now"
```

```python
@dataclass(frozen=True)
class Relation:
    source_id: str
    target_id: str
    relation_type: RelationType
    confidence: float
    provenance: Provenance
    rule_id: str | None = None
    value: float | tuple[float, ...] | None = None
    unit: str | None = None
```

```python
@dataclass(frozen=True)
class PresentGeometry:
    cycle_id: int
    entities: tuple[Entity, ...]
    relations: tuple[Relation, ...]
```

```python
@dataclass(frozen=True)
class NowState:
    now_id: UUID
    cycle_id: int
    created_at: datetime
    geometry: PresentGeometry
```

`NowState` must not include:
- `previous_now`;
- `history`;
- `memories`;
- `conversation`;
- `future_states`;
- `identity_history`.

## Entity IDs

Stable IDs are permitted at the world/perception level so the system can refer to the same external object after it moves.

This is object identity in the environment, not an autobiographical self.

## Inference engine

Prefer a transparent rule engine.

Example:

```text
Rule ID: LEFT_TRANSITIVE

IF:
  LEFT_OF(A,B)
  LEFT_OF(B,C)

THEN:
  LEFT_OF(A,C)
```

Each inferred relation should include:
- rule ID;
- premise references;
- confidence.

## Explanation object

Suggested:

```python
@dataclass(frozen=True)
class ReasoningStep:
    rule_id: str
    premises: tuple[RelationRef, ...]
    conclusion: RelationRef

@dataclass(frozen=True)
class Answer:
    status: TruthStatus
    confidence: float
    explanation: tuple[ReasoningStep, ...]
```

This makes the reasoning auditable and later allows direct comparison with LLM-generated answers.

## Architectural firewall

The runtime package graph should ideally point one way:

```text
world -> perception -> geometry -> core -> reasoning

evaluation may IMPORT core outputs
core/reasoning must NOT IMPORT evaluation history
```

Consider architecture tests that inspect imports or simply keep the `ExperimentRecorder` passed from the outer application shell, never from the reasoning package.
