from __future__ import annotations

import json
import threading
from urllib.request import Request, urlopen

from nowmind.demo import web_controller
from nowmind.demo.web import create_server
from nowmind.demo.web import _INDEX_HTML
from nowmind.demo.web_controller import WebDemoController
from nowmind.reasoning.query import Answer, TruthStatus
from nowmind.temporal.query import TemporalAnswer


def test_web_page_contains_visual_clarity_elements() -> None:
    required_text = [
        "NowMind - Geometric Now G1",
        "What this tests",
        "Start here",
        "Live experiment",
        "How it works",
        "Visual architecture",
        "Guided processing path",
        "Persistent world",
        "Current Now",
        "External history",
        "World now",
        "Demo A before / after",
        "What the reasoner can see right now",
        "What exists but the reasoner cannot see",
        "Present Geometry graph",
        "Technical details",
        "Cycle rail",
        "cycleRailBody",
        "sideWorldBody",
        "demoBriefBody",
        "beforeAfterSection",
        "side-panel",
        "object-block",
        "Left-to-right order",
        "Known chain",
        "Nested containment",
        "Known containment",
        "This prototype tests representation and reasoning behavior",
        "Temporal Geometry",
        "PRESENT",
        "RECONSTRUCTED PAST",
        "POSSIBLE FUTURE",
        "CURRENT TEMPORAL NOW",
        "NOT DIRECTLY AVAILABLE",
        "Benchmark dashboard",
        "CONFLICTING MEMORY DID NOT REPLACE PRESENT",
        "G2.1-A - Possibility Replanning",
        "SOLID = observed now",
        "DASHED = MEMORY RECONSTRUCTION",
        "DOTTED = POSSIBLE FUTURE",
        "Selected plan is NOT reality",
        "Execute one step",
        "Run closed loop",
        "G2.2-A - Verify False Memory",
        "G2.2-B - Verify Correct Memory",
        "G2.2.1-R1 - Stale Target Recovery",
        "G2.2.1-R2 - Hidden Obstacle Recovery",
        "FOG = currently unknown",
        "SCAN changes observation, not world truth",
        "Epistemic decision",
        "Toggle memory truth",
        "G2.3 - Model Comparison",
        "G2.3 Model Comparison",
        "NOWMIND REPRESENTATION",
        "CHRONOLOGICAL REPRESENTATION",
        "Reveal evaluator answer",
        "Model proposal",
        "Full-G Reviewer",
        "Full-G reviewer package",
        "What the demo does NOT prove",
        "Real-model result to date",
    ]

    for text in required_text:
        assert text in _INDEX_HTML


def test_web_page_generic_scene_renderer_uses_defined_order_variable() -> None:
    assert "const { connected, disconnected, ordered }" in _INDEX_HTML
    assert "if (!ordered.length)" in _INDEX_HTML
    assert "if (!order.length)" not in _INDEX_HTML


def test_web_page_places_architecture_in_sidebar_helper() -> None:
    assert '<aside class="side-panel"' in _INDEX_HTML
    assert '<summary>Visual architecture</summary>' in _INDEX_HTML
    assert '<summary>Guided processing path</summary>' in _INDEX_HTML
    assert "<h2>Visual architecture</h2>" not in _INDEX_HTML
    assert "<h2>Guided processing path</h2>" not in _INDEX_HTML
    assert "<h2>Live experiment</h2>" in _INDEX_HTML


def test_web_controller_uses_runtime_reasoning(monkeypatch) -> None:
    calls = []

    def fake_answer(now, query):
        calls.append((now, query))
        return Answer(TruthStatus.UNKNOWN, 0.0, query)

    monkeypatch.setattr(web_controller, "runtime_answer", fake_answer)
    controller = WebDemoController()
    controller.run_cycle()

    assert calls
    assert calls[-1][0] is controller.current_now
    assert calls[-1][1] is controller.active_query
    assert controller.current_answer is not None
    assert controller.current_answer.status is TruthStatus.UNKNOWN


def test_full_g_reviewer_mode_is_local_and_nonclaiming() -> None:
    controller = WebDemoController()
    state = controller.load_demo("full_g_reviewer")

    assert state["schema"] == "nowmind.full_g.web_state.v1"
    assert len(state["full_g"]["sections"]) == 6
    assert "consciousness" in state["full_g"]["nonclaims"]
    assert "qwen3:0.6b did not show" in state["full_g"]["real_model_result"]
    assert state["world_event_available"] is False
    assert state["success_badges"][1]["status"] == "OFF"


