# G2.3 Locality Audit

## Allowed Backends

G2.3 defines:

- `MockModelBackend`, deterministic and fully local;
- `OllamaBackend`, HTTP calls to localhost only.

No OpenAI, Anthropic, Gemini, hosted inference, telemetry, or cloud model backend
is implemented.

## Ollama Endpoint Restriction

`OllamaBackend` accepts only HTTP endpoints whose host is:

- `127.0.0.1`;
- `localhost`;
- `::1`.

Non-local URLs raise `ValueError` before any request is made.

## No Automatic Download

G2.3 never downloads model weights. The manifest may inspect whether `ollama` is
available and list installed models, but missing models are reported as a local
runtime prerequisite rather than fetched.

## Proposal Boundary

Model output remains a `ModelProposal`. It cannot:

- write `OBSERVED_NOW`;
- create `MemoryTrace`;
- mutate `WorldState`;
- bypass symbolic validation;
- bypass action execution.

Tests cover these boundaries with `MockModelBackend`.

## Current Machine Result

`ollama list` was attempted for this task and failed because `ollama` was not
recognized on `PATH`. The generated G2.3 artifacts therefore use
`MockModelBackend` and record:

```text
Ollama is not installed on PATH; real local-model evaluation was not run.
```
