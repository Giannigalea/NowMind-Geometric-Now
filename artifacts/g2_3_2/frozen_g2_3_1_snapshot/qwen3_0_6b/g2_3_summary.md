# G2.3 Model Integration Summary

- selected backend: `ollama`
- selected model: `qwen3:0.6b`
- final paired trial IDs: `250`
- invariants: `5 passed, 1 failed`
- local model prerequisite: `None`

## Aggregate Metrics
- `qwen3:0.6b|A_EQUAL_INFORMATION|C_CHRONOLOGICAL|validated` accuracy=0.148 source=0.172 parse=0.496
- `qwen3:0.6b|A_EQUAL_INFORMATION|N_NOWMIND_STRUCTURED|validated` accuracy=0.116 source=0.136 parse=0.496
- `qwen3:0.6b|A_EQUAL_INFORMATION|R_CURRENT_ONLY|validated` accuracy=0.116 source=0.176 parse=1.000
- `qwen3:0.6b|B_FIXED_BUDGET|C_CHRONOLOGICAL|validated` accuracy=0.116 source=0.152 parse=0.992
- `qwen3:0.6b|B_FIXED_BUDGET|N_NOWMIND_STRUCTURED|validated` accuracy=0.116 source=0.136 parse=0.996
- `qwen3:0.6b|B_FIXED_BUDGET|R_CURRENT_ONLY|validated` accuracy=0.116 source=0.192 parse=1.000
- `symbolic-nowmind-g2.3-reference|A_EQUAL_INFORMATION|S_SYMBOLIC_NOWMIND|validated` accuracy=1.000 source=1.000 parse=1.000
- `symbolic-nowmind-g2.3-reference|B_FIXED_BUDGET|S_SYMBOLIC_NOWMIND|validated` accuracy=1.000 source=1.000 parse=1.000

## Pairwise N vs C
- `qwen3:0.6b|A_EQUAL_INFORMATION|proposal` N=0 C=8 tied=242
- `qwen3:0.6b|B_FIXED_BUDGET|proposal` N=12 C=0 tied=238
- `qwen3:0.6b|A_EQUAL_INFORMATION|validated` N=0 C=8 tied=242
- `qwen3:0.6b|B_FIXED_BUDGET|validated` N=0 C=0 tied=250
