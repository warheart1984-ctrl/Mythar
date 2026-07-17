# API Reference

`POST /v1/compile` compiles against frozen Mythar Core v0.2. `POST /v2/compile` compiles against v0.3.

```json
{"expression":"maia tila","mode":"strict"}
```

Send the API key in `X-API-Key`. A success response contains `api_version`, `ast`, `registry_refs`, `invariants`, `diagnostics`, and `valid`. See [OpenAPI v1](../mythar-api/openapi.yaml).

## ISF v0.4 (draft)

`POST /v2/compile?format=isf` adds a language-neutral Intermediate Semantic Form to a successful v2 compilation. `source` is accepted as an alias for `expression`.

```json
{"source":"ja ema","mode":"strict","format":"isf"}
```

See the [ratified ISF v0.4 specification](../specifications/MYTHAR-ISF-v0.4.md). ISF semantic profiles are specified design data and are not claims of historical reconstruction.

## English translation

`POST /v2/compile?format=english` compiles valid Mythar to ISF v0.4 and returns the English contract output in `translation.text`. For example, `{"source":"ra","format":"english"}` returns `speak`; `{"source":"光","source_language":"zh","format":"english"}` returns `illuminate`.

The CLI is UTF-8 configured on Windows and can translate directly:

```powershell
python -m mythar translate ra
python -m mythar translate 光 --source-language zh
```

## Mandarin translation

`POST /v2/compile?format=mandarin` returns the Standard Mandarin contract output. The v0.4 English semantic-input adapter enables a defined vocabulary to travel through Mythar:

```powershell
python -m mythar translate light --source-language en --target-language zh
# 照亮

python -m mythar translate speak --source-language en --target-language zh
# 说话
```

This is exact-token semantic translation for the documented v0.4 vocabulary, not unrestricted English-to-Mandarin machine translation.
