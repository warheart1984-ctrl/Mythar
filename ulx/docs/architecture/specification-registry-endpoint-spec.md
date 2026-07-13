# Specification Registry Endpoint Specification

## Purpose
The Specification Registry endpoint provides a queryable HTTP view of the governed specification registry.
It lets tooling inspect the registry without introducing another authoritative source of truth.

## Scope
This specification covers:
- the `GET /specification-registry` endpoint
- the registry JSON payload
- the relationship between the daemon and the checked-in registry artifact

This specification does not cover:
- registry content policy
- specification governance adjudication
- mutation endpoints for the registry

## Discovery Contract
The endpoint SHOULD be discoverable through:
- `constitutional/specification-registry.endpoint.json`
- docs-site mirror pages under `docs/site/specification-registry/`

The endpoint manifest is informative and machine-readable.
It does not override CIS Core.

## Response Contract
`GET /specification-registry` returns the checked-in registry JSON payload.

The payload SHOULD include:
- registry identity
- document status
- steward
- classification
- launch readiness
- registry entries

## Implementation Mapping
- `src/daemon/specificationRegistry.ts` handles the HTTP GET request
- `src/core/specification-governance/registry.ts` reads and shapes the registry
- `src/daemon/index.ts` routes the request

## Conformance Notes
An implementation claiming conformance SHOULD:
- return the same registry payload as the checked-in artifact
- keep the endpoint read-only
- keep the manifest location stable for automated discovery

