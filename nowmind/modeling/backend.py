from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import re
from time import perf_counter
from typing import Any, Mapping, Protocol
from urllib import error, request
from urllib.parse import urlparse


MODEL_PROPOSAL_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "status": {
            "type": "string",
            "enum": [
                "TRUE",
                "FALSE",
                "UNKNOWN",
                "CONTRADICTORY",
                "ANSWER",
                "ACTION",
            ],
        },
        "answer": {"type": ["string", "null"]},
        "source_used": {
            "type": "string",
            "enum": [
                "observed_now",
                "inferred_now",
                "reconstructed_memory",
                "hypothetical_future",
                "mixed",
                "none",
            ],
        },
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "action": {"type": ["string", "null"]},
        "assumptions": {"type": "array", "items": {"type": "string"}},
        "explanation": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "status",
        "answer",
        "source_used",
        "confidence",
        "action",
        "assumptions",
        "explanation",
    ],
}


def estimate_tokens(text: str) -> int:
    return max(1, (len(text) + 3) // 4)


def schema_hash(schema: Mapping[str, Any] | None) -> str | None:
    if schema is None:
        return None
    return hashlib.sha256(
        json.dumps(schema, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True, slots=True)
class ModelRequest:
    prompt: str
    system_instruction: str
    model: str
    temperature: float = 0.0
    top_p: float = 1.0
    seed: int | None = 20260823
    response_format: str = "json"
    response_schema: Mapping[str, Any] | None = None
    context_size: int | None = None
    num_predict: int | None = None
    think: bool | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def config_dict(self) -> dict[str, Any]:
        return {
            "model": self.model,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "seed": self.seed,
            "response_format": self.response_format,
            "response_schema_hash": schema_hash(self.response_schema),
            "context_size": self.context_size,
            "num_predict": self.num_predict,
            "think": self.think,
        }


@dataclass(frozen=True, slots=True)
class ModelResponse:
    raw_text: str
    model: str
    backend: str
    latency_ms: float
    input_token_estimate: int
    output_token_estimate: int
    config: Mapping[str, Any]
    error: str | None = None
    provider_metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "raw_text": self.raw_text,
            "model": self.model,
            "backend": self.backend,
            "latency_ms": self.latency_ms,
            "input_token_estimate": self.input_token_estimate,
            "output_token_estimate": self.output_token_estimate,
            "config": dict(self.config),
            "error": self.error,
            "provider_metadata": dict(self.provider_metadata),
        }


class ModelBackend(Protocol):
    def generate(self, request: ModelRequest) -> ModelResponse:
        ...


class MockModelBackend:
    """Deterministic local backend for tests and no-model environments."""

    backend_name = "mock"

    def __init__(
        self,
        model: str = "mock-deterministic-g2.3",
        context_size: int = 100000,
        invalid_first: bool = False,
    ) -> None:
        self.model = model
        self.context_size = context_size
        self.invalid_first = invalid_first
        self._call_count = 0

    def manifest(self) -> dict[str, Any]:
        return {
            "backend": self.backend_name,
            "model": self.model,
            "digest": "local-deterministic-mock",
            "context_size": self.context_size,
            "temperature": 0.0,
            "top_p": 1.0,
            "seed": 20260823,
        }

    def generate(self, request: ModelRequest) -> ModelResponse:
        started = perf_counter()
        self._call_count += 1
        if self.invalid_first and self._call_count == 1:
            raw = "{invalid json"
        else:
            representation = _extract_representation(request.prompt)
            raw = json.dumps(_mock_answer(representation), sort_keys=True)
        return ModelResponse(
            raw_text=raw,
            model=request.model or self.model,
            backend=self.backend_name,
            latency_ms=(perf_counter() - started) * 1000.0,
            input_token_estimate=estimate_tokens(
                request.system_instruction + "\n" + request.prompt
            ),
            output_token_estimate=estimate_tokens(raw),
            config=request.config_dict(),
        )


class OllamaBackend:
    backend_name = "ollama"

    def __init__(
        self,
        model: str,
        base_url: str = "http://127.0.0.1:11434",
        context_size: int = 2048,
        num_predict: int = 256,
        response_schema: Mapping[str, Any] | None = None,
        think: bool | None = None,
        timeout_seconds: int = 180,
    ) -> None:
        parsed = urlparse(base_url)
        if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
            raise ValueError("G2.3 OllamaBackend must use a localhost HTTP endpoint")
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.context_size = context_size
        self.num_predict = num_predict
        self.response_schema = response_schema or MODEL_PROPOSAL_JSON_SCHEMA
        self.think = think if think is not None else _default_think_for_model(model)
        self.timeout_seconds = timeout_seconds

    def manifest(self) -> dict[str, Any]:
        return {
            "backend": self.backend_name,
            "model": self.model,
            "base_url": self.base_url,
            "api_path": "/api/chat",
            "context_size": self.context_size,
            "num_predict": self.num_predict,
            "temperature": 0.0,
            "top_p": 1.0,
            "seed": 20260823,
            "response_format": "json_schema",
            "response_schema_hash": schema_hash(self.response_schema),
            "think": self.think,
        }

    def generate(self, request_obj: ModelRequest) -> ModelResponse:
        started = perf_counter()
        model = request_obj.model or self.model
        response_schema = request_obj.response_schema or self.response_schema
        context_size = request_obj.context_size or self.context_size
        num_predict = request_obj.num_predict or self.num_predict
        think = request_obj.think
        if think is None:
            think = self.think if self.think is not None else _default_think_for_model(model)
        config = {
            **request_obj.config_dict(),
            "model": model,
            "context_size": context_size,
            "num_predict": num_predict,
            "think": think,
            "response_format": "json_schema" if response_schema else request_obj.response_format,
            "response_schema_hash": schema_hash(response_schema),
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": request_obj.system_instruction},
                {"role": "user", "content": request_obj.prompt},
            ],
            "stream": False,
            "format": response_schema
            if response_schema
            else ("json" if request_obj.response_format == "json" else ""),
            "options": {
                "temperature": request_obj.temperature,
                "top_p": request_obj.top_p,
                "num_ctx": context_size,
                "num_predict": num_predict,
            },
        }
        if request_obj.seed is not None:
            payload["options"]["seed"] = request_obj.seed
        if think is not None:
            payload["think"] = think
        data = json.dumps(payload).encode("utf-8")
        req = request.Request(
            f"{self.base_url}/api/chat",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        provider_metadata: dict[str, Any] = {"api_path": "/api/chat"}
        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
            message = body.get("message", {})
            raw = str(message.get("content", "")) if isinstance(message, dict) else ""
            provider_metadata.update(
                {
                    "raw_response": body,
                    "message_thinking_present": isinstance(message, dict)
                    and "thinking" in message,
                    "message_thinking_omitted_from_scoring": isinstance(message, dict)
                    and "thinking" in message,
                    "prompt_eval_count": body.get("prompt_eval_count"),
                    "eval_count": body.get("eval_count"),
                    "total_duration": body.get("total_duration"),
                    "load_duration": body.get("load_duration"),
                }
            )
            error_message = None
        except error.HTTPError as exc:  # pragma: no cover - depends on local Ollama.
            error_body = exc.read().decode("utf-8", errors="replace")
            raw = ""
            error_message = f"HTTP {exc.code}: {error_body}"
            provider_metadata.update({"http_status": exc.code, "error_body": error_body})
        except Exception as exc:  # pragma: no cover - depends on local Ollama.
            raw = ""
            error_message = str(exc)
        input_tokens = _provider_count(provider_metadata, "prompt_eval_count")
        output_tokens = _provider_count(provider_metadata, "eval_count")
        return ModelResponse(
            raw_text=raw,
            model=model,
            backend=self.backend_name,
            latency_ms=(perf_counter() - started) * 1000.0,
            input_token_estimate=input_tokens
            if input_tokens is not None
            else estimate_tokens(request_obj.system_instruction + "\n" + request_obj.prompt),
            output_token_estimate=output_tokens if output_tokens is not None else estimate_tokens(raw),
            config=config,
            error=error_message,
            provider_metadata=provider_metadata,
        )


class OpenRouterBackend:
    backend_name = "openrouter"

    def __init__(
        self,
        model: str,
        *,
        provider: str | None = None,
        timeout_seconds: int = 180,
        api_key_env: str = "OPENROUTER_API_KEY",
        allow_fallbacks: bool = False,
        require_parameters: bool = True,
        data_collection: str = "deny",
        native_json_schema: bool = True,
        reasoning_config: Mapping[str, Any] | None = None,
        context_size: int | None = None,
    ) -> None:
        if model == "openrouter/free" or model.endswith("/free"):
            raise ValueError("G2.3.3 requires exact free model IDs, not openrouter/free")
        self.model = model
        self.provider = provider
        self.timeout_seconds = timeout_seconds
        self.api_key_env = api_key_env
        self.allow_fallbacks = allow_fallbacks
        self.require_parameters = require_parameters
        self.data_collection = data_collection
        self.native_json_schema = native_json_schema
        self.reasoning_config = dict(reasoning_config or {"exclude": True})
        self.context_size = context_size
        self.endpoint = "https://openrouter.ai/api/v1/chat/completions"

    def manifest(self) -> dict[str, Any]:
        return {
            "backend": self.backend_name,
            "model": self.model,
            "endpoint": self.endpoint,
            "provider": self.provider,
            "allow_fallbacks": self.allow_fallbacks,
            "require_parameters": self.require_parameters,
            "data_collection": self.data_collection,
            "temperature": 0.0,
            "top_p": 1.0,
            "seed": 20260823,
            "response_format": "json_schema" if self.native_json_schema else "prompt_only_json",
            "response_schema_hash": schema_hash(MODEL_PROPOSAL_JSON_SCHEMA),
            "reasoning": self.reasoning_config,
            "context_size": self.context_size,
        }

    def generate(self, request_obj: ModelRequest) -> ModelResponse:
        started = perf_counter()
        model = request_obj.model or self.model
        response_schema = request_obj.response_schema or MODEL_PROPOSAL_JSON_SCHEMA
        config = {
            **request_obj.config_dict(),
            "model": model,
            "response_format": "json_schema" if self.native_json_schema else "prompt_only_json",
            "response_schema_hash": schema_hash(response_schema),
            "provider": self.provider,
            "allow_fallbacks": self.allow_fallbacks,
            "require_parameters": self.require_parameters,
            "data_collection": self.data_collection,
            "native_json_schema": self.native_json_schema,
            "reasoning": self.reasoning_config,
            "context_size": request_obj.context_size or self.context_size,
        }
        provider_config: dict[str, Any] = {
            "allow_fallbacks": self.allow_fallbacks,
            "require_parameters": self.require_parameters,
            "data_collection": self.data_collection,
        }
        if self.provider:
            provider_config["order"] = [self.provider]
            provider_config["only"] = [self.provider]
        payload: dict[str, Any] = {
            "model": model,
            "messages": [
                {"role": "system", "content": request_obj.system_instruction},
                {"role": "user", "content": request_obj.prompt},
            ],
            "stream": False,
            "temperature": request_obj.temperature,
            "top_p": request_obj.top_p,
            "max_tokens": request_obj.num_predict or self._default_num_predict(),
            "provider": provider_config,
            "reasoning": self.reasoning_config,
        }
        if self.native_json_schema:
            payload["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": "nowmind_g23_model_proposal",
                    "strict": True,
                    "schema": response_schema,
                },
            }
        if request_obj.seed is not None:
            payload["seed"] = request_obj.seed
        data = json.dumps(payload).encode("utf-8")
        req = request.Request(
            self.endpoint,
            data=data,
            headers={
                "Authorization": f"Bearer {self._api_key()}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://local.nowmind.invalid",
                "X-Title": "NowMind G2.3.3 Free OpenRouter Replication",
            },
            method="POST",
        )
        provider_metadata: dict[str, Any] = {
            "endpoint": self.endpoint,
            "provider_request": provider_config,
        }
        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
            raw = _openrouter_message_content(body)
            provider_metadata.update(_openrouter_metadata(body))
            error_message = None
        except error.HTTPError as exc:  # pragma: no cover - depends on OpenRouter.
            error_body = _redact_sensitive_text(exc.read().decode("utf-8", errors="replace"))
            raw = ""
            error_message = f"HTTP {exc.code}: {error_body}"
            provider_metadata.update(
                {
                    "http_status": exc.code,
                    "error_body": error_body,
                    "rate_limited": exc.code == 429,
                }
            )
        except Exception as exc:  # pragma: no cover - depends on OpenRouter.
            raw = ""
            error_message = str(exc)
        usage = provider_metadata.get("usage", {})
        input_tokens = usage.get("prompt_tokens") if isinstance(usage, Mapping) else None
        output_tokens = usage.get("completion_tokens") if isinstance(usage, Mapping) else None
        return ModelResponse(
            raw_text=raw,
            model=model,
            backend=self.backend_name,
            latency_ms=(perf_counter() - started) * 1000.0,
            input_token_estimate=input_tokens
            if isinstance(input_tokens, int)
            else estimate_tokens(request_obj.system_instruction + "\n" + request_obj.prompt),
            output_token_estimate=output_tokens if isinstance(output_tokens, int) else estimate_tokens(raw),
            config=config,
            error=error_message,
            provider_metadata=provider_metadata,
        )

    def _api_key(self) -> str:
        import os

        value = os.environ.get(self.api_key_env)
        if value:
            return value
        raise RuntimeError(f"{self.api_key_env} is not set")

    @staticmethod
    def _default_num_predict() -> int:
        return 256


