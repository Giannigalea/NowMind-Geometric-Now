# G2.3 Model Integration Specification

## Principle

The LLM is a replaceable reasoning faculty, not NowMind identity.

It does not own world truth, observation, memory, or action execution.

## Required backends

- `MockModelBackend`
- `OllamaBackend`

No cloud backend in G2.3.

## Representation builders

Implement deterministic:
- `NowMindRepresentationBuilder`
- `ChronologicalRepresentationBuilder`
- `CurrentOnlyRepresentationBuilder`

All consume the same admissible trial information source.

## No evaluator leakage

Builders cannot access:
- expected answer;
- hidden ground truth;
- correctness labels;
- family-specific solution hints.

## Model proposal

Model output may become:
- proposed answer;
- proposed action;
- proposed explanation.

It may not become:
- OBSERVED_NOW;
- MemoryTrace;
- direct WorldState mutation.

## Validation

Keep raw proposal and validated outcome separate in storage and metrics.
