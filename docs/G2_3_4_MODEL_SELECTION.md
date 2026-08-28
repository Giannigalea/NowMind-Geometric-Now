# G2.3.4 Model Selection

Date: 2026-08-28T10:35:52.664290+00:00

Only exact OpenRouter `:free` text models with live input price `0` and output price `0` are eligible. `openrouter/free` remains rejected.

Provider privacy routing is relaxed to `data_collection=allow` only for synthetic benchmark prompts. Provider fallback remains disabled and provider pinning is required where the endpoint exposes a provider tag.

## Selected Priority Order

- `nvidia/nemotron-3-super-120b-a12b:free` family=nvidia provider=`nvidia` g2_3_3_status=`stopped_privacy_policy` price=input `0` output `0` structured=True
- `liquid/lfm-2.5-2.6b:free` family=liquid provider=`liquid/fp8` g2_3_3_status=`stopped_privacy_policy` price=input `0` output `0` structured=True
- `nvidia/nemotron-3-ultra-550b-a55b:free` family=nvidia provider=`nvidia` g2_3_3_status=`stopped_privacy_policy` price=input `0` output `0` structured=False
- `nvidia/nemotron-3.5-lightning:free` family=nvidia provider=`nvidia/nvfp4` g2_3_3_status=`stopped_privacy_policy` price=input `0` output `0` structured=False
- `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` family=nvidia provider=`nvidia` g2_3_3_status=`stopped_privacy_policy` price=input `0` output `0` structured=False
- `nvidia/nemotron-3.5-content-safety:free` family=nvidia provider=`nvidia` g2_3_3_status=`stopped_privacy_policy` price=input `0` output `0` structured=False
- `z-ai/glm-5.2:free` family=z-ai provider=`decart/fp4` g2_3_3_status=`paused_rate_limit` price=input `0` output `0` structured=True
- `inclusionai/ling-3.0-flash-fin:free` family=inclusionai provider=`novita` g2_3_3_status=`stopped_schema_invalid` price=input `0` output `0` structured=False
- `cohere/north-mini-code:free` family=cohere provider=`cohere` g2_3_3_status=`stopped_schema_invalid` price=input `0` output `0` structured=False
- `minimax/minimax-m3:free` family=minimax provider=`gmicloud/fp8` g2_3_3_status=`stopped_error` price=input `0` output `0` structured=True
- `dots-studio/dots-3-note-preview:free` family=dots-studio provider=`atlas-cloud/fp8` g2_3_3_status=`stopped_error` price=input `0` output `0` structured=True
- `google/gemma-4-26b-a4b-it:free` family=google provider=`google-ai-studio` g2_3_3_status=`stopped_error` price=input `0` output `0` structured=True
- `google/gemma-4-31b-it:free` family=google provider=`google-ai-studio` g2_3_3_status=`stopped_error` price=input `0` output `0` structured=True
- `minimax/minimax-m2.7:free` family=minimax provider=`gmicloud/fp8` g2_3_3_status=`stopped_error` price=input `0` output `0` structured=True
- `thinkingmachines/inkling-small:free` family=thinkingmachines provider=`thinkingmachines/nvfp4` g2_3_3_status=`stopped_error` price=input `0` output `0` structured=False
- `thinkingmachines/inkling:free` family=thinkingmachines provider=`thinkingmachines/nvfp4` g2_3_3_status=`stopped_error` price=input `0` output `0` structured=False
- `poolside/laguna-s-2.1:free` family=poolside provider=`poolside/fp4` g2_3_3_status=`stopped_error` price=input `0` output `0` structured=False
- `poolside/laguna-xs-2.1:free` family=poolside provider=`poolside/fp8` g2_3_3_status=`stopped_error` price=input `0` output `0` structured=False
