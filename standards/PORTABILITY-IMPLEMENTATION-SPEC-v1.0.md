# Portability Implementation Specification v1.0

**Status:** Normative implementation specification  
**Implements:** [Repository Portability Policy v1.0](REPOSITORY-PORTABILITY-POLICY-v1.0.md)  
**Current support profile:** Windows, macOS, and Linux

## 1. OS-neutral paths

Runtime code, scripts, tests, configuration, and documentation MUST NOT use developer-specific absolute paths, drive letters, user-profile paths, or host-specific separators. Implementations MUST use platform-aware path handling and package-relative or project-relative resolution.

## 2. Deterministic resource discovery

Every runtime dependency that is not passed directly MUST document an ordered resolution contract. It MUST support an explicit environment-variable override, project-local discovery where applicable, installed package resources where applicable, and a clear configuration error when no valid resource is found.

## 3. Platform-independent execution

Published installation, quickstart, and test instructions MUST identify their shell. Where a command is shell-specific, an equivalent supported execution path MUST be provided for all declared platforms. A standard source checkout MUST run without private machine configuration.

## 4. CI verification

Executable artifacts MUST run their declared conformance or smoke suite in CI on `ubuntu-latest`, `macos-latest`, and `windows-latest`. The current enforcement workflow is [`.github/workflows/portability.yml`](../.github/workflows/portability.yml).

## 5. Release evidence

The release manifest or conformance report MUST record the portability workflow, source commit, supported-platform matrix, and result. A missing or failed required platform result blocks publication.

## 6. Change control

This specification may be amended through normal repository governance when implementation practice changes. Amendments MUST preserve the constitutional obligations in the Repository Portability Policy or explicitly seek a policy amendment.
