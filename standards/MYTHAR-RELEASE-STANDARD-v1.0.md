# Mythar Release Standard v1.0

## Purpose

This standard defines the minimum canonical package for any published Mythar release. Its purpose is reproducibility, traceability, reviewability, and durable citation.

## Required Release Package

Every release must contain:

1. **Release Manifest** — machine-readable identity, artifact inventory, compatibility, and hashes.
2. **CRS Evidence Policy** — Observed, Specified, and Hypothesized classifications.
3. **Mythar DCS version** — governing language/semantic constitutional version.
4. **Registry snapshot** — immutable registry JSON used by the release.
5. **API/OpenAPI specification** — public API contract, if an executable endpoint is released.
6. **Conformance report** — test corpus version, total, pass/fail results, and execution command.
7. **Assurance status** — declared conformance profile and assurance level.
8. **Changelog** — changes, compatibility effects, and migration notes.
9. **Ratification record** — approved constitutional amendments and authorities.
10. **DOI/Zenodo metadata** — title, authors, version, publication date, license, keywords, and DOI once assigned.

## Required Traceability Declarations

Each manifest must declare: CRS version, CAIP version, Mythar DCS version, conformance profile, assurance level, registry version, API versions, and release tag/commit.

## Evidence Labels

- **Observed:** externally evidenced; cite source and confidence.
- **Specified:** deliberate Mythar design; cite ratification or governing artifact.
- **Hypothesized:** proposed research; state assumptions and falsifiers.

## Release Gate

A release is publishable only when all required artifacts exist, the declared conformance report passes, assurance status is present, and the manifest is committed/tagged. DOI is `pending` until Zenodo publication assigns it.
