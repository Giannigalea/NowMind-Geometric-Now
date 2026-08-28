# G2.3 Model Integration Summary

- selected backend: `ollama`
- selected model: `qwen3:1.7b`
- final paired trial IDs: `250`
- invariants: `5 passed, 1 failed`
- local model prerequisite: `None`

## Aggregate Metrics
- `qwen3:1.7b|A_EQUAL_INFORMATION|C_CHRONOLOGICAL|validated` accuracy=0.116 source=0.116 parse=0.000
- `qwen3:1.7b|A_EQUAL_INFORMATION|N_NOWMIND_STRUCTURED|validated` accuracy=0.116 source=0.116 parse=0.000
- `qwen3:1.7b|A_EQUAL_INFORMATION|R_CURRENT_ONLY|validated` accuracy=0.116 source=0.116 parse=0.000
- `qwen3:1.7b|B_FIXED_BUDGET|C_CHRONOLOGICAL|validated` accuracy=0.116 source=0.116 parse=0.000
- `qwen3:1.7b|B_FIXED_BUDGET|N_NOWMIND_STRUCTURED|validated` accuracy=0.116 source=0.116 parse=0.000
- `qwen3:1.7b|B_FIXED_BUDGET|R_CURRENT_ONLY|validated` accuracy=0.116 source=0.116 parse=0.000
- `symbolic-nowmind-g2.3-reference|A_EQUAL_INFORMATION|S_SYMBOLIC_NOWMIND|validated` accuracy=1.000 source=1.000 parse=1.000
- `symbolic-nowmind-g2.3-reference|B_FIXED_BUDGET|S_SYMBOLIC_NOWMIND|validated` accuracy=1.000 source=1.000 parse=1.000

## Pairwise N vs C
- `qwen3:1.7b|A_EQUAL_INFORMATION|proposal` N=0 C=0 tied=250
- `qwen3:1.7b|B_FIXED_BUDGET|proposal` N=0 C=0 tied=250
- `qwen3:1.7b|A_EQUAL_INFORMATION|validated` N=0 C=0 tied=250
- `qwen3:1.7b|B_FIXED_BUDGET|validated` N=0 C=0 tied=250
