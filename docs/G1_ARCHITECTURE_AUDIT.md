# G1 Architecture Audit

## Audit Date

2026-08-22

## Scope

This audit independently inspected the G1 implementation before G1.1 presentation
work. It checks that the G1 runtime still implements a fresh current-state
architecture and that no G2 features have entered the cognitive path.

## Inspected Modules

- `nowmind/core/now_state.py`
- `nowmind/core/cycle.py`
- `nowmind/world/model.py`
- `nowmind/world/events.py`
- `nowmind/perception/adapter.py`
- `nowmind/perception/observation.py`
- `nowmind/geometry/builder.py`
- `nowmind/geometry/inference.py`
- `nowmind/geometry/present_geometry.py`
- `nowmind/geometry/relation.py`
- `nowmind/geometry/validation.py`
- `nowmind/reasoning/query.py`
- `nowmind/reasoning/reasoner.py`
- `nowmind/evaluation/recorder.py`
- `tests/architecture/test_now_firewall.py`
- `tests/unit/test_geometry_relations.py`
- `tests/scenarios/test_g1_scenarios.py`

## Invariant Results

| Invariant | Result | Evidence |
|---|---:|---|
| `NowState` is immutable. | PASS | `NowState` is `@dataclass(frozen=True, slots=True)`. Covered by `tests/architecture/test_now_firewall.py::test_now_state_is_immutable`. |
| `NowState` has no previous/history/memory reference. | PASS | Fields are `now_id`, `cycle_id`, `created_at`, `geometry`. Covered by `test_now_state_has_no_previous_or_history_fields`. |
| Each cycle creates a new `now_id`. | PASS | `NowState.create()` calls `uuid4()` every time. Covered by `test_fresh_now_ids_are_created_for_consecutive_cycles`. |
| `WorldState` is distinct from `NowState`. | PASS | `WorldState` is a persistent environment object; `NowState` is a frozen current cognitive state built from geometry. |
| Perception reads the current world state. | PASS | `PerceptionAdapter.observe(world, cycle_id)` snapshots `world.entities`, `world.relations`, and `world.world_version`. |
| Present Geometry is rebuilt from current observation. | PASS | `PresentGeometryBuilder.build(observation)` accepts only `Observation`; no previous Now parameter exists. |
| No stale relation survives merely because it existed in the previous cycle. | PASS | `MoveRelation` removes incompatible relation families in `WorldState`; next cycle rebuilds geometry from current world. Covered by `test_world_change_rebuilds_geometry_without_stale_relation` and scenario tests. |
| Deterministic reasoner receives only current `NowState` plus current query. | PASS | Public function signature is `answer(now, query)`. Covered by `test_reasoning_and_building_api_have_no_history_argument`. |
| Runtime cognitive packages do not import evaluation-history retrieval. | PASS | AST import inspection covers `world`, `perception`, `geometry`, `core`, and `reasoning`. Covered by `test_runtime_modules_do_not_import_evaluation_history`. |
| `ExperimentRecorder` remains external to cognition. | PASS | Recorder lives under `nowmind/evaluation`; deleting recorder logs does not change current answers. Covered by `test_recorder_external_and_history_deletion_equivalence`. |
| Inferred and observed relations retain distinct provenance. | PASS | `PresentGeometryBuilder` labels direct relations `OBSERVED_NOW`; `inference.py` labels derived relations `INFERRED_NOW`. Covered by unit relation tests. |
| Predictions, memories, identities, and LLM state are absent. | PASS | No runtime modules or dependencies for memory, retrieval, vector storage, prediction, identity, Veto Gate, LLMs, or cloud APIs were found. |

## Weaknesses Found

No G1 architectural invariant was weakened.

Two non-architecture issues were handled during G1.1:

- Pytest's default Windows temp/cache locations could be blocked on the user's
  machine. The test suite now disables pytest cache writes and uses a project-local
  temp directory for the recorder test.
- The actual PCT book PDF was found under `reference/missing_originals/`. It was
  moved to `reference/PCT_Book_Latest.pdf` and `reference/SOURCE_INDEX.md` was
  updated.

## Relevant Tests

- `tests/architecture/test_now_firewall.py`
- `tests/unit/test_geometry_relations.py`
- `tests/scenarios/test_g1_scenarios.py`
- `tests/demo/test_web_demo.py`
- `tests/evaluation/test_g1_suite.py`

## Final Assessment

PASS.

G1 remains a fresh-current-state architecture. The G1.1 demonstrator and evidence
runner are external presentation/evaluation layers and do not introduce memory,
prediction, identity, Veto Gate, LLM integration, or a route from experiment
history back into runtime reasoning.

