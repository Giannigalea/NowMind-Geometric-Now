# qwen3:1.7b Failure Gallery

This model did not reach G2.3.1 calibration. The required local JSON smoke test failed before any benchmark prompt was run.

Representative failure:

```text
llama_init_from_model: failed to initialize the context: std::bad_alloc
```

Earlier attempts also failed with CPU/KV-cache allocation errors at `num_ctx` values from `40960` down to `1024`.

No N/C/R benchmark rows exist for this model, and no representation-effect claim can be made.
