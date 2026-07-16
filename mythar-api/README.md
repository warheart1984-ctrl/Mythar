# Mythar Semantic API v1

The stable API contract is [openapi.yaml](./openapi.yaml). Run locally:

```powershell
$env:PYTHONPATH = '.\mythar-v0.2\src'
$env:MYTHAR_API_KEYS = 'development-key'
python -m mythar serve --host 0.0.0.0 --port 8080
```

Send `POST /v1/compile` with `X-API-Key`, `expression`, and optional `mode`. Set `MYTHAR_RATE_LIMIT` to override the default 60 requests/minute per client/API key.

The included Dockerfile is deployment-ready; publishing requires a hosting provider and credentials.