def _default_think_for_model(model: str) -> bool | None:
    return False if model.lower().startswith("qwen3") else None


def _provider_count(metadata: Mapping[str, Any], key: str) -> int | None:
    value = metadata.get(key)
    if isinstance(value, int):
        return value
    return None


def _openrouter_message_content(body: Mapping[str, Any]) -> str:
    choices = body.get("choices", [])
    if not isinstance(choices, list) or not choices:
        return ""
    choice = choices[0]
    if not isinstance(choice, Mapping):
        return ""
    message = choice.get("message", {})
    if not isinstance(message, Mapping):
        return ""
    content = message.get("content", "")
    return content if isinstance(content, str) else json.dumps(content, sort_keys=True)


def _redact_sensitive_text(text: str) -> str:
    text = re.sub(r"sk-or-v1-[A-Za-z0-9_-]+", "sk-or-v1-[REDACTED]", text)
    text = re.sub(r'"user_id"\s*:\s*"[^"]+"', '"user_id":"[REDACTED]"', text)
    return text


def _openrouter_metadata(body: Mapping[str, Any]) -> dict[str, Any]:
    choices = body.get("choices", [])
    choice = choices[0] if isinstance(choices, list) and choices else {}
    message = choice.get("message", {}) if isinstance(choice, Mapping) else {}
    usage = body.get("usage", {})
    return {
        "response_id": body.get("id"),
        "response_model": body.get("model"),
        "provider": body.get("provider"),
        "usage": usage if isinstance(usage, Mapping) else {},
        "finish_reason": choice.get("finish_reason") if isinstance(choice, Mapping) else None,
        "native_finish_reason": choice.get("native_finish_reason") if isinstance(choice, Mapping) else None,
        "message_reasoning_present": isinstance(message, Mapping) and "reasoning" in message,
        "message_reasoning_omitted_from_scoring": isinstance(message, Mapping) and "reasoning" in message,
    }


