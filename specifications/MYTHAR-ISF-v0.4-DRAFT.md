# Mythar ISF v0.4 — Intermediate Semantic Form

**Status:** Draft for ratification  
**Evidence class:** Specified  
**Applies to:** Mythar Compiler API v2  
**Purpose:** Define a stable, language-neutral semantic representation emitted after Mythar compilation and consumed by transducers and tools.

## Constitutional boundary

ISF is a semantic interchange contract, not a historical reconstruction claim and not a deployment architecture. It is the single semantic representation after successful compilation. This draft does not ratify new Mythar roots or alter the v0.3 registry.

## Required ISF v0.4 fields

```json
{
  "version": "0.4",
  "root": "ema",
  "canonical": true,
  "class": "proclamation",
  "domain": "speech",
  "intent": "declare",
  "operators": [],
  "arguments": [],
  "context": {"source_language": "mythar", "compiler_version": "v2", "line": 1, "column": 1},
  "metadata": {"confidence": 1.0, "notes": []}
}
```

`version`, `root`, `canonical`, `class`, `domain`, `intent`, `operators`, `arguments`, `context`, and `metadata` are required. Arguments are nested ISF nodes; v0.4 emits an empty list until clause-level argument roles are ratified. An unknown semantic profile is represented by `unclassified` / `unspecified` values and a metadata note, rather than invented meaning.

## Specified root profiles

| Root | Class | Domain | Intent |
| --- | --- | --- | --- |
| ema | proclamation | speech | declare |
| ma | existence | being | ground |
| la | illumination | truth | reveal |
| ka | power | time | test |
| tor | threshold | boundary | cross |
| ia | divinity | sacred | sanctify |
| fu | blessing | wind | carry |
| ra | proclamation | speech | speak |
| rum | collective | assembly | unite |

The table is specified language-engineering data for ISF v0.4. It is not evidence of historical etymology.

## Operators and transduction

Applied prefix and suffix operators are emitted in source application order through `operators`. The v0.4 API does not yet claim a complete sentence-generation grammar. A language transducer consumes ISF by mapping each root to target-language noun, verb, and adjective forms; reconstructed-language mappings MUST be labeled Hypothesized unless separately evidenced.

## API contract

`POST /v2/compile?format=isf` accepts the existing `expression` field and the `source` alias. A valid result retains the normal compilation fields and adds `isf`. Invalid input remains a `400` compilation result with diagnostics and no ISF object. The body field `format: "isf"` is supported as an equivalent to the query parameter.