def test_g2_web_controller_uses_temporal_runtime_reasoning(monkeypatch) -> None:
    calls = []

    def fake_temporal_answer(now, query):
        calls.append((now, query))
        return TemporalAnswer(TruthStatus.UNKNOWN, query, 0.0, None)

    monkeypatch.setattr(web_controller, "answer_temporal", fake_temporal_answer)
    controller = WebDemoController()
    controller.load_demo("g2_memory_present")
    controller.run_cycle()

    assert calls
    assert calls[-1][0] is controller.current_temporal_now
    assert calls[-1][1] is controller.active_temporal_query
    assert controller.current_temporal_answer is not None
    assert controller.current_temporal_answer.status is TruthStatus.UNKNOWN


def test_g2_memory_present_demo_separates_present_memory_and_future() -> None:
    controller = WebDemoController()
    controller.load_demo("g2_memory_present")
    state = controller.run_cycle()

    assert state["schema"] == "nowmind.g2.web_state.v1"
    assert state["temporal_answer"]["source"] == "observed_now"
    assert state["temporal_answer"]["propositions"][0]["target_id"] == "box_b"
    assert state["temporal_now"]["reconstructed_memories"][0]["proposition"]["target_id"] == "box_a"
    assert state["temporal_now"]["future_hypotheses"][0]["proposition"]["target_id"] == "box_c"

    past_state = controller.set_query("g2_past_a")
    assert past_state["temporal_answer"]["source"] == "reconstructed_memory"
    assert past_state["temporal_answer"]["propositions"][0]["target_id"] == "box_a"

    future_state = controller.set_query("g2_future_c")
    assert future_state["temporal_answer"]["source"] == "hypothetical_future"
    assert future_state["temporal_answer"]["propositions"][0]["target_id"] == "box_c"


def test_g2_false_memory_and_hidden_current_visual_states() -> None:
    controller = WebDemoController()
    controller.load_demo("g2_false_memory")
    false_state = controller.run_cycle()

    assert false_state["temporal_answer"]["source"] == "observed_now"
    assert false_state["temporal_answer"]["propositions"][0]["target_id"] == "box_b"
    assert false_state["temporal_now"]["reconstructed_memories"][0]["proposition"][
        "target_id"
    ] == "box_d"
    assert any(
        badge["label"] == "Conflicting memory did not replace present"
        for badge in false_state["success_badges"]
    )

    controller.load_demo("g2_hidden")
    hidden_state = controller.run_cycle()
    assert hidden_state["temporal_answer"]["status"] == "unknown"
    assert hidden_state["temporal_answer"]["context"][0]["source"] == "reconstructed_memory"


def test_g2_history_boundary_message_after_deleting_researcher_history() -> None:
    controller = WebDemoController()
    controller.load_demo("g2_memory_present")
    controller.run_cycle()

    state = controller.delete_history_and_rerun()

    assert state["external_history"] == []
    assert "MemoryStore traces" in state["history_firewall_message"]


def test_g2_1_web_controller_plans_executes_and_reobserves() -> None:
    controller = WebDemoController()
    controller.load_demo("g2_1_replanning")
    planned = controller.run_cycle()

    assert planned["schema"] == "nowmind.g2_1.web_state.v1"
    assert planned["spatial_now"]["cycle_id"] == 1
    assert planned["plan"]["valid"] is True
    assert planned["plan"]["provenance"] == "hypothetical_future"

    executed = controller.g2_1_execute_one_step()

    assert executed["action_result"]["success"] is True
    assert executed["spatial_now"]["cycle_id"] == 2
    assert executed["temporal_now"]["now_id"] != planned["temporal_now"]["now_id"]


def test_g2_1_web_memory_and_future_overlays_are_source_distinct() -> None:
    controller = WebDemoController()
    memory_state = controller.load_demo("g2_1_unknown_memory")
    memory_state = controller.run_cycle()

    assert memory_state["memory_cells"][0]["provenance"] == "reconstructed_memory"
    assert memory_state["plan"]["conditional"] is True
    assert memory_state["plan"]["assumptions"][0]["source"] == "reconstructed_memory"

    future_state = controller.load_demo("g2_1_future_target")
    future_state = controller.run_cycle()

    assert future_state["future_cells"][0]["provenance"] == "hypothetical_future"
    assert future_state["spatial_now"]["entities"][1]["pose"] != future_state["future_cells"][0]["pose"]


