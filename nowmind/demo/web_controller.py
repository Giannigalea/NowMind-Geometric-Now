from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any
from uuid import uuid4

from nowmind.core.cycle import CognitiveCycleRunner
from nowmind.core.now_state import NowState
from nowmind.evaluation.recorder import ExperimentRecorder
from nowmind.evaluation.serialization import (
    query_display,
    serialize_cycle,
    serialize_answer,
    serialize_issue,
    serialize_now,
    serialize_query,
    serialize_relation,
    serialize_world,
    summarize_relations,
)
from nowmind.evaluation.g2_3_benchmark import build_hero_comparison
from nowmind.epistemic import (
    EpistemicActionExecutionResult,
    EpistemicActionExecutor,
    EpistemicCycleRunner,
    EpistemicCycleState,
    EpistemicPlan,
    EpistemicPolicyConfig,
    EpistemicRecoveryState,
    NowMindEpistemicPlanner,
    SensorConfig,
    retrieve_relevant_reconstructions,
)
from nowmind.geometry.relation import RelationType
from nowmind.reasoning.query import Answer, Query
from nowmind.reasoning.reasoner import answer as runtime_answer
from nowmind.reasoning.query import TruthStatus
from nowmind.temporal.future import FutureHypothesis
from nowmind.temporal.memory import MemoryReconstruction, MemoryStore, MemoryTrace, RetrievalCue
from nowmind.temporal.now_state import TemporalNowState
from nowmind.temporal.proposition import Proposition
from nowmind.temporal.query import TemporalAnswer, TemporalIntent, TemporalQuery
from nowmind.temporal.reasoner import answer_temporal
from nowmind.temporal.source import TemporalSource
from nowmind.temporal.cycle import TemporalCycleRunner
from nowmind.spatial import (
    AStarPlanner,
    ActionExecutionResult,
    ActionExecutor,
    ActionProposal,
    OccupancyState,
    Plan,
    Pose2D,
    SpatialCycleRunner,
    SpatialCycleState,
    SpatialEntity,
    SpatialWorldState,
)
from nowmind.world.events import AddEntity, MoveRelation, RemoveRelation, SetRelation
from nowmind.world.model import WorldState


@dataclass(frozen=True, slots=True)
class QueryOption:
    query_id: str
    label: str
    query: Query | TemporalQuery


