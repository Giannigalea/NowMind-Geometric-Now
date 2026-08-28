from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path
from urllib.error import HTTPError

import pytest
import nowmind.modeling.backend as backend_module

from nowmind.evaluation.g2_3_benchmark import (
    _run_condition,
    generate_trials,
)
from nowmind.modeling import (
    COMMON_SYSTEM_INSTRUCTION,
    ChronologicalRepresentationBuilder,
    CurrentOnlyRepresentationBuilder,
    MockModelBackend,
    ModelRequest,
    NowMindRepresentationBuilder,
    OllamaBackend,
    OpenRouterBackend,
    canonical_input_token_count,
    parse_model_output,
    validate_model_proposal,
)
from nowmind.modeling.proposal import ModelProposal
from scripts import run_g2_3_3_openrouter_replication as g233
from scripts import run_g2_3_4_provider_compatible_replication as g234


def test_g2_3_mock_backend_is_deterministic_and_json_parseable() -> None:
    trial = generate_trials(20260823, 1, "test", "mock")[0]
    representation = NowMindRepresentationBuilder().build(
        trial.facts,
        "A_EQUAL_INFORMATION",
    )
    request = ModelRequest(
        prompt=representation.prompt,
        system_instruction="Return JSON.",
        model="mock-deterministic-g2.3",
    )
    backend = MockModelBackend()

    first = backend.generate(request)
    second = backend.generate(request)

    assert first.raw_text == second.raw_text
    assert parse_model_output(first.raw_text).parse_success


def test_g2_3_ollama_backend_rejects_non_local_endpoint() -> None:
    with pytest.raises(ValueError):
        OllamaBackend("llama-test", base_url="https://example.com")


def test_g2_3_ollama_backend_uses_chat_schema_and_qwen_no_think(monkeypatch) -> None:
    captured = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return None

        def read(self) -> bytes:
            return json.dumps(
                {
                    "message": {
                        "role": "assistant",
                        "content": json.dumps(
                            {
                                "status": "ANSWER",
                                "answer": "box_b",
                                "source_used": "observed_now",
                                "confidence": 0.9,
                                "action": None,
                                "assumptions": [],
                                "explanation": ["structured final answer"],
                            }
                        ),
                        "thinking": "hidden reasoning not used for scoring",
                    },
                    "prompt_eval_count": 12,
                    "eval_count": 8,
                    "total_duration": 123,
                    "load_duration": 45,
                }
            ).encode("utf-8")

    def fake_urlopen(req, timeout):
        captured["url"] = req.full_url
        captured["timeout"] = timeout
        captured["payload"] = json.loads(req.data.decode("utf-8"))
        return FakeResponse()

    monkeypatch.setattr(backend_module.request, "urlopen", fake_urlopen)
    backend = OllamaBackend("qwen3:1.7b", context_size=2048, num_predict=64)

    response = backend.generate(
        ModelRequest(
            prompt="REPRESENTATION_JSON:\n{}",
            system_instruction="Use only supplied evidence.",
            model="qwen3:1.7b",
        )
    )

    payload = captured["payload"]
    assert captured["url"].endswith("/api/chat")
    assert payload["stream"] is False
    assert payload["think"] is False
    assert payload["format"]["required"] == [
        "status",
        "answer",
        "source_used",
        "confidence",
        "action",
        "assumptions",
        "explanation",
    ]
    assert payload["options"]["temperature"] == 0.0
    assert payload["options"]["num_ctx"] == 2048
    assert payload["options"]["num_predict"] == 64
    assert [message["role"] for message in payload["messages"]] == ["system", "user"]
    assert "prompt" not in payload
    assert "system" not in payload
    assert parse_model_output(response.raw_text).parse_success
    assert response.input_token_estimate == 12
    assert response.output_token_estimate == 8
    assert response.provider_metadata["message_thinking_present"] is True
    assert "hidden reasoning" not in response.raw_text


