# Repository Portability Policy v1.0

**Status:** Repository law  
**Applies to:** Every artifact published from this repository  
**Supported operating systems:** Windows, macOS, and Linux

## Rule

Published artifacts MUST be usable on all supported operating systems unless an explicit, documented exception is ratified before publication. A developer's machine layout, user profile, drive letter, shell, or local secret MUST NOT be a prerequisite for use.

## Requirements

1. **Portable paths.** Runtime code, scripts, configuration, tests, and documentation MUST NOT contain developer-specific absolute paths. Paths MUST be resolved from explicit configuration, package resources, or project-relative locations.
2. **Deterministic configuration.** A runtime dependency such as a registry, data directory, or cache MUST have a documented, ordered resolution contract and a clear error when it cannot be located.
3. **Portable installation and execution.** Published Python, JavaScript, Rust, CLI, API, and container artifacts MUST use supported platform-neutral mechanisms. Shell-specific commands MUST identify their shell and provide an equivalent supported path when needed.
4. **Release verification.** Before publication, executable artifacts MUST pass their declared conformance or smoke tests on `ubuntu-latest`, `macos-latest`, and `windows-latest` in GitHub Actions.
5. **Portable documentation.** Quickstarts MUST work from a clean clone without knowledge of an author's filesystem or local environment. Environment overrides may be documented, but MUST NOT be required for the standard source-checkout path.
6. **No secrets in portability mechanisms.** Environment variables MAY configure paths and endpoints, but published defaults MUST NOT contain credentials, user identifiers, or private local locations.

## Evidence and release gate

The release manifest or conformance report MUST identify the portability workflow, commit, and passing OS matrix for every executable published artifact. A release that lacks passing Windows, macOS, and Linux evidence is not publication-ready.

## Exceptions

An exception requires a documented scope, rationale, affected operating systems, alternative access path, owner, expiration or review date, and a ratification record. An unavailable platform feature is not permission to silently narrow the support claim.

## Enforcement

The repository's `Portability` GitHub Actions workflow is the executable enforcement mechanism for the Mythar Core conformance suites. Maintainers MUST treat a failed matrix job as a release blocker.
