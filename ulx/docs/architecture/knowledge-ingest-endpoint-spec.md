# Knowledge Ingest Endpoint Specification

## Purpose
The Knowledge Ingest endpoint specification defines the discovery contract for the ULX knowledge batch ingress surface.
It exists so external pipelines can discover the endpoint without inspecting daemon code directly.

## Scope
This specification covers:
- the `POST /knowledge/ingest` endpoint
- the classified batch payload shape
- the summary response shape
- the relationship between the daemon endpoint and the CLI batch command

This specification does not cover:
- knowledge classification policy
- the governed knowledge store schema
- broader specification registry behavior
- runtime orchestration outside this endpoint

## Discovery Contract
The endpoint SHOULD be discoverable through:
- `constitutional/knowledge-ingest.endpoint.json`
- docs-site mirror pages under `docs/site/knowledge-ingest/`

The endpoint manifest is informative and machine-readable.
It does not override CIS Core.

## Request Contract
`POST /knowledge/ingest` accepts either:

1. a JSON array of `KnowledgePipelineItem`
2. an object with an `items` array of `KnowledgePipelineItem`

Each item contains:
- `candidate`
- `classification`

The daemon and CLI MUST share the same batch contract.

## Response Contract
The endpoint returns a JSON summary with:
- `ok`
- `processed`
- `ingested`
- `excluded`
- `validationIssues`
- `projection`

The `projection` MUST match the governed store projection for the ingested batch.

## Implementation Mapping
- `src/daemon/knowledge.ts` handles the HTTP POST request
- `src/core/knowledge/batch.ts` parses and processes the batch
- `src/cli/commands/knowledgeIngest.ts` reuses the same batch processor

## Conformance Notes
An implementation claiming conformance SHOULD:
- preserve the batch format exactly
- keep the daemon endpoint and CLI command aligned
- expose the endpoint through the manifest entry

An implementation claiming stronger conformance MUST:
- return the documented response fields
- keep the response summary deterministic for the same input batch
- keep the manifest location stable for automated discovery