def test_g2_3_ollama_backend_omits_think_for_non_thinking_model(monkeypatch) -> None:
    captured = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return None

        def read(self) -> bytes:
            return json.dumps(
                {
                    "message": {
                        "role": "assistant",
                        "content": json.dumps(
                            {
                                "status": "UNKNOWN",
                                "answer": None,
                                "source_used": "none",
                                "confidence": 0.0,
                                "action": None,
                                "assumptions": [],
                                "explanation": [],
                            }
                        ),
                    }
                }
            ).encode("utf-8")

    def fake_urlopen(req, timeout):
        captured["payload"] = json.loads(req.data.decode("utf-8"))
        return FakeResponse()

    monkeypatch.setattr(backend_module.request, "urlopen", fake_urlopen)
    response = OllamaBackend("gemma3:1b").generate(
        ModelRequest("prompt", "system", "gemma3:1b")
    )
    parsed = parse_model_output(response.raw_text)

    assert "think" not in captured["payload"]
    assert parsed.parse_success
    assert parsed.proposal is not None
    assert parsed.proposal.answer == ""


def test_g2_3_ollama_backend_preserves_http_error_body(monkeypatch) -> None:
    def fake_urlopen(req, timeout):
        raise HTTPError(
            req.full_url,
            500,
            "Internal Server Error",
            hdrs=None,
            fp=BytesIO(b'{"error":"failed to allocate buffer"}'),
        )

    monkeypatch.setattr(backend_module.request, "urlopen", fake_urlopen)

    response = OllamaBackend("qwen3:1.7b").generate(
        ModelRequest("prompt", "system", "qwen3:1.7b")
    )

    assert response.raw_text == ""
    assert response.error is not None
    assert "failed to allocate buffer" in response.error
    assert response.provider_metadata["http_status"] == 500
    assert "failed to allocate buffer" in response.provider_metadata["error_body"]


def test_g2_3_3_openrouter_backend_rejects_random_free_router() -> None:
    with pytest.raises(ValueError):
        OpenRouterBackend("openrouter/free")


def test_g2_3_3_openrouter_backend_request_shape_and_secret_redaction(monkeypatch) -> None:
    captured = {}
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-v1-test-secret-not-real")

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return None

        def read(self) -> bytes:
            return json.dumps(
                {
                    "id": "gen-test",
                    "model": "z-ai/glm-5.2:free",
                    "provider": "FreeProvider",
                    "choices": [
                        {
                            "message": {
                                "role": "assistant",
                                "content": json.dumps(
                                    {
                                        "status": "UNKNOWN",
                                        "answer": None,
                                        "source_used": "none",
                                        "confidence": 0.0,
                                        "action": None,
                                        "assumptions": [],
                                        "explanation": ["no current fact"],
                                    }
                                ),
                            },
                            "finish_reason": "stop",
                        }
                    ],
                    "usage": {"prompt_tokens": 10, "completion_tokens": 7},
                }
            ).encode("utf-8")

    def fake_urlopen(req, timeout):
        captured["url"] = req.full_url
        captured["headers"] = dict(req.header_items())
        captured["payload"] = json.loads(req.data.decode("utf-8"))
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr(backend_module.request, "urlopen", fake_urlopen)

    response = OpenRouterBackend("z-ai/glm-5.2:free").generate(
        ModelRequest("REPRESENTATION_JSON:\n{}", "Use only supplied evidence.", "z-ai/glm-5.2:free")
    )

    payload = captured["payload"]
    assert captured["url"] == "https://openrouter.ai/api/v1/chat/completions"
    assert payload["stream"] is False
    assert payload["provider"]["allow_fallbacks"] is False
    assert payload["provider"]["require_parameters"] is True
    assert payload["provider"]["data_collection"] == "deny"
    assert payload["reasoning"] == {"exclude": True}
    assert payload["response_format"]["type"] == "json_schema"
    assert [message["role"] for message in payload["messages"]] == ["system", "user"]
    assert response.provider_metadata["provider"] == "FreeProvider"
    assert response.input_token_estimate == 10
    assert response.output_token_estimate == 7
    serialized = json.dumps(response.to_dict())
    assert "sk-or-v1-test-secret-not-real" not in serialized