def _g2_2_cell(state: dict, x: int, y: int) -> dict:
    return next(
        cell
        for cell in state["epistemic_now"]["cells"]
        if cell["pose"] == {"x": x, "y": y}
    )


def test_g2_2_web_verify_false_demo_scans_then_replans_safely() -> None:
    controller = WebDemoController()
    controller.load_demo("g2_2_verify_false")
    planned = controller.run_cycle()

    assert planned["schema"] == "nowmind.g2_2.web_state.v1"
    assert planned["plan"]["decision_type"] == "verify_first"
    assert planned["plan"]["provenance"] == "hypothetical_future"
    assert _g2_2_cell(planned, 3, 2)["observed_occupancy"] == "unknown"
    assert planned["memory_cells"][0]["provenance"] == "reconstructed_memory"
    assert planned["future_cells"][0]["provenance"] == "hypothetical_future"

    verified = controller.g2_2_execute_one_step()

    assert verified["action_result"]["action_type"] == "scan"
    assert verified["action_result"]["information_action"] is True
    assert verified["temporal_now"]["now_id"] != planned["temporal_now"]["now_id"]
    assert _g2_2_cell(verified, 3, 2)["observed_occupancy"] == "occupied"
    assert verified["plan"]["decision_type"] == "known_safe"
    assert all(step["to_pose"] != {"x": 3, "y": 2} for step in verified["plan"]["steps"])


def test_g2_2_web_verify_correct_demo_scans_then_uses_shortcut() -> None:
    controller = WebDemoController()
    controller.load_demo("g2_2_verify_correct")
    planned = controller.run_cycle()

    assert planned["plan"]["decision_type"] == "verify_first"

    verified = controller.g2_2_execute_one_step()

    assert verified["action_result"]["action_type"] == "scan"
    assert _g2_2_cell(verified, 3, 2)["observed_occupancy"] == "free"
    assert verified["plan"]["decision_type"] == "known_safe"
    assert any(step["to_pose"] == {"x": 3, "y": 2} for step in verified["plan"]["steps"])


def test_g2_2_world_event_toggles_memory_truth_without_stale_note() -> None:
    controller = WebDemoController()
    controller.load_demo("g2_2_verify_false")

    correct = controller.apply_demo_world_event()
    assert correct["demo_id"] == "g2_2_verify_correct"
    assert "memory is now correct" in correct["g2_2_event_note"]
    assert "memory-correct" in correct["g2_2_note"]

    false = controller.apply_demo_world_event()
    assert false["demo_id"] == "g2_2_verify_false"
    assert "memory is now false" in false["g2_2_event_note"]
    assert "verify-first" in false["g2_2_note"]


def test_g2_2_1_web_stale_target_recovery_disconfirms_then_reacquires() -> None:
    controller = WebDemoController()
    controller.load_demo("g2_2_1_stale_target_recovery")
    planned = controller.run_cycle()

    assert planned["schema"] == "nowmind.g2_2.web_state.v1"
    assert planned["recovery"]["disconfirmed_target_poses"] == [{"x": 2, "y": 2}]
    assert planned["plan"]["decision_type"] == "explore"
    assert planned["temporal_now"]["reconstructed_memories"][0]["proposition"]["target_id"] == "cell:2,2"

    scanned = controller.g2_2_execute_one_step()

    assert scanned["action_result"]["action_type"] == "scan"
    assert scanned["temporal_now"]["now_id"] != planned["temporal_now"]["now_id"]
    assert scanned["epistemic_now"]["target_pose"] == {"x": 6, "y": 2}
    assert scanned["recovery"]["target_reacquired"] is True


def test_g2_2_1_web_hidden_obstacle_recovery_invalidates_assumption() -> None:
    controller = WebDemoController()
    controller.load_demo("g2_2_1_hidden_obstacle_recovery")
    planned = controller.run_cycle()

    assert _g2_2_cell(planned, 3, 2)["observed_occupancy"] == "unknown"
    assert planned["recovery"]["invalidated_poses"] == []

    scanned = controller.g2_2_execute_one_step()

    assert scanned["action_result"]["action_type"] == "scan"
    assert _g2_2_cell(scanned, 3, 2)["observed_occupancy"] == "occupied"
    assert scanned["recovery"]["invalidated_poses"] == [{"x": 3, "y": 2}]
    assert all(step["to_pose"] != {"x": 3, "y": 2} for step in scanned["plan"]["steps"])


