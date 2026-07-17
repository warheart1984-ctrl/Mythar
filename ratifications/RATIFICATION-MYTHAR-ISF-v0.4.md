# Ratification Record — Mythar ISF v0.4

**Ratification status:** Ratified  
**Effective release:** v0.4.0  
**Date:** 2026-07-16  
**Authority:** Mythar repository stewardship

## Decision

The repository ratifies the [Mythar ISF v0.4 specification](../specifications/MYTHAR-ISF-v0.4.md) and its JSON schema as the stable semantic IR contract for Mythar Compiler API v2.

## Ratified surface

- Required ISF object fields and schema version `0.4`.
- Specified root profiles for `ema`, `ma`, `la`, `ka`, `tor`, `ia`, `fu`, `ra`, and `rum`.
- Operator preservation through `operators`.
- Source-language provenance through `context.source_language`.
- Deterministic unclassified-root behavior and invalid-input rejection.
- Versioned English, Spanish, and Standard Mandarin contract format governed by the Transduction Contract Standard.

## Conformance evidence

| Suite | Result |
| --- | --- |
| Mythar Core v0.2 | 101 / 101 passed |
| Mythar v0.3 | 5 / 5 passed |
| Mythar ISF v0.4 | 7 / 7 passed |

## Boundaries

ISF v0.4 does not ratify a complete clause argument grammar, unrestricted source-language parsing, historical reconstruction, or equivalence between Mandarin particles and Mythar operators. Those topics require future specification, evidence, and conformance work.

## Continuity and amendment

This ratification preserves v0.2 and v0.3 behavior. Any incompatible ISF change requires a later ISF version, migration record, conformance suite, and ratification; it MUST NOT silently mutate v0.4.
