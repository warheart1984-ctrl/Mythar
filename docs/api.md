# API Reference

`POST /v1/compile` compiles against frozen Mythar Core v0.2. `POST /v2/compile` compiles against v0.3.

```json
{"expression":"maia tila","mode":"strict"}
```

Send the API key in `X-API-Key`. A success response contains `api_version`, `ast`, `registry_refs`, `invariants`, `diagnostics`, and `valid`. See [OpenAPI v1](../mythar-api/openapi.yaml).