def test_g2_3_3_openrouter_prompt_only_json_keeps_provider_guardrails(monkeypatch) -> None:
    captured = {}
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-v1-test-secret-not-real")

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return None

        def read(self) -> bytes:
            return json.dumps(
                {
                    "id": "gen-test-2",
                    "model": "cohere/north-mini-code:free",
                    "choices": [
                        {
                            "message": {
                                "role": "assistant",
                                "content": json.dumps(
                                    {
                                        "status": "UNKNOWN",
                                        "answer": None,
                                        "source_used": "none",
                                        "confidence": 0.0,
                                        "action": None,
                                        "assumptions": [],
                                        "explanation": ["no current fact"],
                                    }
                                ),
                            },
                            "finish_reason": "stop",
                        }
                    ],
                    "usage": {"prompt_tokens": 11, "completion_tokens": 8},
                }
            ).encode("utf-8")

    def fake_urlopen(req, timeout):
        captured["payload"] = json.loads(req.data.decode("utf-8"))
        return FakeResponse()

    monkeypatch.setattr(backend_module.request, "urlopen", fake_urlopen)

    response = OpenRouterBackend(
        "cohere/north-mini-code:free",
        native_json_schema=False,
    ).generate(
        ModelRequest(
            "REPRESENTATION_JSON:\n{}",
            "Return only JSON matching the schema.",
            "cohere/north-mini-code:free",
        )
    )

    payload = captured["payload"]
    assert "response_format" not in payload
    assert payload["provider"]["allow_fallbacks"] is False
    assert payload["provider"]["require_parameters"] is True
    assert payload["provider"]["data_collection"] == "deny"
    assert payload["reasoning"] == {"exclude": True}
    assert response.config["response_format"] == "prompt_only_json"


def test_g2_3_3_free_model_price_gate_and_selection() -> None:
    paid = {
        "id": "paid/model",
        "pricing": {"prompt": "0.1", "completion": "0"},
        "architecture": {"output_modalities": ["text"]},
    }
    random_router = {
        "id": "openrouter/free",
        "pricing": {"prompt": "0", "completion": "0"},
        "architecture": {"output_modalities": ["text"]},
    }
    free = {
        "id": "z-ai/glm-5.2:free",
        "name": "GLM",
        "context_length": 256000,
        "pricing": {"prompt": "0", "completion": "0"},
        "architecture": {"input_modalities": ["text"], "output_modalities": ["text"]},
        "supported_parameters": ["response_format", "structured_outputs"],
    }

    assert not g233.is_free_text_model(paid)
    assert not g233.is_free_text_model(random_router)
    assert g233.is_free_text_model(free)
    selected = g233.select_models([g233.summarize_model(free)])
    assert selected[0]["id"] == "z-ai/glm-5.2:free"
    assert selected[0]["current_price"] == {"input": "0", "output": "0"}


def test_g2_3_3_resumable_duplicate_request_prevention(tmp_path) -> None:
    path = tmp_path / "rows.jsonl"
    key = g233.row_key(
        "z-ai/glm-5.2:free",
        "A_EQUAL_INFORMATION",
        "g2_3_eval_00000_temporal_present_vs_stale_memory",
        "N_NOWMIND_STRUCTURED",
    )
    g233.append_rows(
        path,
        [
            {
                "parse_success": True,
                "error": None,
                "g2_3_3": {
                    "row_key": key,
                    "output_schema_guard": {"passed": True, "issues": []},
                },
            }
        ],
    )

    assert g233.completed_keys(path) == {key}
    g233.append_rows(
        path,
        [{"parse_success": False, "error": None, "g2_3_3": {"row_key": "invalid-row"}}],
    )
    assert "invalid-row" not in g233.completed_keys(path)