def test_g2_3_web_controller_exposes_side_by_side_model_comparison() -> None:
    controller = WebDemoController()
    state = controller.load_demo("g2_3_model_comparison")

    assert state["schema"] == "nowmind.g2_3.web_state.v1"
    assert state["world_event_available"] is False

    comparison = state["g2_3_comparison"]
    rows = comparison["comparisons"]
    conditions = {row["condition"] for row in rows}
    model_configs = {json.dumps(row["model_config"], sort_keys=True) for row in rows}

    assert {"N_NOWMIND_STRUCTURED", "C_CHRONOLOGICAL"}.issubset(conditions)
    assert len(model_configs) == 1
    assert comparison["expected_hidden_by_default"]["answer"] == "cell:4,2"
    assert all("representation" in row["representation"] for row in rows)
    assert any(badge["label"] == "Evaluator truth" for badge in state["success_badges"])


def test_history_deletion_reruns_current_now_not_previous_now(monkeypatch) -> None:
    controller = WebDemoController()
    controller.run_cycle()
    previous_now = controller.current_now
    controller.apply_demo_a_move()
    controller.run_cycle()
    current_now = controller.current_now
    calls = []

    def fake_answer(now, query):
        calls.append((now, query))
        return Answer(TruthStatus.TRUE, 1.0, query)

    monkeypatch.setattr(web_controller, "runtime_answer", fake_answer)
    controller.delete_history_and_rerun()

    assert previous_now is not current_now
    assert calls[-1][0] is current_now
    assert calls[-1][0] is not previous_now
    assert controller.external_history == []
    assert "not a cognitive input" in (controller.last_history_firewall_message or "")


def test_external_history_deletion_does_not_affect_current_answer() -> None:
    controller = WebDemoController()
    controller.run_cycle()
    before = controller.current_answer

    state = controller.delete_history_and_rerun()

    assert before is not None
    assert controller.current_answer is not None
    assert controller.current_answer.status is before.status
    assert controller.current_answer.confidence == before.confidence
    assert state["external_history"] == []
    assert "not a cognitive input" in state["history_firewall_message"]


def test_demo_a_history_contains_runtime_data_for_before_after_visuals() -> None:
    controller = WebDemoController()
    first_state = controller.run_cycle()
    controller.apply_demo_a_move()
    second_state = controller.run_cycle()

    assert first_state["external_history"][0]["now"]["observed_relations"][0][
        "relation_type"
    ] == "left_of"
    assert len(second_state["external_history"]) == 2
    assert second_state["external_history"][1]["now"]["observed_relations"][0][
        "relation_type"
    ] == "right_of"
    assert second_state["stale_red_left_blue_present"] is False


def test_demo_a_move_event_toggles_visible_world_position() -> None:
    controller = WebDemoController()
    first_state = controller.run_cycle()

    assert first_state["world"]["relations"][0]["relation_type"] == "left_of"
    assert first_state["move_event_label"] == "Move red_cube right"

    moved_right = controller.apply_demo_a_move()

    assert moved_right["world"]["relations"][0]["relation_type"] == "right_of"
    assert moved_right["current_now"]["observed_relations"][0]["relation_type"] == "left_of"
    assert moved_right["world_changed_since_now"] is True
    assert moved_right["move_event_label"] == "Move red_cube left"

    second_state = controller.run_cycle()

    assert second_state["current_now"]["observed_relations"][0]["relation_type"] == "right_of"
    assert second_state["world_changed_since_now"] is False

    moved_left = controller.apply_demo_a_move()

    assert moved_left["world"]["relations"][0]["relation_type"] == "left_of"
    assert moved_left["world_changed_since_now"] is True
    assert moved_left["move_event_label"] == "Move red_cube right"


def test_inference_demo_exposes_three_objects_for_visual_scene() -> None:
    controller = WebDemoController()
    controller.load_demo("inference")
    state = controller.run_cycle()

    entity_ids = {entity["entity_id"] for entity in state["current_now"]["entities"]}
    observed = {
        (
            relation["source_id"],
            relation["relation_type"],
            relation["target_id"],
        )
        for relation in state["current_now"]["observed_relations"]
    }

    assert entity_ids == {"a", "b", "c"}
    assert ("a", "left_of", "b") in observed
    assert ("b", "left_of", "c") in observed