def _extract_representation(prompt: str) -> dict[str, Any]:
    marker = "REPRESENTATION_JSON:"
    index = prompt.rfind(marker)
    if index < 0:
        return {}
    raw = prompt[index + len(marker) :].strip()
    return json.loads(raw)


def _mock_answer(representation: Mapping[str, Any]) -> dict[str, Any]:
    query = dict(representation.get("query", {}))
    view = _view_from_representation(representation)
    kind = query.get("kind")
    if view["contradictory"]:
        return _proposal("CONTRADICTORY", "current evidence conflicts", "observed_now", 0.96)
    if kind == "current_location":
        subject = str(query.get("subject", ""))
        relation = str(query.get("relation", ""))
        current = _find_fact(view["current"], subject, relation, None)
        if current is None:
            return _proposal("UNKNOWN", "", "none", 0.1, ["current observation does not locate the subject"])
        return _proposal("ANSWER", str(current["target"]), str(current["source"]), 0.92)
    if kind == "current_relation":
        fact = _find_fact(
            view["current"],
            str(query.get("source", "")),
            str(query.get("relation", "")),
            str(query.get("target", "")),
        )
        if fact is None:
            return _proposal("UNKNOWN", "", "none", 0.2)
        return _proposal("TRUE", "true", str(fact["source"]), 0.9)
    if kind == "past_relation":
        fact = _find_fact(
            view["memory"],
            str(query.get("source", "")),
            str(query.get("relation", "")),
            str(query.get("target", "")),
        )
        if fact is None:
            return _proposal("UNKNOWN", "", "none", 0.2)
        return _proposal("TRUE", "true", "reconstructed_memory", 0.82)
    if kind == "future_relation":
        fact = _find_fact(
            view["future"],
            str(query.get("source", "")),
            str(query.get("relation", "")),
            str(query.get("target", "")),
        )
        if fact is None:
            return _proposal("UNKNOWN", "", "none", 0.2)
        return _proposal("TRUE", "true", "hypothetical_future", 0.72)
    if kind == "action_choice":
        for option in query.get("action_options", []):
            if option.get("recommended"):
                return _proposal(
                    "ACTION",
                    str(option["action"]),
                    str(option.get("source", "observed_now")),
                    0.86,
                    [str(item) for item in option.get("assumptions", [])],
                    str(option["action"]),
                )
        return _proposal("UNKNOWN", "", "none", 0.2)
    if kind == "source_explanation":
        source = str(query.get("expected_source_label", "observed_now"))
        return _proposal(
            "ANSWER",
            f"source={source}",
            source,
            0.84,
            explanation=[f"The supplied evidence labels this as {source}."],
        )
    return _proposal("UNKNOWN", "", "none", 0.0)