def test_g2_3_3_regime_batch_stops_after_requested_new_rows(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(g233, "OUTPUT_DIR", tmp_path)
    monkeypatch.setattr(g233, "RUN_STATE_PATH", tmp_path / "run_state.json")
    calls = []

    def fake_run_cloud_condition(model, trial, regime, condition, timeout_seconds, num_predict):
        calls.append((model, trial.trial_id, regime, condition))
        return {
            "model": model,
            "backend": "openrouter",
            "regime": regime,
            "condition": condition,
            "trial": trial.public_dict(),
            "proposal_score": {"correct": 1},
            "validated_score": {"correct": 1},
            "parse_success": True,
            "repair_retry_count": 0,
            "latency_ms": 1.0,
            "input_tokens": 10,
            "output_tokens": 5,
            "context_overflow": False,
            "error": None,
            "model_response": {"provider_metadata": {"provider": "same-free-provider"}},
            "g2_3_3": {
                "row_key": g233.row_key(model, regime, trial.trial_id, condition),
                "synthetic_payload_guard": {"passed": True, "forbidden_hits": []},
                "output_schema_guard": {"passed": True, "issues": []},
            },
        }

    monkeypatch.setattr(g233, "run_cloud_condition", fake_run_cloud_condition)

    with pytest.raises(g233.BatchComplete):
        g233.run_regimes(
            "z-ai/glm-5.2:free",
            250,
            "evaluation",
            "g2_3_eval",
            1,
            1,
            request_batch_size=3,
        )

    rows = g233.read_rows(tmp_path / "z_ai_glm_5_2_free" / "a_equal_information_results.jsonl")
    assert len(calls) == 3
    assert len(rows) == 3
    assert json.loads((tmp_path / "run_state.json").read_text(encoding="utf-8"))["models"]["z-ai/glm-5.2:free"]["status"] == "paused_batch_complete"


def test_g2_3_3_regime_batch_skips_completed_rows(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(g233, "OUTPUT_DIR", tmp_path)
    monkeypatch.setattr(g233, "RUN_STATE_PATH", tmp_path / "run_state.json")
    model = "z-ai/glm-5.2:free"
    trial = generate_trials(20260824, 1, "evaluation", "g2_3_eval")[0]
    completed = {
        "model": model,
        "backend": "openrouter",
        "regime": "A_EQUAL_INFORMATION",
        "condition": "N_NOWMIND_STRUCTURED",
        "trial": trial.public_dict(),
        "proposal_score": {"correct": 1},
        "validated_score": {"correct": 1},
        "parse_success": True,
        "repair_retry_count": 0,
        "latency_ms": 1.0,
        "input_tokens": 10,
        "output_tokens": 5,
        "context_overflow": False,
        "error": None,
        "model_response": {"provider_metadata": {"provider": "same-free-provider"}},
        "g2_3_3": {
            "row_key": g233.row_key(model, "A_EQUAL_INFORMATION", trial.trial_id, "N_NOWMIND_STRUCTURED"),
            "output_schema_guard": {"passed": True, "issues": []},
        },
    }
    rows_path = tmp_path / "z_ai_glm_5_2_free" / "a_equal_information_results.jsonl"
    g233.append_rows(rows_path, [completed])
    calls = []

    def fake_run_cloud_condition(model, trial, regime, condition, timeout_seconds, num_predict):
        calls.append(condition)
        return {
            "model": model,
            "backend": "openrouter",
            "regime": regime,
            "condition": condition,
            "trial": trial.public_dict(),
            "proposal_score": {"correct": 1},
            "validated_score": {"correct": 1},
            "parse_success": True,
            "repair_retry_count": 0,
            "latency_ms": 1.0,
            "input_tokens": 10,
            "output_tokens": 5,
            "context_overflow": False,
            "error": None,
            "model_response": {"provider_metadata": {"provider": "same-free-provider"}},
            "g2_3_3": {
                "row_key": g233.row_key(model, regime, trial.trial_id, condition),
                "synthetic_payload_guard": {"passed": True, "forbidden_hits": []},
                "output_schema_guard": {"passed": True, "issues": []},
            },
        }

    monkeypatch.setattr(g233, "run_cloud_condition", fake_run_cloud_condition)

    with pytest.raises(g233.BatchComplete):
        g233.run_regimes(model, 1, "evaluation", "g2_3_eval", 1, 1, request_batch_size=1)

    assert calls == ["C_CHRONOLOGICAL"]


def test_g2_3_3_provider_matching_excludes_mismatched_pairs() -> None:
    base = {
        "model": "z-ai/glm-5.2:free",
        "regime": "A_EQUAL_INFORMATION",
        "trial": {"trial_id": "trial-1"},
        "proposal_score": {"correct": 1},
        "validated_score": {"correct": 1},
        "model_response": {"provider_metadata": {"provider": "A"}},
    }
    n = {**base, "condition": "N_NOWMIND_STRUCTURED"}
    c = {**base, "condition": "C_CHRONOLOGICAL", "model_response": {"provider_metadata": {"provider": "B"}}}

    pairwise = g233.pairwise_provider_safe([n, c])

    assert pairwise == {}


def test_g2_3_3_frozen_trial_hash_and_budget_are_unchanged() -> None:
    manifest = g233.frozen_protocol_manifest(250)
    trial_ids = [trial.trial_id for trial in generate_trials(20260824, 250, "evaluation", "g2_3_eval")]

    assert manifest["trial_ids"] == trial_ids
    assert manifest["trial_ids_hash"] == backend_module.hashlib.sha256(
        json.dumps(trial_ids, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    assert "1600" in manifest["regime_b_template_hash"] or manifest["regime_b_template_hash"]


def test_g2_3_3_synthetic_only_payload_guard_rejects_secrets() -> None:
    safe_row = {"representation": {"prompt": "REPRESENTATION_JSON: synthetic cube facts only"}}
    unsafe_row = {"representation": {"prompt": "sk-or-v1-secret"}}

    assert g233.synthetic_payload_guard(safe_row)["passed"]
    assert not g233.synthetic_payload_guard(unsafe_row)["passed"]


def test_g2_3_3_output_schema_guard_rejects_invalid_status() -> None:
    valid = {
        "parsed_output": {
            "status": "ANSWER",
            "source_used": "observed_now",
            "assumptions": [],
            "explanation": ["grounded"],
        }
    }
    invalid = {
        "parsed_output": {
            "status": "SUCCESS",
            "source_used": "observed_now",
            "assumptions": [],
            "explanation": ["grounded"],
        }
    }

    assert g233.output_schema_guard(valid)["passed"]
    assert not g233.output_schema_guard(invalid)["passed"]


def test_g2_3_4_openrouter_provider_pinning_allows_collection(monkeypatch) -> None:
    captured = {}
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-v1-test-secret-not-real")

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return None

        def read(self) -> bytes:
            return json.dumps(
                {
                    "id": "gen-test-g234",
                    "model": "nvidia/nemotron-3-super-120b-a12b:free",
                    "provider": "nvidia",
                    "choices": [
                        {
                            "message": {
                                "role": "assistant",
                                "content": json.dumps(
                                    {
                                        "status": "ANSWER",
                                        "answer": "box_b",
                                        "source_used": "observed_now",
                                        "confidence": 1.0,
                                        "action": None,
                                        "assumptions": [],
                                        "explanation": ["current observation wins"],
                                    }
                                ),
                            },
                            "finish_reason": "stop",
                        }
                    ],
                    "usage": {"prompt_tokens": 12, "completion_tokens": 9},
                }
            ).encode("utf-8")

    def fake_urlopen(req, timeout):
        captured["payload"] = json.loads(req.data.decode("utf-8"))
        return FakeResponse()

    monkeypatch.setattr(backend_module.request, "urlopen", fake_urlopen)

    OpenRouterBackend(
        "nvidia/nemotron-3-super-120b-a12b:free",
        provider="nvidia",
        data_collection="allow",
    ).generate(
        ModelRequest(
            "REPRESENTATION_JSON:\n{}",
            "Use only supplied evidence.",
            "nvidia/nemotron-3-super-120b-a12b:free",
        )
    )

    provider = captured["payload"]["provider"]
    assert provider["allow_fallbacks"] is False
    assert provider["require_parameters"] is True
    assert provider["data_collection"] == "allow"
    assert provider["order"] == ["nvidia"]
    assert provider["only"] == ["nvidia"]


def test_g2_3_4_output_schema_guard_is_raw_and_strict() -> None:
    valid = {
        "raw_output": json.dumps(
            {
                "status": "ANSWER",
                "answer": "box_b",
                "source_used": "observed_now",
                "confidence": 1.0,
                "action": None,
                "assumptions": [],
                "explanation": ["grounded"],
            }
        )
    }
    invalid = {
        "raw_output": json.dumps(
            {
                "status": "success",
                "answer": "box_b",
                "source_used": "observed_now",
                "confidence": 1.0,
                "action": None,
                "assumptions": [],
                "explanation": "grounded",
            }
        )
    }

    assert g234.output_schema_guard(valid)["passed"]
    guard = g234.output_schema_guard(invalid)
    assert not guard["passed"]
    assert "invalid_status" in guard["issues"]
    assert "invalid_explanation" in guard["issues"]


def test_g2_3_4_uses_separate_artifact_namespace_and_same_trial_hash() -> None:
    manifest = g234.frozen_protocol_manifest(250)
    trial_ids = [trial.trial_id for trial in generate_trials(20260824, 250, "evaluation", "g2_3_eval")]

    assert g234.OUTPUT_DIR.as_posix().endswith("artifacts/g2_3_4")
    assert g233.OUTPUT_DIR.as_posix().endswith("artifacts/g2_3_3")
    assert manifest["trial_ids"] == trial_ids
    assert manifest["regime_b_template_hash"]


def test_g2_3_4_reasoning_config_uses_lowest_supported_effort() -> None:
    rediscovery = {
        "free_models": [
            {
                "id": "nvidia/nemotron-3-super-120b-a12b:free",
                "reasoning": {"mandatory": False, "supported_efforts": ["medium", "low"]},
            },
            {
                "id": "thinkingmachines/inkling:free",
                "reasoning": {"mandatory": False, "supported_efforts": ["max", "low", "none"]},
            },
        ]
    }

    assert g234.reasoning_config_for_model(
        "nvidia/nemotron-3-super-120b-a12b:free",
        rediscovery,
    ) == {"effort": "low", "exclude": True}
    assert g234.reasoning_config_for_model(
        "thinkingmachines/inkling:free",
        rediscovery,
    ) == {"effort": "none", "exclude": True}


def test_g2_3_4_uses_live_endpoint_context_and_provider_display_name() -> None:
    rediscovery = {
        "free_models": [
            {
                "id": "liquid/lfm-2.5-2.6b:free",
                "context_length": 32000,
                "endpoints": [
                    {
                        "provider_tag": "liquid/fp8",
                        "provider_name": "Liquid",
                        "context_length": 65536,
                    }
                ],
            }
        ]
    }
    row = {"model_response": {"provider_metadata": {"provider": "Liquid"}}}

    assert g234.context_size_for_model("liquid/lfm-2.5-2.6b:free", rediscovery) == 65536
    assert g234.provider_matches(row, "liquid/lfm-2.5-2.6b:free", rediscovery)


def test_openrouter_backend_redacts_provider_user_ids() -> None:
    text = '{"user_id":"user_3F5AY8boz6KCXHiZ6POliD4yG7k","key":"sk-or-v1-real-looking"}'

    redacted = backend_module._redact_sensitive_text(text)

    assert "user_3F5AY8boz6KCXHiZ6POliD4yG7k" not in redacted
    assert "sk-or-v1-real-looking" not in redacted
    assert '"user_id":"[REDACTED]"' in redacted


def test_g2_3_3_plaintext_key_file_is_ignored_and_absent() -> None:
    root = Path(__file__).resolve().parents[2]
    ignore_text = (root / ".gitignore").read_text(encoding="utf-8")

    assert "*api*key*.txt" in ignore_text
    assert not (root / "open router api key.txt").exists()


def test_g2_3_representation_builders_share_admissible_fact_hash_and_hide_truth() -> None:
    trial = generate_trials(20260823, 1, "test", "fair")[0]
    n_rep = NowMindRepresentationBuilder().build(trial.facts, "A_EQUAL_INFORMATION")
    c_rep = ChronologicalRepresentationBuilder().build(trial.facts, "A_EQUAL_INFORMATION")
    r_rep = CurrentOnlyRepresentationBuilder().build(trial.facts, "A_EQUAL_INFORMATION")

    assert n_rep.fact_set_hash == c_rep.fact_set_hash == r_rep.fact_set_hash
    combined_prompt = "\n".join([n_rep.prompt, c_rep.prompt, r_rep.prompt])
    assert "expected_status" not in combined_prompt
    assert "expected_answer" not in combined_prompt
    assert "oracle" not in combined_prompt.lower()
    assert "ground_truth" not in combined_prompt


def test_g2_3_fixed_budget_builders_are_deterministic() -> None:
    trial = generate_trials(20260823, 6, "test", "budget")[-1]
    builder = ChronologicalRepresentationBuilder()

    first = builder.build(trial.facts, "B_FIXED_BUDGET", token_budget=1600)
    second = builder.build(trial.facts, "B_FIXED_BUDGET", token_budget=1600)

    assert first.prompt_hash == second.prompt_hash
    assert first.fact_set_hash == second.fact_set_hash


def test_g2_3_fixed_budget_counts_final_prompt_after_construction() -> None:
    trial = generate_trials(20260824, 250, "evaluation", "g2_3_eval")[-1]
    builders = (
        NowMindRepresentationBuilder(),
        ChronologicalRepresentationBuilder(),
        CurrentOnlyRepresentationBuilder(),
    )

    for builder in builders:
        representation = builder.build(trial.facts, "B_FIXED_BUDGET", token_budget=1600)

        assert representation.token_estimate == canonical_input_token_count(
            COMMON_SYSTEM_INSTRUCTION,
            representation.prompt,
        )
        assert representation.budget_accounting["final_input_token_estimate"] == representation.token_estimate
        assert representation.budget_accounting["budgeted_input_tokens"] <= 1600


def test_g2_3_fixed_budget_all_frozen_evaluation_prompts_fit_shared_counter() -> None:
    trials = generate_trials(20260824, 250, "evaluation", "g2_3_eval")
    builders = (
        NowMindRepresentationBuilder(),
        ChronologicalRepresentationBuilder(),
        CurrentOnlyRepresentationBuilder(),
    )

    over_budget = []
    for trial in trials:
        for builder in builders:
            representation = builder.build(trial.facts, "B_FIXED_BUDGET", token_budget=1600)
            if representation.budget_accounting["budgeted_input_tokens"] > 1600:
                over_budget.append((trial.trial_id, builder.condition))

    assert over_budget == []


def test_g2_3_fixed_budget_preserves_current_observation_and_query() -> None:
    trial = generate_trials(20260824, 250, "evaluation", "g2_3_eval")[-1]

    nowmind = NowMindRepresentationBuilder().build(trial.facts, "B_FIXED_BUDGET", token_budget=1600)
    chronological = ChronologicalRepresentationBuilder().build(trial.facts, "B_FIXED_BUDGET", token_budget=1600)

    assert nowmind.representation["query"] == trial.facts.query
    assert nowmind.representation["observed_now"] == list(trial.facts.observed_now)
    assert chronological.representation["query"] == trial.facts.query
    assert any(
        record.get("cycle_id") == trial.facts.current_cycle_id
        for record in chronological.representation["chronological_records"]
    )


def test_g2_3_fixed_budget_uses_no_evaluator_truth() -> None:
    trial = generate_trials(20260824, 250, "evaluation", "g2_3_eval")[-1]
    prompts = [
        NowMindRepresentationBuilder().build(trial.facts, "B_FIXED_BUDGET", token_budget=1600).prompt,
        ChronologicalRepresentationBuilder().build(trial.facts, "B_FIXED_BUDGET", token_budget=1600).prompt,
    ]
    combined_prompt = "\n".join(prompts)

    assert "expected_status" not in combined_prompt
    assert "expected_answer" not in combined_prompt
    assert "oracle" not in combined_prompt.lower()
    assert "ground_truth" not in combined_prompt


def test_g2_3_frozen_regime_a_result_is_unchanged() -> None:
    path = Path("artifacts/g2_3_1/qwen3_0_6b/g2_3_pairwise_n_vs_c.json")
    pairwise = json.loads(path.read_text(encoding="utf-8"))

    assert pairwise["qwen3:0.6b|A_EQUAL_INFORMATION|validated"] == {
        "c_better": 8,
        "n_better": 0,
        "tied": 242,
    }


def test_g2_3_frozen_final_trial_ids_are_reused() -> None:
    trial_ids = [
        trial.trial_id
        for trial in generate_trials(20260824, 250, "evaluation", "g2_3_eval")
    ]

    assert len(trial_ids) == 250
    assert trial_ids[0] == "g2_3_eval_00000_temporal_present_vs_stale_memory"
    assert trial_ids[-1] == "g2_3_eval_00249_action_safe_vs_conditional_route"
    assert len(set(trial_ids)) == 250


def test_g2_3_invalid_json_retry_is_recorded_identically() -> None:
    trial = generate_trials(20260823, 1, "test", "repair")[0]
    row = _run_condition(
        trial,
        "A_EQUAL_INFORMATION",
        "N_NOWMIND_STRUCTURED",
        MockModelBackend(invalid_first=True),
    )

    assert row["repair_retry_count"] == 1
    assert row["parse_success"] is True
    assert row["raw_output"].startswith("{")


def test_g2_3_fixed_budget_skips_over_budget_repair_prompt() -> None:
    trial = generate_trials(20260824, 250, "evaluation", "g2_3_eval")[-1]
    row = _run_condition(
        trial,
        "B_FIXED_BUDGET",
        "N_NOWMIND_STRUCTURED",
        MockModelBackend(invalid_first=True),
    )

    assert row["repair_retry_count"] == 0
    assert row["repair_skipped_budget_gate"] is True
    assert row["parse_success"] is False
    assert row["representation"]["budget_accounting"]["budgeted_input_tokens"] <= 1600


def test_g2_3_validator_rejects_source_violation_and_invalid_action() -> None:
    trial = generate_trials(20260823, 2, "test", "validator")[1]
    memory_as_current = ModelProposal(
        "ANSWER",
        "box_a",
        "reconstructed_memory",
        0.9,
        None,
        (),
        ("memory promoted to current",),
    )
    rejected = validate_model_proposal(memory_as_current, trial.facts)

    assert not rejected.accepted
    assert rejected.rejection_reason == "temporal_source_violation"

    action_trial = generate_trials(20260823, 12, "test", "validator")[-1]
    invalid_action = ModelProposal(
        "ACTION",
        "move_west",
        "observed_now",
        0.9,
        "move_west",
        (),
        (),
    )
    action_rejected = validate_model_proposal(invalid_action, action_trial.facts)

    assert not action_rejected.accepted
    assert action_rejected.rejection_reason == "invalid_action"


def test_g2_3_model_output_remains_proposal_not_observation_or_memorytrace() -> None:
    trial = generate_trials(20260823, 1, "test", "proposal")[0]
    row = _run_condition(
        trial,
        "A_EQUAL_INFORMATION",
        "N_NOWMIND_STRUCTURED",
        MockModelBackend(),
    )

    parsed = row["parsed_output"]
    assert parsed["source_used"] in {"observed_now", "inferred_now", "none", "mixed"}
    assert "OBSERVED_NOW" not in json.dumps(parsed)
    assert "MemoryTrace" not in json.dumps(parsed)
