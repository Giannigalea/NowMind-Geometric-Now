# G2.2 Limitations

- The world is a synthetic deterministic grid, not real perception.
- Sensor confidence and false positive/false negative cases are evaluator
  controls, not calibrated physical sensor models.
- Planning is symbolic A* plus a documented verification heuristic, not learned
  policy search.
- Memory reconstructions are compact propositions, not rich episodic memory.
- Future hypotheses are typed uncertain records, not a probabilistic simulator.
- `SCAN` is a simplified information action; it does not model real camera,
  attention, orientation, or active sensing physics.
- The chronological baseline is intentionally strong and may match or beat
  NowMind on accuracy or scaling.
- The oracle is an evaluator upper bound, not a cognitive competitor.
- The browser demo is an inspector for research behavior, not a cognitive UI.
- G2.2 does not implement identity, dreaming, L3 Veto Gate, LLM integration,
  embeddings, vector retrieval, cloud services, external APIs, camera/microphone
  input, autonomous OS tools, self-modification, or a quantum mechanism.

Passing G2.2 tests and benchmarks shows that the software preserves the stated
epistemic/source invariants under these synthetic conditions. It is not evidence
that the system is conscious, self-aware, sentient, or alive.