def _proposal(
    status: str,
    answer: str,
    source_used: str,
    confidence: float,
    assumptions: list[str] | None = None,
    action: str | None = None,
    explanation: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "status": status,
        "answer": answer,
        "source_used": source_used,
        "confidence": confidence,
        "action": action,
        "assumptions": assumptions or [],
        "explanation": explanation or ["Used only supplied labeled evidence."],
    }


def _view_from_representation(representation: Mapping[str, Any]) -> dict[str, Any]:
    condition = str(representation.get("condition", ""))
    current: list[dict[str, Any]] = []
    memory: list[dict[str, Any]] = []
    future: list[dict[str, Any]] = []
    contradictory = bool(representation.get("contradiction", False))
    if condition.startswith("N_"):
        current.extend(representation.get("observed_now", []))
        current.extend(representation.get("inferred_now", []))
        memory.extend(representation.get("reconstructed_memories", []))
        future.extend(representation.get("future_hypotheses", []))
    elif condition.startswith("C_"):
        current_cycle = representation.get("current_cycle_id")
        for record in representation.get("chronological_records", []):
            source = record.get("source", "")
            if record.get("contradiction"):
                contradictory = True
            if record.get("cycle_id") == current_cycle and source in {"observed_now", "inferred_now"}:
                current.append(record)
            elif source == "reconstructed_memory":
                memory.append(record)
            elif source == "hypothetical_future":
                future.append(record)
    else:
        current.extend(representation.get("observed_now", []))
        current.extend(representation.get("inferred_now", []))
    return {
        "current": current,
        "memory": memory,
        "future": future,
        "contradictory": contradictory,
    }


def _find_fact(
    facts: list[Mapping[str, Any]],
    source: str,
    relation: str,
    target: str | None,
) -> Mapping[str, Any] | None:
    for fact in facts:
        if str(fact.get("source_id")) != source:
            continue
        if str(fact.get("relation")) != relation:
            continue
        if target is not None and str(fact.get("target")) != target:
            continue
        return fact
    return None
