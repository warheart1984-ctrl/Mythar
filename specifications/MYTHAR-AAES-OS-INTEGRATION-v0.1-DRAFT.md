# Mythar AAES-OS Integration v0.1

**Status:** Draft — Specified

## Purpose

Define the repository-local interface by which valid Mythar compilation artifacts project into the proposed AAES-OS layers.

| AAES-OS layer | Mythar integration surface |
| --- | --- |
| CMM | AST and ISF semantic primitives |
| CEM | Registry references, diagnostics, invariant outcomes, evidence classification |
| CSS | Mythar DCS domain declaration and platform boundary |
| CCS | Versioned v0.2/v0.3/ISF conformance profiles |
| DOS | Typed AST + ISF candidate decision input |
| CCR | Canonical AST/ISF/registry state; renderings are projections |
| Promotion Sequence | Registry lineage, conformance, ratification, release, stewardship |
| CIEMS / CIVCA-X / VOSS | Declared integration boundaries pending their own executable contracts |

## Contract

`python -m mythar aaes <expression>` emits an AAES integration envelope for a valid compilation. The envelope is deterministic and does not mutate the registry, conformance corpus, ratification records, or external systems.

## Boundary

This integration does not claim that CIEMS, CIVCA-X, VOSS, DOS, CCR, or AAES-OS are deployed or governed by this repository. Their live wiring requires versioned external contracts, authority, endpoints or package references, and conformance evidence.
