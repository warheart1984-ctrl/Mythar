# Sovereign OS Constitutional Kernel Endpoint Specification

## Purpose and Scope
The Sovereign OS Constitutional Kernel endpoint specification defines the discovery contract for the kernel query surface.
It exists so external tools can locate the machine-readable kernel registry model without importing daemon code directly.

## Scope
This specification covers:
- the `GET /sovereign-os-constitutional-kernel` endpoint
- the CLI command `sovereign-os-constitutional-kernel`
- the registry-model payload returned by both surfaces
- the docs-site mirror pages for the endpoint

This specification does not cover:
- the runtime semantics of the constitutional kernel
- CIS Core authority
- any execution behavior beyond reading and returning the registry model

## Discovery Contract
The endpoint SHOULD be discoverable through:
- `constitutional/sovereign-os-constitutional-kernel.endpoint.json`
- docs-site mirror pages under `docs/site/sovereign-os-constitutional-kernel-endpoint/`

The endpoint manifest is informative and machine-readable.
It does not redefine CIS Core.

## Request Contract
`GET /sovereign-os-constitutional-kernel` has no request body.
It returns the checked-in kernel registry-model JSON payload.

The CLI command MUST return the same payload as the daemon endpoint.

## Response Contract
The endpoint returns the kernel registry-model JSON, including:
- `$schema`
- `$id`
- `id`
- `name`
- `documentStatus`
- `version`
- `steward`
- `classification`
- `launchReadiness`
- `kernel`
- `layers`

## Implementation Mapping
- `src/daemon/sovereignOsConstitutionalKernel.ts` handles the HTTP GET request
- `src/cli/commands/sovereignOsConstitutionalKernel.ts` reuses the same registry-model reader
- `src/core/specification-governance/registry.ts` provides the reader helper

## Conformance Notes
An implementation claiming conformance SHOULD:
- keep the daemon endpoint and CLI command aligned
- return the registry-model payload unchanged
- keep the manifest location stable for automated discovery

An implementation claiming stronger conformance MUST:
- return the documented response fields
- keep the response deterministic for the same checked-in payload
- preserve the documentation-first separation from the constitutional kernel spec