def test_inference_demo_world_event_breaks_and_restores_inference() -> None:
    controller = WebDemoController()
    controller.load_demo("inference")

    first_state = controller.run_cycle()

    assert first_state["current_answer"]["status"] == "true"
    assert first_state["move_event_label"] == "Break inference chain"
    assert first_state["world_event_available"] is True

    broken_world = controller.apply_demo_world_event()

    assert broken_world["world_changed_since_now"] is True
    assert broken_world["move_event_label"] == "Restore inference chain"
    assert {
        (relation["source_id"], relation["relation_type"], relation["target_id"])
        for relation in broken_world["world"]["relations"]
    } == {("a", "left_of", "b")}
    assert broken_world["current_answer"]["status"] == "true"

    broken_now = controller.run_cycle()

    assert broken_now["world_changed_since_now"] is False
    assert broken_now["current_answer"]["status"] == "unknown"
    assert broken_now["current_answer"]["confidence"] == 0.0

    restored_world = controller.apply_demo_world_event()

    assert restored_world["world_changed_since_now"] is True
    assert restored_world["move_event_label"] == "Break inference chain"

    restored_now = controller.run_cycle()

    assert restored_now["current_answer"]["status"] == "true"
    assert restored_now["world_changed_since_now"] is False


def test_containment_demo_world_event_breaks_and_restores_inference() -> None:
    controller = WebDemoController()
    controller.load_demo("containment")

    first_state = controller.run_cycle()

    assert first_state["current_answer"]["status"] == "true"
    assert first_state["move_event_label"] == "Break containment chain"
    assert first_state["world_event_available"] is True

    broken_world = controller.apply_demo_world_event()

    assert broken_world["world_changed_since_now"] is True
    assert broken_world["move_event_label"] == "Restore containment chain"
    assert {
        (relation["source_id"], relation["relation_type"], relation["target_id"])
        for relation in broken_world["world"]["relations"]
    } == {("key", "inside", "box")}
    assert broken_world["current_answer"]["status"] == "true"

    broken_now = controller.run_cycle()

    assert broken_now["world_changed_since_now"] is False
    assert broken_now["current_answer"]["status"] == "unknown"
    assert broken_now["current_answer"]["confidence"] == 0.0

    restored_world = controller.apply_demo_world_event()

    assert restored_world["world_changed_since_now"] is True
    assert restored_world["move_event_label"] == "Break containment chain"

    restored_now = controller.run_cycle()

    assert restored_now["current_answer"]["status"] == "true"
    assert restored_now["world_changed_since_now"] is False


def test_contradiction_demo_world_event_resolves_and_restores_conflict() -> None:
    controller = WebDemoController()
    controller.load_demo("contradiction")

    first_state = controller.run_cycle()

    assert first_state["current_answer"]["status"] == "contradictory"
    assert first_state["move_event_label"] == "Resolve contradiction"
    assert first_state["world_event_available"] is True

    resolved_world = controller.apply_demo_world_event()

    assert resolved_world["world_changed_since_now"] is True
    assert resolved_world["move_event_label"] == "Restore contradiction"
    assert {
        (relation["source_id"], relation["relation_type"], relation["target_id"])
        for relation in resolved_world["world"]["relations"]
    } == {("red_cube", "left_of", "blue_cube")}
    assert resolved_world["current_answer"]["status"] == "contradictory"

    resolved_now = controller.run_cycle()

    assert resolved_now["world_changed_since_now"] is False
    assert resolved_now["current_answer"]["status"] == "true"
    assert resolved_now["current_now"]["validation"]["is_valid"] is True

    restored_world = controller.apply_demo_world_event()

    assert restored_world["world_changed_since_now"] is True
    assert restored_world["move_event_label"] == "Resolve contradiction"

    restored_now = controller.run_cycle()

    assert restored_now["current_answer"]["status"] == "contradictory"
    assert restored_now["current_now"]["validation"]["is_valid"] is False
    assert restored_now["world_changed_since_now"] is False


def test_web_api_serves_state_and_runs_cycle() -> None:
    controller = WebDemoController()
    server = create_server("127.0.0.1", 0, controller)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        port = server.server_address[1]
        base = f"http://127.0.0.1:{port}"
        with urlopen(f"{base}/api/state", timeout=5) as response:
            state = json.loads(response.read().decode("utf-8"))
        assert state["schema"] == "nowmind.g1.web_state.v1"
        assert state["current_now"] is None

        request = Request(
            f"{base}/api/run-cycle",
            data=b"{}",
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=5) as response:
            state = json.loads(response.read().decode("utf-8"))
        assert state["current_now"]["cycle_id"] == 1
        assert state["current_answer"]["status"] == "true"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
