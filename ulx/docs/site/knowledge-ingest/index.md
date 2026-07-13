# Knowledge Ingest Mirror

This docs-site mirror reflects the formal Knowledge Ingest endpoint discovery surface without moving discovery logic into runtime behavior.

## Linked Artifacts
- [Knowledge Ingest Endpoint Specification](../../architecture/knowledge-ingest-endpoint-spec.md)
- [Knowledge Ingest Endpoint Manifest](../../../constitutional/knowledge-ingest.endpoint.json)
- [Knowledge Ingest Conformance Artifact](../../../constitutional/knowledge-ingest.conformance.json)

## Mirror Summary
- Documentation-first discovery surface
- Shared batch contract between CLI and daemon
- Informative endpoint manifest
- No governance reinterpretation

## What It Represents
- `POST /knowledge/ingest`
- Classified knowledge batch ingestion
- Shared batch processor for CLI and daemon
- Public projection emitted from the governed store

