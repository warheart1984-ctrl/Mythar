# Mythar Core v0.2

AST-only reference compiler and REST contract for the Mythar Constitutional Registry.

```powershell
cd mythar-v0.2
$env:PYTHONPATH = '.\src'
python -m mythar test
$env:MYTHAR_CONFORMANCE_ROOT = '..\mythar-registry\tests\v0.3'
python -m mythar test
python -m mythar compile 'ja la ra-fa ma tor wie'
python -m mythar serve --port 8080
```

`POST /v1/compile` accepts `{"expression":"ja tor","mode":"strict"}`. Successful requests return an AST, registry references, invariant results, and diagnostics. Invalid strict expressions return HTTP 400.

The parser accepts only registered roots and composites; it does not infer a root split from arbitrary spelling. Hyphenated operator notation is explicit (`ra-fa`, `ka-la-rum`).
