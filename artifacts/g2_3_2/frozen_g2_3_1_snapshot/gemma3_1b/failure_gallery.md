# gemma3:1b Failure Gallery

This fallback model did not reach G2.3.1 calibration. The required local JSON smoke test failed before any benchmark prompt was run.

Representative failure:

```text
llama-server process has terminated: exit status 0xe06d7363
```

A smaller `num_ctx=1024` attempt also failed with:

```text
llama_init_from_model: failed to initialize the context: std::bad_alloc
```

No N/C/R benchmark rows exist for this model, and no representation-effect claim can be made.