class WebDemoController:
    """Stateful local demonstrator shell around the existing G1 runtime."""

    def __init__(self) -> None:
        self.recorder = ExperimentRecorder()
        self.external_history: list[dict[str, Any]] = []
        self.last_history_firewall_message: str | None = None
        self.load_demo("fresh_now")

    def load_demo(self, demo_id: str) -> dict[str, Any]:
        self.demo_id = demo_id
        self.runner = CognitiveCycleRunner()
        self.temporal_runner: TemporalCycleRunner | None = None
        self.recorder.delete_logs()
        self.external_history.clear()
        self.last_history_firewall_message = None
        self.current_now: NowState | None = None
        self.current_answer: Answer | None = None
        self.current_temporal_now: TemporalNowState | None = None
        self.current_temporal_answer: TemporalAnswer | None = None
        self.world = WorldState()

        if self._is_full_g_demo(demo_id):
            return self._load_full_g_demo()
        if self._is_g2_3_demo(demo_id):
            return self._load_g2_3_demo(demo_id)
        if self._is_g2_2_demo(demo_id):
            return self._load_g2_2_demo(demo_id)
        if self._is_g2_1_demo(demo_id):
            return self._load_g2_1_demo(demo_id)
        if self._is_g2_demo(demo_id):
            return self._load_g2_demo(demo_id)

        if demo_id == "fresh_now":
            self.world.apply(AddEntity("red_cube", "cube", "red cube"))
            self.world.apply(AddEntity("blue_cube", "cube", "blue cube"))
            self.world.apply(MoveRelation("red_cube", "blue_cube", RelationType.LEFT_OF))
            self.query_options = (
                QueryOption(
                    "red_left_blue",
                    "red_cube LEFT_OF blue_cube?",
                    Query.relation("red_cube", "blue_cube", RelationType.LEFT_OF),
                ),
                QueryOption(
                    "red_right_blue",
                    "red_cube RIGHT_OF blue_cube?",
                    Query.relation("red_cube", "blue_cube", RelationType.RIGHT_OF),
                ),
                QueryOption(
                    "blue_left_red",
                    "blue_cube LEFT_OF red_cube?",
                    Query.relation("blue_cube", "red_cube", RelationType.LEFT_OF),
                ),
            )
            self.active_query_id = "red_left_blue"
        elif demo_id == "inference":
            for entity_id in ("a", "b", "c"):
                self.world.apply(AddEntity(entity_id, "object", entity_id.upper()))
            self.world.apply(SetRelation("a", "b", RelationType.LEFT_OF))
            self.world.apply(SetRelation("b", "c", RelationType.LEFT_OF))
            self.query_options = (
                QueryOption(
                    "a_left_c",
                    "A LEFT_OF C?",
                    Query.explain("a", RelationType.LEFT_OF, "c"),
                ),
            )
            self.active_query_id = "a_left_c"
        elif demo_id == "containment":
            for entity_id, kind in (
                ("key", "object"),
                ("box", "container"),
                ("cabinet", "container"),
            ):
                self.world.apply(AddEntity(entity_id, kind, entity_id))
            self.world.apply(SetRelation("key", "box", RelationType.INSIDE))
            self.world.apply(SetRelation("box", "cabinet", RelationType.INSIDE))
            self.query_options = (
                QueryOption(
                    "key_inside_cabinet",
                    "key INSIDE cabinet?",
                    Query.explain("key", RelationType.INSIDE, "cabinet"),
                ),
            )
            self.active_query_id = "key_inside_cabinet"
        elif demo_id == "contradiction":
            self.world.apply(AddEntity("red_cube", "cube", "red cube"))
            self.world.apply(AddEntity("blue_cube", "cube", "blue cube"))
            self.world.apply(SetRelation("red_cube", "blue_cube", RelationType.LEFT_OF))
            self.world.apply(SetRelation("red_cube", "blue_cube", RelationType.RIGHT_OF))
            self.query_options = (
                QueryOption(
                    "contradictory_left",
                    "red_cube LEFT_OF blue_cube?",
                    Query.relation("red_cube", "blue_cube", RelationType.LEFT_OF),
                ),
            )
            self.active_query_id = "contradictory_left"
        else:
            raise ValueError(f"Unknown demo_id: {demo_id}")

        return self.to_dict()

    def run_cycle(self) -> dict[str, Any]:
        if self._is_full_g_demo(self.demo_id):
            return self.to_dict()
        if self._is_g2_3_demo(self.demo_id):
            self.g2_3_comparison = build_hero_comparison()
            return self.to_dict()
        if self._is_g2_2_demo(self.demo_id):
            return self._run_g2_2_cycle()
        if self._is_g2_1_demo(self.demo_id):
            return self._run_g2_1_cycle()
        if self._is_g2_demo(self.demo_id):
            return self._run_g2_cycle()
        self.current_now = self.runner.run(self.world)
        self.current_answer = runtime_answer(self.current_now, self.active_query)
        self.recorder.record(self.current_now, self.active_query, self.current_answer)
        self.external_history.append(
            {
                "cycle_id": self.current_now.cycle_id,
                "now_id": str(self.current_now.now_id),
                "now": serialize_now(self.current_now),
                "relations": summarize_relations(self.current_now),
                "query": query_display(self.active_query),
                "answer": self.current_answer.status.value,
                "cycle": serialize_cycle(
                    self.current_now,
                    self.active_query,
                    self.current_answer,
                ),
            }
        )
        return self.to_dict()

    def apply_demo_world_event(self) -> dict[str, Any]:
        if self._is_full_g_demo(self.demo_id):
            return self.to_dict()
        if self._is_g2_3_demo(self.demo_id):
            self.g2_3_comparison = build_hero_comparison()
            return self.to_dict()
        if self._is_g2_2_demo(self.demo_id):
            return self.g2_2_apply_world_event()
        if self._is_g2_1_demo(self.demo_id):
            return self._apply_g2_1_world_event()
        if self._is_g2_demo(self.demo_id):
            return self._apply_g2_world_event()
        if self.demo_id == "fresh_now":
            return self.apply_demo_a_move()
        if self.demo_id == "inference":
            return self.apply_demo_b_event()
        if self.demo_id == "containment":
            return self.apply_demo_c_event()
        if self.demo_id == "contradiction":
            return self.apply_demo_d_event()
        raise ValueError("No world event is available for this demo.")

    def apply_demo_a_move(self) -> dict[str, Any]:
        if self.demo_id != "fresh_now":
            raise ValueError("The move event is only available for Demo A.")
        current_relation = self._demo_a_world_relation()
        next_relation = (
            RelationType.LEFT_OF
            if current_relation is RelationType.RIGHT_OF
            else RelationType.RIGHT_OF
        )
        self.world.apply(MoveRelation("red_cube", "blue_cube", next_relation))
        self.active_query_id = (
            "red_right_blue"
            if next_relation is RelationType.RIGHT_OF
            else "red_left_blue"
        )
        self.last_history_firewall_message = None
        return self.to_dict()

    def apply_demo_b_event(self) -> dict[str, Any]:
        if self.demo_id != "inference":
            raise ValueError("The inference event is only available for Demo B.")
        if self._demo_b_bridge_present():
            self.world.apply(RemoveRelation("b", "c", RelationType.LEFT_OF))
        else:
            self.world.apply(SetRelation("b", "c", RelationType.LEFT_OF))
        self.active_query_id = "a_left_c"
        self.last_history_firewall_message = None
        return self.to_dict()

    def apply_demo_c_event(self) -> dict[str, Any]:
        if self.demo_id != "containment":
            raise ValueError("The containment event is only available for Demo C.")
        if self._demo_c_bridge_present():
            self.world.apply(RemoveRelation("box", "cabinet", RelationType.INSIDE))
        else:
            self.world.apply(SetRelation("box", "cabinet", RelationType.INSIDE))
        self.active_query_id = "key_inside_cabinet"
        self.last_history_firewall_message = None
        return self.to_dict()

    def apply_demo_d_event(self) -> dict[str, Any]:
        if self.demo_id != "contradiction":
            raise ValueError("The contradiction event is only available for Demo D.")
        if self._demo_d_contradiction_present():
            self.world.apply(RemoveRelation("red_cube", "blue_cube", RelationType.RIGHT_OF))
        else:
            self.world.apply(SetRelation("red_cube", "blue_cube", RelationType.RIGHT_OF))
        self.active_query_id = "contradictory_left"
        self.last_history_firewall_message = None
        return self.to_dict()

    def set_query(self, query_id: str) -> dict[str, Any]:
        if query_id not in {option.query_id for option in self.query_options}:
            raise ValueError(f"Unknown query_id for current demo: {query_id}")
        self.active_query_id = query_id
        if self._is_g2_demo(self.demo_id):
            if self.current_temporal_now is not None:
                self.current_temporal_answer = answer_temporal(
                    self.current_temporal_now,
                    self.active_temporal_query,
                )
            return self.to_dict()
        if self.current_now is not None:
            self.current_answer = runtime_answer(self.current_now, self.active_query)
        return self.to_dict()

    def delete_history_and_rerun(self) -> dict[str, Any]:
        if self._is_full_g_demo(self.demo_id):
            self.external_history.clear()
            self.recorder.delete_logs()
            self.last_history_firewall_message = (
                "Full-G reviewer mode is a local package view. It reads no previous "
                "NowState and makes no cloud or model calls."
            )
            return self.to_dict()
        if self._is_g2_3_demo(self.demo_id):
            self.external_history.clear()
            self.recorder.delete_logs()
            self.last_history_firewall_message = (
                "Researcher history was deleted. G2.3 model comparison still "
                "uses only explicit representation payloads built from the current "
                "admissible fact set."
            )
            return self.to_dict()
        if self._is_g2_2_demo(self.demo_id):
            self.external_history.clear()
            self.recorder.delete_logs()
            self.last_history_firewall_message = (
                "Researcher history was deleted. G2.2 still receives only fresh "
                "epistemic observation plus explicit memory/hypothesis channels."
            )
            return self.to_dict()
        if self._is_g2_1_demo(self.demo_id):
            self.external_history.clear()
            self.recorder.delete_logs()
            self.last_history_firewall_message = (
                "Researcher history was deleted. G2.1 planning still uses only the "
                "fresh spatial observation plus explicit memory assumptions."
            )
            return self.to_dict()
        if self._is_g2_demo(self.demo_id):
            if self.current_temporal_now is None:
                raise ValueError("Run a temporal cycle before deleting history.")
            before = self.current_temporal_answer
            self.external_history.clear()
            self.recorder.delete_logs()
            self.current_temporal_answer = answer_temporal(
                self.current_temporal_now,
                self.active_temporal_query,
            )
            unchanged = (
                before is not None
                and before.status is self.current_temporal_answer.status
                and before.confidence == self.current_temporal_answer.confidence
            )
            self.last_history_firewall_message = (
                "Researcher history was deleted. Temporal reasoning is unchanged "
                "because memory comes from MemoryStore traces, not ExperimentRecorder logs."
                if unchanged
                else "History was deleted, but the temporal answer changed. Investigate immediately."
            )
            return self.to_dict()
        if self.current_now is None:
            raise ValueError("Run a cycle before deleting history.")
        before = self.current_answer
        self.recorder.delete_logs()
        self.external_history.clear()
        self.current_answer = runtime_answer(self.current_now, self.active_query)
        unchanged = (
            before is not None
            and before.status is self.current_answer.status
            and before.confidence == self.current_answer.confidence
        )
        self.last_history_firewall_message = (
            "Current reasoning is unchanged because external experiment history "
            "is not a cognitive input."
            if unchanged
            else "History was deleted, but the current answer changed. Investigate immediately."
        )
        return self.to_dict()

    @property
    def active_query(self) -> Query:
        for option in self.query_options:
            if option.query_id == self.active_query_id:
                if isinstance(option.query, Query):
                    return option.query
        raise RuntimeError("active_query_id is not in query_options")

    @property
    def active_temporal_query(self) -> TemporalQuery:
        for option in self.query_options:
            if option.query_id == self.active_query_id:
                if isinstance(option.query, TemporalQuery):
                    return option.query
        raise RuntimeError("active_query_id is not a temporal query")

    def to_dict(self) -> dict[str, Any]:
        if self._is_full_g_demo(self.demo_id):
            return self._full_g_to_dict()
        if self._is_g2_3_demo(self.demo_id):
            return self._g2_3_to_dict()
        if self._is_g2_2_demo(self.demo_id):
            return self._g2_2_to_dict()
        if self._is_g2_1_demo(self.demo_id):
            return self._g2_1_to_dict()
        if self._is_g2_demo(self.demo_id):
            return self._g2_to_dict()
        stale_present = None
        world_relation = self._demo_a_world_relation()
        if self.current_now is not None:
            stale_present = (
                self.current_now.geometry.find_relation(
                    "red_cube",
                    "blue_cube",
                    RelationType.LEFT_OF,
                )
                is not None
            )
        return {
            "schema": "nowmind.g1.web_state.v1",
            "demo_id": self.demo_id,
            "disclaimer": (
                "NowMind G1 is a computational research architecture inspired by "
                "Present Consciousness Theory. Its behavior tests representation "
                "and reasoning properties; it does not demonstrate or claim "
                "phenomenal consciousness."
            ),
            "world": serialize_world(self.world),
            "current_now": serialize_now(self.current_now) if self.current_now else None,
            "active_query": serialize_query(self.active_query),
            "current_answer": (
                serialize_answer(self.current_answer) if self.current_answer else None
            ),
            "query_options": [
                {
                    "query_id": option.query_id,
                    "label": option.label,
                    "query": serialize_query(option.query),
                }
                for option in self.query_options
            ],
            "external_history": list(self.external_history),
            "recorder_record_count": len(self.recorder.history),
            "history_firewall_message": self.last_history_firewall_message,
            "stale_red_left_blue_present": stale_present,
            "world_changed_since_now": (
                self.current_now is not None
                and self.world.world_version != self.current_now.geometry.world_version
            ),
            "world_event_available": self.demo_id
            in {"fresh_now", "inference", "containment", "contradiction"},
            "move_event_label": self._move_event_label(world_relation),
            "world_event_help": self._world_event_help(),
            "success_badges": self._success_badges(stale_present),
        }

    def _is_full_g_demo(self, demo_id: str) -> bool:
        return demo_id == "full_g_reviewer"

    def _is_g2_demo(self, demo_id: str) -> bool:
        return (
            demo_id.startswith("g2_")
            and not demo_id.startswith("g2_3")
            and not demo_id.startswith("g2_1")
            and not demo_id.startswith("g2_2")
        )

    def _is_g2_3_demo(self, demo_id: str) -> bool:
        return demo_id.startswith("g2_3")

    def _is_g2_1_demo(self, demo_id: str) -> bool:
        return demo_id.startswith("g2_1")

    def _is_g2_2_demo(self, demo_id: str) -> bool:
        return demo_id.startswith("g2_2")

    def _load_full_g_demo(self) -> dict[str, Any]:
        self.demo_id = "full_g_reviewer"
        self.query_options = (
            QueryOption(
                "full_g_review",
                "Review Full-G milestone",
                TemporalQuery.relation(
                    "full_g",
                    RelationType.CONTAINS,
                    "results_package",
                    TemporalIntent.NOW,
                ),
            ),
        )
        self.active_query_id = "full_g_review"
        return self.to_dict()

    def _full_g_to_dict(self) -> dict[str, Any]:
        sections = [
            {
                "title": "Present Geometry",
                "scenario": "A world relation changes; the current Now updates only after a fresh cycle.",
                "state": "WorldState persists, NowState is immutable and rebuilt per cycle.",
                "source_labels": "OBSERVED_NOW and INFERRED_NOW",
                "changed": "Previous Nows stay in external researcher history only.",
                "answer": "G1 stale-state contamination = 0.",
                "why": "This is the base history firewall.",
                "metric": "G1 evidence suite: query accuracy 1.0; stale contamination 0.",
            },
            {
                "title": "Temporal Source Separation",
                "scenario": "Present location, reconstructed past, and possible future coexist without collapsing.",
                "state": "TemporalNowState has present, memory reconstruction, and future hypothesis channels.",
                "source_labels": "OBSERVED_NOW, RECONSTRUCTED_MEMORY, HYPOTHETICAL_FUTURE",
                "changed": "Memory can answer past queries, but not masquerade as current observation.",
                "answer": "NowMind and Chronological both reached 1.0; NaivePersistentState reached 0.332.",
                "why": "Source separation works, but a competent chronological control can also do it.",
                "metric": "G2 stale memory as current: NowMind 0, Naive 502.",
            },
            {
                "title": "Possibility Geometry",
                "scenario": "A planner draws candidate future paths, then executes only one real action.",
                "state": "HypotheticalGeometry and Plan are present hypotheses, not world truth.",
                "source_labels": "Solid observed route, dashed memory, dotted possible future",
                "changed": "After action, the system observes again and builds a fresh TemporalNowState.",
                "answer": "NowMind goal reached rate about 0.867; Reactive and Chronological often matched.",
                "why": "The possibility machinery works, but this stage did not isolate a NowMind-specific advantage.",
                "metric": "G2.1 goal reached: N 0.867, C 0.867, R 0.867.",
            },
            {
                "title": "Epistemic Recovery",
                "scenario": "Fog hides a moved target or obstacle; SCAN creates new evidence before replanning.",
                "state": "Unknown cells remain unknown until observed; stale assumptions can be disconfirmed.",
                "source_labels": "UNKNOWN, OBSERVED_NOW, RECONSTRUCTED_MEMORY, HYPOTHETICAL_FUTURE",
                "changed": "G2.2.1 preserves memory traces while invalidating current assumptions.",
                "answer": "Holdout NowMind goal reached 0.9455; Reactive 0.7085.",
                "why": "Recovery improved substantially, while N and C stayed tied under fair retrieval.",
                "metric": "Hidden target recovery 1.0; hidden obstacle recovery about 0.849.",
            },
            {
                "title": "Real-Model Comparison",
                "scenario": "The same frozen task facts are serialized as NowMind structured and chronological prompts.",
                "state": "Model output is a proposal, then a symbolic validator produces the final score.",
                "source_labels": "model proposal, validator decision, evaluator truth hidden",
                "changed": "Regime-B budget enforcement was corrected without changing the benchmark.",
                "answer": "qwen3:0.6b did not show a NowMind advantage.",
                "why": "The model evidence is negative for N>C and limited to one very small local model.",
                "metric": "Regime A C 8/N 0/T 242; corrected Regime B C 0/N 0/T 250.",
            },
            {
                "title": "Full-G Results",
                "scenario": "The package freezes G1 through G2.3.4 for local reviewer inspection.",
                "state": "Docs, artifacts, benchmark tables, and reviewer demo are local files.",
                "source_labels": "frozen artifacts, claims boundary, negative results",
                "changed": "OpenRouter work is frozen; no paid or cloud calls are part of review.",
                "answer": "No exact-free OpenRouter model passed calibration-valid replication.",
                "why": "This makes the milestone honest: strong invariants, real negative results, clear next questions.",
                "metric": "G2.3.4 calibration-valid exact-free models: 0.",
            },
        ]
        return {
            "schema": "nowmind.full_g.web_state.v1",
            "demo_id": self.demo_id,
            "disclaimer": (
                "Full-G reviewer mode is a local reproducibility and results package. "
                "It makes no cloud calls and proves no consciousness, sentience, or general model superiority."
            ),
            "world": serialize_world(self.world),
            "current_now": None,
            "current_answer": None,
            "temporal_now": None,
            "temporal_answer": None,
            "active_query": self.active_temporal_query.to_dict(),
            "query_options": [
                {
                    "query_id": option.query_id,
                    "label": option.label,
                    "query": option.query.to_dict()
                    if isinstance(option.query, TemporalQuery)
                    else serialize_query(option.query),
                }
                for option in self.query_options
            ],
            "external_history": list(self.external_history),
            "recorder_record_count": len(self.recorder.history),
            "history_firewall_message": self.last_history_firewall_message,
            "world_changed_since_now": False,
            "world_event_available": False,
            "move_event_label": "Reviewer mode is read-only",
            "world_event_help": "Use the sections in the main panel; no cloud or model call is made.",
            "success_badges": [
                {"label": "Full-G package", "status": "FROZEN", "tone": "pass"},
                {"label": "Cloud calls", "status": "OFF", "tone": "pass"},
                {"label": "Model claim", "status": "NEGATIVE", "tone": "warn"},
            ],
            "full_g": {
                "sections": sections,
                "documents": [
                    "docs/FULL_G_MILESTONE_FREEZE.md",
                    "docs/FULL_G_RESULTS_SUMMARY.md",
                    "docs/FULL_G_CLAIMS_AND_NONCLAIMS.md",
                    "docs/FULL_G_NEGATIVE_RESULTS.md",
                    "REPRODUCE_FULL_G.md",
                ],
                "nonclaims": [
                    "consciousness",
                    "sentience",
                    "phenomenal experience",
                    "general model superiority",
                    "quantum consciousness",
                ],
                "real_model_result": (
                    "qwen3:0.6b did not show a NowMind accuracy advantage over chronology."
                ),
            },
        }

    def _load_g2_3_demo(self, demo_id: str) -> dict[str, Any]:
        if demo_id != "g2_3_model_comparison":
            raise ValueError(f"Unknown G2.3 demo_id: {demo_id}")
        self.demo_id = demo_id
        self.g2_3_comparison = build_hero_comparison()
        self.query_options = (
            QueryOption(
                "g2_3_compare",
                "Compare model representations",
                TemporalQuery.relation(
                    "model",
                    RelationType.REACHABLE,
                    "answer",
                    TemporalIntent.POSSIBLE_FUTURE,
                ),
            ),
        )
        self.active_query_id = "g2_3_compare"
        return self.to_dict()

    def _g2_3_to_dict(self) -> dict[str, Any]:
        return {
            "schema": "nowmind.g2_3.web_state.v1",
            "demo_id": self.demo_id,
            "disclaimer": (
                "NowMind G2.3 compares representation formats given the same "
                "replaceable local model faculty. It does not implement identity, "
                "dreaming, or a Veto Gate."
            ),
            "world": serialize_world(self.world),
            "current_now": None,
            "current_answer": None,
            "temporal_now": None,
            "temporal_answer": None,
            "active_query": self.active_temporal_query.to_dict(),
            "query_options": [
                {
                    "query_id": option.query_id,
                    "label": option.label,
                    "query": option.query.to_dict()
                    if isinstance(option.query, TemporalQuery)
                    else serialize_query(option.query),
                }
                for option in self.query_options
            ],
            "external_history": list(self.external_history),
            "recorder_record_count": len(self.recorder.history),
            "history_firewall_message": self.last_history_firewall_message,
            "world_changed_since_now": False,
            "world_event_available": False,
            "move_event_label": "Model comparison is prebuilt",
            "world_event_help": (
                "Run cycle refreshes the same side-by-side G2.3 comparison payload."
            ),
            "success_badges": self._g2_3_success_badges(),
            "g2_3_comparison": self.g2_3_comparison,
        }

    def _g2_3_success_badges(self) -> list[dict[str, str]]:
        selected = self.g2_3_comparison["model_manifest"]["selected"]
        badges = [
            {"label": "G2.3 model comparison", "status": "ACTIVE", "tone": "pass"},
            {"label": "Backend", "status": str(selected["backend"]).upper(), "tone": "warn" if selected["backend"] == "mock" else "pass"},
            {"label": "Evaluator truth", "status": "HIDDEN", "tone": "pass"},
        ]
        if self.last_history_firewall_message:
            badges.append({"label": "History boundary", "status": "PASS", "tone": "pass"})
        return badges

    def _load_g2_2_demo(self, demo_id: str) -> dict[str, Any]:
        self.demo_id = demo_id
        self.epistemic_runner = EpistemicCycleRunner(
            sensor_config=SensorConfig(
                visibility_radius=10,
                scan_radius_bonus=3,
                scan_cost=1.0,
                line_of_sight_blocks=False,
            )
        )
        self.epistemic_planner = NowMindEpistemicPlanner(EpistemicPolicyConfig(scan_cost=1.0))
        self.epistemic_executor = EpistemicActionExecutor()
        self.epistemic_state: EpistemicCycleState | None = None
        self.g2_2_plan: EpistemicPlan | None = None
        self.g2_2_last_result: EpistemicActionExecutionResult | None = None
        self.g2_2_memory_reconstructions: tuple[MemoryReconstruction, ...] = ()
        self.g2_2_future_hypotheses: tuple[FutureHypothesis, ...] = ()
        self.g2_2_recovery = EpistemicRecoveryState()
        self.g2_2_note = ""
        self.g2_2_event_note = ""
        self.g2_2_scan_next = False
        self.g2_2_history_record_count = 50
        self.spatial_world = SpatialWorldState(
            7,
            5,
            [
                SpatialEntity("agent", "agent", Pose2D(0, 2), "Agent"),
                SpatialEntity("target", "target", Pose2D(6, 2), "Target"),
            ],
        )
        if demo_id == "g2_2_verify_false":
            for pose in (Pose2D(2, 2), Pose2D(3, 2), Pose2D(4, 2)):
                self.spatial_world.hide_cell(pose)
            self.g2_2_note = (
                "G2.2 verify-first: fog hides the shortcut; memory says it was clear. "
                "NowMind scans before trusting it, sees blockage, and replans safely."
            )
            self.spatial_world.set_obstacle(Pose2D(3, 2), "hidden_blocked_shortcut")
            self.spatial_world.hide_cell(Pose2D(3, 2))
            self.g2_2_memory_reconstructions = (
                self._g2_1_memory_cell(Pose2D(2, 2), OccupancyState.FREE, "stale_free_epistemic"),
                self._g2_1_memory_cell(Pose2D(3, 2), OccupancyState.FREE, "stale_free_epistemic"),
                self._g2_1_memory_cell(Pose2D(4, 2), OccupancyState.FREE, "stale_free_epistemic"),
            )
        elif demo_id == "g2_2_verify_correct":
            for pose in (Pose2D(2, 2), Pose2D(3, 2), Pose2D(4, 2)):
                self.spatial_world.hide_cell(pose)
            self.g2_2_note = (
                "G2.2 memory-correct: fog hides the shortcut; memory says it was clear. "
                "Verification reveals the shortcut is open, then the plan uses it."
            )
            self.g2_2_memory_reconstructions = (
                self._g2_1_memory_cell(Pose2D(2, 2), OccupancyState.FREE, "accurate_free_epistemic"),
                self._g2_1_memory_cell(Pose2D(3, 2), OccupancyState.FREE, "accurate_free_epistemic"),
                self._g2_1_memory_cell(Pose2D(4, 2), OccupancyState.FREE, "accurate_free_epistemic"),
            )
        elif demo_id == "g2_2_1_stale_target_recovery":
            self.spatial_world.hide_cell(Pose2D(6, 2))
            self.g2_2_note = (
                "G2.2.1 R1: memory says the target was at A, but A is currently visible "
                "and empty. The current assumption is disconfirmed, historical memory is "
                "preserved, and SCAN/frontier search reacquires the hidden target."
            )
            self.g2_2_memory_reconstructions = (
                self._g2_2_memory_target(Pose2D(2, 2), "stale_target_location"),
            )
        elif demo_id == "g2_2_1_hidden_obstacle_recovery":
            for pose in (Pose2D(2, 2), Pose2D(3, 2), Pose2D(4, 2)):
                self.spatial_world.hide_cell(pose)
            self.spatial_world.set_obstacle(Pose2D(3, 2), "moved_hidden_obstacle")
            self.spatial_world.hide_cell(Pose2D(3, 2))
            self.g2_2_note = (
                "G2.2.1 R2: an obstacle has moved under fog. The first Now does not know. "
                "SCAN reveals the conflict, invalidates the old free-cell assumption, and "
                "the next plan avoids the blocked cell."
            )
            self.g2_2_memory_reconstructions = (
                self._g2_1_memory_cell(Pose2D(2, 2), OccupancyState.FREE, "before_move_free"),
                self._g2_1_memory_cell(Pose2D(3, 2), OccupancyState.FREE, "before_move_free"),
                self._g2_1_memory_cell(Pose2D(4, 2), OccupancyState.FREE, "before_move_free"),
            )
        else:
            raise ValueError(f"Unknown G2.2 demo_id: {demo_id}")
        self.g2_2_future_hypotheses = (
            FutureHypothesis.create(
                1,
                Proposition("target", RelationType.AT, Pose2D(6, 1).cell_id()),
                0.62,
                generator_id="g2_2_demo_future_overlay",
                metadata={"pose": Pose2D(6, 1).to_dict(), "demo": demo_id},
            ),
        )
        self.query_options = (
            QueryOption(
                "g2_2_plan",
                "Plan under partial observation",
                TemporalQuery.relation(
                    "agent",
                    RelationType.REACHABLE,
                    "target",
                    TemporalIntent.POSSIBLE_FUTURE,
                ),
            ),
        )
        self.active_query_id = "g2_2_plan"
        return self.to_dict()

    def _run_g2_2_cycle(self) -> dict[str, Any]:
        self.epistemic_state = self.epistemic_runner.run(
            self.spatial_world,
            reconstructed_memories=self.g2_2_memory_reconstructions,
            future_hypotheses=self.g2_2_future_hypotheses,
            scan=self.g2_2_scan_next,
        )
        self.g2_2_scan_next = False
        recovery_update = self.g2_2_recovery.update_from_geometry(
            self.epistemic_state.epistemic_geometry,
            executed_steps=len(self.external_history),
        )
        retrieval = retrieve_relevant_reconstructions(
            self.epistemic_state.epistemic_geometry,
            self.g2_2_memory_reconstructions,
            disconfirmed_target_poses=self.g2_2_recovery.disconfirmed_target_poses,
            invalidated_poses=self.g2_2_recovery.invalidated_poses,
        )
        self.g2_2_plan = self.epistemic_planner.plan(
            self.epistemic_state.epistemic_geometry,
            memory_reconstructions=retrieval.reconstructions,
            future_hypotheses=self.epistemic_state.temporal_now.future_hypotheses,
            history_record_count=self.g2_2_history_record_count,
            disconfirmed_target_poses=self.g2_2_recovery.disconfirmed_target_poses,
            invalidated_poses=self.g2_2_recovery.invalidated_poses,
        )
        if recovery_update.newly_disconfirmed_targets:
            self.g2_2_event_note = "Current observation falsified the remembered target location."
        if recovery_update.newly_invalidated_cells:
            self.g2_2_event_note = "Current observation invalidated a remembered free-cell assumption."
        if recovery_update.target_reacquired:
            self.g2_2_event_note = "Target reacquired as a new observed-now fact."
        self.external_history.append(
            {
                "cycle_id": self.epistemic_state.temporal_now.cycle_id,
                "now_id": str(self.epistemic_state.temporal_now.now_id),
                "agent_pose": self.epistemic_state.epistemic_geometry.agent_pose.to_dict(),
                "target_pose": (
                    self.epistemic_state.epistemic_geometry.target_pose.to_dict()
                    if self.epistemic_state.epistemic_geometry.target_pose
                    else None
                ),
                "plan_valid": self.g2_2_plan.valid,
                "plan_steps": len(self.g2_2_plan.steps),
                "conditional": self.g2_2_plan.conditional,
                "decision_type": self.g2_2_plan.decision_type.value,
                "now_type": "scan" if self.epistemic_state.epistemic_geometry.scan_used else "local",
                "recovery": recovery_update.to_dict(),
                "records_scanned": retrieval.metrics.records_scanned,
            }
        )
        return self.to_dict()

    def g2_2_execute_one_step(self) -> dict[str, Any]:
        if self.epistemic_state is None or self.g2_2_plan is None:
            self._run_g2_2_cycle()
        if self.g2_2_plan is None or not self.g2_2_plan.valid or self.g2_2_plan.first_step() is None:
            self.g2_2_event_note = "No valid epistemic plan is available to execute."
            return self.to_dict()
        self.g2_2_last_result = self.epistemic_executor.execute(
            self.spatial_world,
            self.g2_2_plan,
        )
        self.g2_2_scan_next = self.g2_2_last_result.information_action
        self.g2_2_event_note = (
            "SCAN gathered information and rebuilt a fresh Now."
            if self.g2_2_last_result.information_action
            else "Executed one movement step in the external world; rebuilding fresh Now."
        )
        return self._run_g2_2_cycle()

    def g2_2_run_closed_loop(self) -> dict[str, Any]:
        for _ in range(12):
            if self.epistemic_state is None or self.g2_2_plan is None:
                self._run_g2_2_cycle()
            agent_pose = self.spatial_world.entity("agent").pose
            target_pose = self.spatial_world.entity("target").pose
            if agent_pose == target_pose:
                self.g2_2_event_note = "Goal reached without collision."
                break
            before_cycle = (
                self.epistemic_state.temporal_now.cycle_id if self.epistemic_state else -1
            )
            self.g2_2_execute_one_step()
            if self.epistemic_state is None or self.epistemic_state.temporal_now.cycle_id == before_cycle:
                break
        return self.to_dict()

    def g2_2_apply_world_event(self) -> dict[str, Any]:
        if self.demo_id == "g2_2_verify_false":
            self._load_g2_2_demo("g2_2_verify_correct")
            self.g2_2_event_note = "Shortcut truth changed for demo: memory is now correct."
            return self.to_dict()
        if self.demo_id == "g2_2_verify_correct":
            self._load_g2_2_demo("g2_2_verify_false")
            self.g2_2_event_note = "Shortcut truth changed for demo: memory is now false."
            return self.to_dict()
        self.g2_2_event_note = "This recovery demo has no manual world toggle."
        return self.to_dict()

    def _g2_2_to_dict(self) -> dict[str, Any]:
        geometry = self.epistemic_state.epistemic_geometry if self.epistemic_state else None
        temporal_now = self.epistemic_state.temporal_now if self.epistemic_state else None
        return {
            "schema": "nowmind.g2_2.web_state.v1",
            "demo_id": self.demo_id,
            "disclaimer": (
                "NowMind G2.2 is a deterministic epistemic-planning research demo. "
                "It does not demonstrate or claim phenomenal consciousness."
            ),
            "world": self.spatial_world.to_dict(),
            "epistemic_now": geometry.to_dict() if geometry else None,
            "spatial_now": geometry.to_dict() if geometry else None,
            "temporal_now": (
                {
                    "cycle_id": temporal_now.cycle_id,
                    "now_id": str(temporal_now.now_id),
                    "created_at": temporal_now.created_at.isoformat(),
                    "reconstructed_memories": [
                        memory.to_dict() for memory in temporal_now.reconstructed_memories
                    ],
                    "future_hypotheses": [
                        hypothesis.to_dict() for hypothesis in temporal_now.future_hypotheses
                    ],
                }
                if temporal_now
                else None
            ),
            "current_now": None,
            "current_answer": None,
            "temporal_answer": None,
            "active_query": self.active_temporal_query.to_dict(),
            "query_options": [
                {
                    "query_id": option.query_id,
                    "label": option.label,
                    "query": option.query.to_dict()
                    if isinstance(option.query, TemporalQuery)
                    else serialize_query(option.query),
                }
                for option in self.query_options
            ],
            "plan": self.g2_2_plan.to_dict() if self.g2_2_plan else None,
            "action_result": (
                self.g2_2_last_result.to_dict() if self.g2_2_last_result else None
            ),
            "memory_cells": self._g2_2_memory_cells(),
            "future_cells": self._g2_2_future_cells(),
            "external_history": list(self.external_history),
            "recovery": self.g2_2_recovery.to_dict(),
            "recorder_record_count": len(self.recorder.history),
            "history_firewall_message": self.last_history_firewall_message,
            "world_changed_since_now": False,
            "world_event_available": self.demo_id
            in {"g2_2_verify_false", "g2_2_verify_correct"},
            "move_event_label": (
                "Toggle memory truth"
                if self.demo_id in {"g2_2_verify_false", "g2_2_verify_correct"}
                else "Recovery demo has no world toggle"
            ),
            "world_event_help": (
                "Plan, execute SCAN, then compare the fresh Now ID and recovery state."
            ),
            "success_badges": self._g2_2_success_badges(),
            "g2_2_note": self.g2_2_note,
            "g2_2_event_note": self.g2_2_event_note,
            "benchmark": self._load_g2_2_benchmark_snapshot(),
        }

    def _g2_2_success_badges(self) -> list[dict[str, str]]:
        badges = [{"label": "G2.2 epistemic geometry", "status": "ACTIVE", "tone": "pass"}]
        if self.epistemic_state is not None:
            badges.append({"label": "Fresh TemporalNow", "status": "PASS", "tone": "pass"})
        if self.g2_2_plan is not None:
            badges.append(
                {
                    "label": "Decision",
                    "status": self.g2_2_plan.decision_type.value.upper(),
                    "tone": "warn" if self.g2_2_plan.verification_required else "pass",
                }
            )
        if self.g2_2_last_result is not None and self.g2_2_last_result.information_action:
            badges.append({"label": "SCAN", "status": "OBSERVED FRESH", "tone": "pass"})
        if self.g2_2_recovery.disconfirmed_target_poses:
            badges.append({"label": "Target memory", "status": "DISCONFIRMED", "tone": "warn"})
        if self.g2_2_recovery.invalidated_poses:
            badges.append({"label": "Path assumption", "status": "INVALIDATED", "tone": "warn"})
        if self.g2_2_recovery.target_reacquired:
            badges.append({"label": "Target", "status": "REACQUIRED", "tone": "pass"})
        return badges

    def _g2_2_memory_cells(self) -> list[dict[str, Any]]:
        cells = []
        for memory in self.g2_2_memory_reconstructions:
            pose = self._pose_from_cell_id(memory.proposition.source_id)
            if pose is None and memory.proposition.source_id == "target":
                pose = self._pose_from_cell_id(memory.proposition.target_id)
            if pose is None:
                continue
            cells.append(
                {
                    "pose": pose.to_dict(),
                    "state": memory.proposition.target_id,
                    "confidence": memory.confidence,
                    "provenance": memory.provenance.value,
                    "tags": list(memory.distortion_tags),
                }
            )
        return cells

    def _g2_2_future_cells(self) -> list[dict[str, Any]]:
        cells = []
        for hypothesis in self.g2_2_future_hypotheses:
            pose = None
            raw_pose = hypothesis.metadata.get("pose")
            if isinstance(raw_pose, dict):
                pose = Pose2D(int(raw_pose["x"]), int(raw_pose["y"]))
            if pose is None:
                pose = self._pose_from_cell_id(hypothesis.proposition.target_id)
            if pose is None:
                continue
            cells.append(
                {
                    "pose": pose.to_dict(),
                    "confidence": hypothesis.confidence,
                    "provenance": hypothesis.provenance.value,
                    "label": "HYPOTHETICAL - not current target location",
                }
            )
        return cells

    def _load_g2_2_benchmark_snapshot(self) -> dict[str, Any] | None:
        root = Path(__file__).resolve().parents[2]
        artifact_dir = root / "artifacts" / "g2_2"
        metrics_path = artifact_dir / "g2_2_metrics.json"
        config_path = artifact_dir / "g2_2_seed_and_config.json"
        difficulty_path = artifact_dir / "g2_2_metrics_by_difficulty.json"
        if not metrics_path.exists() or not config_path.exists():
            return None
        return {
            "metrics": json.loads(metrics_path.read_text(encoding="utf-8")),
            "config": json.loads(config_path.read_text(encoding="utf-8")),
            "by_difficulty": json.loads(difficulty_path.read_text(encoding="utf-8"))
            if difficulty_path.exists()
            else {},
        }

    def _load_g2_1_demo(self, demo_id: str) -> dict[str, Any]:
        self.spatial_runner = SpatialCycleRunner()
        self.spatial_planner = AStarPlanner()
        self.spatial_executor = ActionExecutor()
        self.spatial_state: SpatialCycleState | None = None
        self.g2_1_plan: Plan | None = None
        self.g2_1_last_result: ActionExecutionResult | None = None
        self.g2_1_memory_reconstructions: tuple[MemoryReconstruction, ...] = ()
        self.g2_1_future_hypotheses: tuple[FutureHypothesis, ...] = ()
        self.g2_1_note = ""
        self.g2_1_event_note = ""
        self.g2_1_dynamic_event_applied = False
        self.spatial_world = SpatialWorldState(
            8,
            6,
            [
                SpatialEntity("agent", "agent", Pose2D(0, 2), "Agent"),
                SpatialEntity("target", "target", Pose2D(7, 2), "Target"),
            ],
        )

        if demo_id == "g2_1_replanning":
            self.g2_1_note = (
                "Hero replanning: a selected path is only a possible future. "
                "After a world obstacle appears, the next fresh observation forces replanning."
            )
            for pose in (Pose2D(3, 0), Pose2D(3, 1), Pose2D(3, 2), Pose2D(3, 3)):
                self.spatial_world.set_obstacle(pose)
        elif demo_id == "g2_1_stale_memory":
            self.g2_1_note = (
                "Stale memory says the shortcut is free, but current observation shows a solid obstacle."
            )
            self.spatial_world = SpatialWorldState(
                6,
                5,
                [
                    SpatialEntity("agent", "agent", Pose2D(0, 2), "Agent"),
                    SpatialEntity("target", "target", Pose2D(5, 2), "Target"),
                ],
            )
            self.spatial_world.set_obstacle(Pose2D(2, 2), "blocked_shortcut")
            self.g2_1_memory_reconstructions = (
                self._g2_1_memory_cell(Pose2D(2, 2), OccupancyState.FREE, "stale_free"),
            )
        elif demo_id == "g2_1_unknown_memory":
            self.g2_1_note = (
                "Unknown corridor: memory can support a conditional route, but it remains an assumption."
            )
            self.spatial_world = SpatialWorldState(
                5,
                3,
                [
                    SpatialEntity("agent", "agent", Pose2D(0, 1), "Agent"),
                    SpatialEntity("target", "target", Pose2D(4, 1), "Target"),
                    SpatialEntity("wall_a", "obstacle", Pose2D(2, 0), blocks_movement=True),
                    SpatialEntity("wall_b", "obstacle", Pose2D(2, 2), blocks_movement=True),
                ],
                hidden_cells=(Pose2D(2, 1),),
            )
            self.g2_1_memory_reconstructions = (
                self._g2_1_memory_cell(Pose2D(2, 1), OccupancyState.FREE, "remembered_corridor"),
            )
        elif demo_id == "g2_1_future_target":
            self.g2_1_note = (
                "Future target hypothesis: the dotted target is possible future content, not the current goal."
            )
            future_pose = Pose2D(7, 0)
            self.g2_1_future_hypotheses = (
                FutureHypothesis.create(
                    1,
                    Proposition("target", RelationType.AT, future_pose.cell_id()),
                    0.72,
                    generator_id="g2_1_demo_future_target",
                    metadata={"pose": future_pose.to_dict(), "demo": demo_id},
                ),
            )
        else:
            raise ValueError(f"Unknown G2.1 demo_id: {demo_id}")

        self.query_options = (
            QueryOption(
                "g2_1_plan",
                "Plan from current geometry",
                TemporalQuery.relation(
                    "agent",
                    RelationType.REACHABLE,
                    "target",
                    TemporalIntent.POSSIBLE_FUTURE,
                ),
            ),
        )
        self.active_query_id = "g2_1_plan"
        return self.to_dict()

    def _run_g2_1_cycle(self) -> dict[str, Any]:
        self.spatial_state = self.spatial_runner.run(
            self.spatial_world,
            reconstructed_memories=self.g2_1_memory_reconstructions,
            future_hypotheses=self.g2_1_future_hypotheses,
        )
        self.g2_1_plan = self.spatial_planner.plan(
            self.spatial_state.spatial_geometry,
            memory_reconstructions=self.spatial_state.temporal_now.reconstructed_memories,
        )
        self.external_history.append(
            {
                "cycle_id": self.spatial_state.temporal_now.cycle_id,
                "now_id": str(self.spatial_state.temporal_now.now_id),
                "agent_pose": self.spatial_state.spatial_geometry.agent().pose.to_dict(),
                "target_pose": self.spatial_state.spatial_geometry.target().pose.to_dict(),
                "plan_valid": self.g2_1_plan.valid,
                "plan_steps": len(self.g2_1_plan.steps),
                "conditional": self.g2_1_plan.conditional,
            }
        )
        return self.to_dict()

    def g2_1_execute_one_step(self) -> dict[str, Any]:
        if self.spatial_state is None or self.g2_1_plan is None:
            self._run_g2_1_cycle()
        if self.g2_1_plan is None or not self.g2_1_plan.valid:
            self.g2_1_event_note = "No valid selected plan is available to execute."
            return self.to_dict()
        proposal = ActionProposal.from_plan(self.g2_1_plan)
        if proposal is None:
            self.g2_1_event_note = "The agent is already at the current goal."
            return self.to_dict()
        self.g2_1_last_result = self.spatial_executor.execute(self.spatial_world, proposal)
        self.g2_1_event_note = (
            "Executed one concrete action in the external world; rebuilding fresh Now."
        )
        return self._run_g2_1_cycle()

    def g2_1_run_closed_loop(self) -> dict[str, Any]:
        for index in range(12):
            if self.spatial_state is None or self.g2_1_plan is None:
                self._run_g2_1_cycle()
            if self.spatial_state is None:
                break
            if self.spatial_state.spatial_geometry.agent().pose == self.spatial_state.spatial_geometry.target().pose:
                break
            if (
                self.demo_id == "g2_1_replanning"
                and index == 1
                and not self.g2_1_dynamic_event_applied
            ):
                self._apply_g2_1_world_event()
            before_cycle = self.spatial_state.temporal_now.cycle_id
            self.g2_1_execute_one_step()
            if self.spatial_state is None or self.spatial_state.temporal_now.cycle_id == before_cycle:
                break
        return self.to_dict()

    def g2_1_move_target(self) -> dict[str, Any]:
        target = self.spatial_world.entity("target").pose
        new_pose = Pose2D(target.x, 0 if target.y != 0 else self.spatial_world.height - 1)
        if self.spatial_world.is_blocked_truth(new_pose):
            new_pose = Pose2D(self.spatial_world.width - 1, self.spatial_world.height - 1)
        self.spatial_world.move_entity("target", new_pose)
        self.g2_1_event_note = "External target moved. Run Plan to observe and replan."
        return self.to_dict()

    def g2_1_inject_stale_memory(self) -> dict[str, Any]:
        pose = Pose2D(max(1, self.spatial_world.width // 2), self.spatial_world.height // 2)
        self.g2_1_memory_reconstructions = (
            *self.g2_1_memory_reconstructions,
            self._g2_1_memory_cell(pose, OccupancyState.FREE, "stale_or_unverified_free"),
        )
        self.g2_1_event_note = "Added a reconstructed-memory assumption; it is not observation."
        return self.to_dict()

    def g2_1_inject_false_memory(self) -> dict[str, Any]:
        pose = Pose2D(max(1, self.spatial_world.width // 2), self.spatial_world.height // 2)
        if not self.spatial_world.is_blocked_truth(pose):
            self.spatial_world.set_obstacle(pose, "false_memory_hidden_obstacle")
        self.spatial_world.hide_cell(pose)
        self.g2_1_memory_reconstructions = (
            *self.g2_1_memory_reconstructions,
            self._g2_1_memory_cell(pose, OccupancyState.FREE, "false_memory"),
        )
        self.g2_1_event_note = "Injected false memory for a hidden blocked cell."
        return self.to_dict()

    def g2_1_add_future_hypothesis(self) -> dict[str, Any]:
        pose = Pose2D(self.spatial_world.width - 1, 0)
        self.g2_1_future_hypotheses = (
            *self.g2_1_future_hypotheses,
            FutureHypothesis.create(
                1,
                Proposition("target", RelationType.AT, pose.cell_id()),
                0.64,
                generator_id="g2_1_demo_manual_future",
                metadata={"pose": pose.to_dict(), "demo": self.demo_id},
            ),
        )
        self.g2_1_event_note = "Added a future target hypothesis; current target is unchanged."
        return self.to_dict()

    def g2_1_hide_region(self) -> dict[str, Any]:
        pose = Pose2D(max(1, self.spatial_world.width // 2), self.spatial_world.height // 2)
        self.spatial_world.hide_cell(pose)
        self.g2_1_event_note = "A region is now unobserved; planning must treat it as unknown."
        return self.to_dict()

    def _apply_g2_1_world_event(self) -> dict[str, Any]:
        if self.demo_id == "g2_1_future_target":
            return self.g2_1_move_target()
        if self.g2_1_plan is None:
            self._run_g2_1_cycle()
        candidate = None
        if self.g2_1_plan is not None and self.g2_1_plan.steps:
            index = 1 if len(self.g2_1_plan.steps) > 1 else 0
            candidate = self.g2_1_plan.steps[index].to_pose
        candidate = candidate or Pose2D(max(1, self.spatial_world.width // 2), self.spatial_world.height // 2)
        if candidate != self.spatial_world.entity("agent").pose and candidate != self.spatial_world.entity("target").pose:
            self.spatial_world.set_obstacle(candidate)
            self.g2_1_dynamic_event_applied = True
            self.g2_1_event_note = (
                "External obstacle appeared on the old selected path. Run Plan or Closed loop to re-observe."
            )
        return self.to_dict()

    def _g2_1_memory_cell(
        self,
        pose: Pose2D,
        state: OccupancyState,
        tag: str,
    ) -> MemoryReconstruction:
        return MemoryReconstruction(
            reconstruction_id=uuid4(),
            created_at_cycle_id=2,
            proposition=Proposition(
                source_id=pose.cell_id(),
                relation_type=RelationType.OCCUPANCY,
                target_id=state.value,
            ),
            source_trace_ids=(uuid4(),),
            historical_source_cycles=(1,),
            confidence=0.84,
            fidelity=0.9,
            distortion_tags=(tag,),
        )

    def _g2_2_memory_target(self, pose: Pose2D, tag: str) -> MemoryReconstruction:
        return MemoryReconstruction(
            reconstruction_id=uuid4(),
            created_at_cycle_id=2,
            proposition=Proposition(
                source_id="target",
                relation_type=RelationType.AT,
                target_id=pose.cell_id(),
            ),
            source_trace_ids=(uuid4(),),
            historical_source_cycles=(1,),
            confidence=0.9,
            fidelity=0.9,
            distortion_tags=(tag,),
        )

    def _g2_1_to_dict(self) -> dict[str, Any]:
        spatial_now = self.spatial_state.spatial_geometry if self.spatial_state else None
        temporal_now = self.spatial_state.temporal_now if self.spatial_state else None
        return {
            "schema": "nowmind.g2_1.web_state.v1",
            "demo_id": self.demo_id,
            "disclaimer": (
                "NowMind G2.1 is a deterministic spatial planning research demo. "
                "It does not demonstrate or claim phenomenal consciousness."
            ),
            "world": self.spatial_world.to_dict(),
            "spatial_now": spatial_now.to_dict() if spatial_now else None,
            "temporal_now": (
                {
                    "cycle_id": temporal_now.cycle_id,
                    "now_id": str(temporal_now.now_id),
                    "created_at": temporal_now.created_at.isoformat(),
                    "reconstructed_memories": [
                        memory.to_dict() for memory in temporal_now.reconstructed_memories
                    ],
                    "future_hypotheses": [
                        hypothesis.to_dict() for hypothesis in temporal_now.future_hypotheses
                    ],
                }
                if temporal_now
                else None
            ),
            "current_now": None,
            "current_answer": None,
            "temporal_answer": None,
            "active_query": self.active_temporal_query.to_dict(),
            "query_options": [
                {
                    "query_id": option.query_id,
                    "label": option.label,
                    "query": option.query.to_dict()
                    if isinstance(option.query, TemporalQuery)
                    else serialize_query(option.query),
                }
                for option in self.query_options
            ],
            "plan": self.g2_1_plan.to_dict() if self.g2_1_plan else None,
            "action_result": (
                self.g2_1_last_result.to_dict() if self.g2_1_last_result else None
            ),
            "memory_cells": self._g2_1_memory_cells(),
            "future_cells": self._g2_1_future_cells(),
            "external_history": list(self.external_history),
            "recorder_record_count": len(self.recorder.history),
            "history_firewall_message": self.last_history_firewall_message,
            "world_changed_since_now": (
                spatial_now is not None
                and self.spatial_world.world_version != spatial_now.world_version
            ),
            "world_event_available": True,
            "move_event_label": (
                "Move target" if self.demo_id == "g2_1_future_target" else "Move obstacle"
            ),
            "world_event_help": (
                "Plan, execute one step, then add a world change. The next observation rebuilds a fresh Now before replanning."
            ),
            "success_badges": self._g2_1_success_badges(),
            "g2_1_note": self.g2_1_note,
            "g2_1_event_note": self.g2_1_event_note,
            "benchmark": self._load_g2_1_benchmark_snapshot(),
        }

    def _g2_1_memory_cells(self) -> list[dict[str, Any]]:
        cells = []
        for memory in self.g2_1_memory_reconstructions:
            pose = self._pose_from_cell_id(memory.proposition.source_id)
            if pose is None:
                continue
            cells.append(
                {
                    "pose": pose.to_dict(),
                    "state": memory.proposition.target_id,
                    "confidence": memory.confidence,
                    "provenance": memory.provenance.value,
                    "tags": list(memory.distortion_tags),
                }
            )
        return cells

    def _g2_1_future_cells(self) -> list[dict[str, Any]]:
        cells = []
        for hypothesis in self.g2_1_future_hypotheses:
            pose = None
            if "pose" in hypothesis.metadata:
                raw = hypothesis.metadata["pose"]
                if isinstance(raw, dict):
                    pose = Pose2D(int(raw["x"]), int(raw["y"]))
            if pose is None:
                pose = self._pose_from_cell_id(hypothesis.proposition.target_id)
            if pose is None:
                continue
            cells.append(
                {
                    "pose": pose.to_dict(),
                    "confidence": hypothesis.confidence,
                    "provenance": hypothesis.provenance.value,
                    "label": "HYPOTHETICAL - not current target location",
                }
            )
        return cells

    def _pose_from_cell_id(self, cell_id: str) -> Pose2D | None:
        if not cell_id.startswith("cell:"):
            return None
        try:
            x_raw, y_raw = cell_id.removeprefix("cell:").split(",", 1)
            return Pose2D(int(x_raw), int(y_raw))
        except ValueError:
            return None

    def _g2_1_success_badges(self) -> list[dict[str, str]]:
        badges = [{"label": "G2.1 possibility geometry", "status": "ACTIVE", "tone": "pass"}]
        if self.spatial_state is not None:
            badges.append({"label": "Fresh TemporalNow", "status": "PASS", "tone": "pass"})
        if self.g2_1_plan is not None:
            badges.append(
                {
                    "label": "Selected plan",
                    "status": "CONDITIONAL" if self.g2_1_plan.conditional else "VALID" if self.g2_1_plan.valid else "NO ROUTE",
                    "tone": "pass" if self.g2_1_plan.valid else "warn",
                }
            )
        if self.g2_1_dynamic_event_applied:
            badges.append({"label": "Dynamic replanning", "status": "VISIBLE", "tone": "warn"})
        if self.last_history_firewall_message:
            badges.append({"label": "History boundary", "status": "PASS", "tone": "pass"})
        return badges

    def _load_g2_1_benchmark_snapshot(self) -> dict[str, Any] | None:
        root = Path(__file__).resolve().parents[2]
        artifact_dir = root / "artifacts" / "g2_1"
        metrics_path = artifact_dir / "g2_1_metrics.json"
        config_path = artifact_dir / "g2_1_seed_and_config.json"
        difficulty_path = artifact_dir / "g2_1_metrics_by_difficulty.json"
        if not metrics_path.exists() or not config_path.exists():
            return None
        return {
            "metrics": json.loads(metrics_path.read_text(encoding="utf-8")),
            "config": json.loads(config_path.read_text(encoding="utf-8")),
            "by_difficulty": json.loads(difficulty_path.read_text(encoding="utf-8"))
            if difficulty_path.exists()
            else {},
        }

    def _load_g2_demo(self, demo_id: str) -> dict[str, Any]:
        store = MemoryStore()
        self.temporal_runner = TemporalCycleRunner(next_cycle_id=2, memory_store=store)
        self.g2_future_hypotheses: tuple[FutureHypothesis, ...] = ()
        self.g2_note = ""
        self.world = WorldState()
        for entity_id, kind, label in (
            ("ball", "object", "ball"),
            ("box_a", "container", "Box A"),
            ("box_b", "container", "Box B"),
            ("box_c", "container", "Box C"),
            ("box_d", "container", "Box D"),
        ):
            self.world.apply(AddEntity(entity_id, kind, label))

        memory_target = "box_a"
        memory_confidence = 0.94
        current_target: str | None = "box_b"
        current_confidence = 1.0
        conflict_target: str | None = None

        if demo_id == "g2_memory_present":
            self.g2_note = "G2-A: Memory vs present. Ball was in Box A, now in Box B."
            self.g2_future_hypotheses = (
                self._g2_future("box_c", confidence=0.6),
            )
        elif demo_id == "g2_false_memory":
            self.g2_note = (
                "G2-B: Injected false memory says Box D, but current observation "
                "still answers Box B."
            )
            memory_target = "box_d"
            memory_confidence = 0.96
        elif demo_id == "g2_future":
            self.g2_note = "G2-C: Future hypothesis says Box C while present remains Box B."
            self.g2_future_hypotheses = (
                self._g2_future("box_c", confidence=0.72),
            )
        elif demo_id == "g2_confidence":
            self.g2_note = (
                "G2-D: High-confidence memory A does not override moderate "
                "current observation B."
            )
            current_confidence = 0.6
            memory_confidence = 0.97
        elif demo_id == "g2_hidden":
            self.g2_note = (
                "G2-E: No current visibility. Memory reconstructs A, but NOW "
                "query returns UNKNOWN."
            )
            current_target = None
        elif demo_id == "g2_contradiction":
            self.g2_note = (
                "G2-F: Conflicting present observations produce structured "
                "contradiction instead of a guess."
            )
            conflict_target = "box_c"
        else:
            raise ValueError(f"Unknown G2 demo_id: {demo_id}")

        store.add(
            self._g2_memory_trace(
                memory_target,
                confidence=memory_confidence,
                false_memory=demo_id == "g2_false_memory",
            )
        )
        if current_target is not None:
            self.world.apply(
                SetRelation("ball", current_target, RelationType.INSIDE, current_confidence)
            )
        if conflict_target is not None:
            self.world.apply(SetRelation("ball", conflict_target, RelationType.INSIDE))

        self.query_options = self._g2_query_options()
        self.active_query_id = "g2_current"
        return self.to_dict()

    def _g2_query_options(self) -> tuple[QueryOption, ...]:
        options = [
            QueryOption(
                "g2_current",
                "Current: where is ball now?",
                TemporalQuery.relation("ball", RelationType.INSIDE, None, TemporalIntent.NOW),
            ),
            QueryOption(
                "g2_past_a",
                "Past: was ball in Box A?",
                TemporalQuery.relation("ball", RelationType.INSIDE, "box_a", TemporalIntent.PAST),
            ),
            QueryOption(
                "g2_future_c",
                "Future: could ball be in Box C?",
                TemporalQuery.relation(
                    "ball",
                    RelationType.INSIDE,
                    "box_c",
                    TemporalIntent.POSSIBLE_FUTURE,
                ),
            ),
        ]
        if self.demo_id == "g2_false_memory":
            options[1] = QueryOption(
                "g2_past_d",
                "Past: reconstructed false memory D?",
                TemporalQuery.relation("ball", RelationType.INSIDE, "box_d", TemporalIntent.PAST),
            )
        return tuple(options)

    def _g2_memory_trace(
        self,
        target_id: str,
        confidence: float,
        false_memory: bool = False,
    ) -> MemoryTrace:
        metadata: dict[str, Any] = {"demo": self.demo_id}
        if false_memory:
            metadata["injected_false_memory"] = True
        return MemoryTrace.create(
            source_cycle_id=1,
            encoded_at_cycle_id=1,
            proposition=Proposition("ball", RelationType.INSIDE, target_id),
            original_source=TemporalSource.OBSERVED_NOW,
            encoded_confidence=confidence,
            trace_strength=1.0,
            metadata=metadata,
        )

    def _g2_future(self, target_id: str, confidence: float) -> FutureHypothesis:
        return FutureHypothesis.create(
            created_at_cycle_id=2,
            proposition=Proposition("ball", RelationType.INSIDE, target_id),
            confidence=confidence,
            generator_id="g2_demo_manual_hypothesis",
            metadata={"demo": self.demo_id},
        )

    def _run_g2_cycle(self) -> dict[str, Any]:
        if self.temporal_runner is None:
            raise RuntimeError("G2 temporal runner was not initialized.")
        self.current_temporal_now = self.temporal_runner.run(
            self.world,
            memory_cue=RetrievalCue.for_relation(
                "ball",
                RelationType.INSIDE,
                temporal_intent=TemporalIntent.PAST.value,
            ),
            future_hypotheses=self.g2_future_hypotheses,
            encode_after=False,
        )
        self.current_temporal_answer = answer_temporal(
            self.current_temporal_now,
            self.active_temporal_query,
        )
        self.external_history.append(
            {
                "cycle_id": self.current_temporal_now.cycle_id,
                "now_id": str(self.current_temporal_now.now_id),
                "temporal_now": self._serialize_temporal_now(self.current_temporal_now),
                "query": self.active_temporal_query.display(),
                "answer": self.current_temporal_answer.status.value,
            }
        )
        return self.to_dict()

    def _apply_g2_world_event(self) -> dict[str, Any]:
        self.last_history_firewall_message = (
            "G2 visual scenarios are preloaded. Choose another G2 demo or run the "
            "cycle again to rebuild a fresh TemporalNowState."
        )
        return self.to_dict()

    def _g2_to_dict(self) -> dict[str, Any]:
        return {
            "schema": "nowmind.g2.web_state.v1",
            "demo_id": self.demo_id,
            "disclaimer": (
                "NowMind G2 is a computational research architecture for temporal "
                "source separation. It does not demonstrate or claim phenomenal consciousness."
            ),
            "world": serialize_world(self.world),
            "current_now": None,
            "current_answer": None,
            "temporal_now": (
                self._serialize_temporal_now(self.current_temporal_now)
                if self.current_temporal_now
                else None
            ),
            "temporal_answer": (
                self.current_temporal_answer.to_dict()
                if self.current_temporal_answer
                else None
            ),
            "active_query": self.active_temporal_query.to_dict(),
            "query_options": [
                {
                    "query_id": option.query_id,
                    "label": option.label,
                    "query": option.query.to_dict()
                    if isinstance(option.query, TemporalQuery)
                    else serialize_query(option.query),
                }
                for option in self.query_options
            ],
            "external_history": list(self.external_history),
            "recorder_record_count": len(self.recorder.history),
            "history_firewall_message": self.last_history_firewall_message,
            "world_changed_since_now": False,
            "world_event_available": False,
            "move_event_label": "G2 scenario preloaded",
            "world_event_help": "Pick a G2 demo, click Run cycle, then switch current/past/future queries.",
            "success_badges": self._g2_success_badges(),
            "g2_note": self.g2_note,
            "benchmark": self._load_g2_benchmark_snapshot(),
        }

    def _serialize_temporal_now(self, now: TemporalNowState) -> dict[str, Any]:
        observed = [
            serialize_relation(relation)
            for relation in now.present_geometry.relations
            if relation.provenance.value == "observed_now"
        ]
        inferred = [
            serialize_relation(relation)
            for relation in now.present_geometry.relations
            if relation.provenance.value == "inferred_now"
        ]
        return {
            "cycle_id": now.cycle_id,
            "now_id": str(now.now_id),
            "created_at": now.created_at.isoformat(),
            "world_version": now.present_geometry.world_version,
            "entities": [entity.to_dict() for entity in now.present_geometry.entities],
            "observed_relations": observed,
            "inferred_relations": inferred,
            "validation": {
                "is_valid": now.present_geometry.validation.is_valid,
                "issues": [
                    serialize_issue(issue) for issue in now.present_geometry.validation.issues
                ],
            },
            "reconstructed_memories": [
                memory.to_dict() for memory in now.reconstructed_memories
            ],
            "future_hypotheses": [
                hypothesis.to_dict() for hypothesis in now.future_hypotheses
            ],
        }

    def _g2_success_badges(self) -> list[dict[str, str]]:
        badges = [{"label": "G2 source channels", "status": "SEPARATE", "tone": "pass"}]
        if self.current_temporal_now is not None:
            badges.append({"label": "Fresh TemporalNow", "status": "PASS", "tone": "pass"})
        if self.current_temporal_answer is not None:
            if (
                self.demo_id == "g2_false_memory"
                and self.current_temporal_answer.status is TruthStatus.TRUE
                and self.current_temporal_answer.source is TemporalSource.OBSERVED_NOW
            ):
                badges.append(
                    {
                        "label": "Conflicting memory did not replace present",
                        "status": "PASS",
                        "tone": "pass",
                    }
                )
            if self.demo_id == "g2_hidden" and self.current_temporal_answer.status is TruthStatus.UNKNOWN:
                badges.append({"label": "No current evidence", "status": "UNKNOWN", "tone": "warn"})
        if self.last_history_firewall_message:
            badges.append({"label": "Temporal history boundary", "status": "PASS", "tone": "pass"})
        return badges

    def _load_g2_benchmark_snapshot(self) -> dict[str, Any] | None:
        root = Path(__file__).resolve().parents[2]
        artifact_dir = root / "artifacts" / "g2"
        metrics_path = artifact_dir / "g2_metrics.json"
        config_path = artifact_dir / "g2_seed_and_config.json"
        matrix_path = artifact_dir / "g2_source_confusion_matrix.json"
        if not metrics_path.exists() or not config_path.exists() or not matrix_path.exists():
            return None
        return {
            "metrics": json.loads(metrics_path.read_text(encoding="utf-8")),
            "config": json.loads(config_path.read_text(encoding="utf-8")),
            "confusion_matrix": json.loads(matrix_path.read_text(encoding="utf-8")),
        }

    def _demo_a_world_relation(self) -> RelationType | None:
        if self.demo_id != "fresh_now":
            return None
        for relation in self.world.relations:
            if (
                relation.source_id == "red_cube"
                and relation.target_id == "blue_cube"
                and relation.relation_type in {RelationType.LEFT_OF, RelationType.RIGHT_OF}
            ):
                return relation.relation_type
        return None

    def _move_event_label(self, world_relation: RelationType | None) -> str:
        if self.demo_id == "inference":
            if self._demo_b_bridge_present():
                return "Break inference chain"
            return "Restore inference chain"
        if self.demo_id == "containment":
            if self._demo_c_bridge_present():
                return "Break containment chain"
            return "Restore containment chain"
        if self.demo_id == "contradiction":
            if self._demo_d_contradiction_present():
                return "Resolve contradiction"
            return "Restore contradiction"
        if self.demo_id != "fresh_now":
            return "World event unavailable"
        if world_relation is RelationType.RIGHT_OF:
            return "Move red_cube left"
        return "Move red_cube right"

    def _demo_b_bridge_present(self) -> bool:
        if self.demo_id != "inference":
            return False
        for relation in self.world.relations:
            if (
                relation.source_id == "b"
                and relation.target_id == "c"
                and relation.relation_type is RelationType.LEFT_OF
            ):
                return True
        return False

    def _demo_c_bridge_present(self) -> bool:
        if self.demo_id != "containment":
            return False
        for relation in self.world.relations:
            if (
                relation.source_id == "box"
                and relation.target_id == "cabinet"
                and relation.relation_type is RelationType.INSIDE
            ):
                return True
        return False

    def _demo_d_contradiction_present(self) -> bool:
        if self.demo_id != "contradiction":
            return False
        has_left = False
        has_right = False
        for relation in self.world.relations:
            if relation.source_id == "red_cube" and relation.target_id == "blue_cube":
                if relation.relation_type is RelationType.LEFT_OF:
                    has_left = True
                if relation.relation_type is RelationType.RIGHT_OF:
                    has_right = True
        return has_left and has_right

    def _world_event_help(self) -> str:
        if self.demo_id == "fresh_now":
            return (
                "Run cycle 1, move red_cube, then run cycle 2. The world changes "
                "before the fresh Now catches up."
            )
        if self.demo_id == "inference":
            return (
                "Run a cycle, break the b -> c link, then run another cycle. "
                "The inferred A LEFT_OF C answer should disappear."
            )
        if self.demo_id == "containment":
            return (
                "Run a cycle, break the box -> cabinet containment, then run "
                "another cycle. The inferred key INSIDE cabinet answer should disappear."
            )
        if self.demo_id == "contradiction":
            return (
                "Run a cycle, resolve one conflicting fact, then run another cycle. "
                "The answer should change from CONTRADICTORY to TRUE."
            )
        return "This demo has no world event. Run a cycle and inspect the result."

    def _success_badges(self, stale_present: bool | None) -> list[dict[str, str]]:
        badges: list[dict[str, str]] = []
        if self.current_now is not None:
            badges.append({"label": "Fresh Now", "status": "PASS", "tone": "pass"})
            if stale_present is False and self.demo_id == "fresh_now":
                badges.append(
                    {
                        "label": "Stale-state contamination",
                        "status": "NONE",
                        "tone": "pass",
                    }
                )
            if self.current_now.geometry.validation.contradictions:
                badges.append(
                    {
                        "label": "Contradiction detected",
                        "status": "YES",
                        "tone": "warn",
                    }
                )
        if self.last_history_firewall_message:
            badges.append(
                {
                    "label": "History firewall",
                    "status": "ENFORCED",
                    "tone": "pass",
                }
            )
        return badges
