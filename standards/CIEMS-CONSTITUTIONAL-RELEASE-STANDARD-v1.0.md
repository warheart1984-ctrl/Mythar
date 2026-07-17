# CIEMS Constitutional Release Standard v1.0

**Status:** Specified — reusable release template  
**Applies to:** CRS v1.0 and CAIP v1.0  
**Purpose:** Define the canonical release structure for constitutional artifacts within the CIEMS sovereignty stack.

## Release principles

Every release MUST be versioned, constitutional, reproducible, evidence-backed, platform-independent, and lineage-anchored. A constitutional specification governs behavior, semantics, evidence, and boundaries; a reference architecture demonstrates conformance and MUST NOT redefine the constitution.

## 1. Constitutional identity layer

Each release MUST declare:

- Artifact name
- Constitutional class (`Record System` or `AI Protocol`)
- Version
- Sovereignty-stack position: `Constitution → Specification → Conformance → Implementation → Deployment → Stewardship`
- Governance kernel: constitutional primitives and invariants
- Constitutional scope statement, including explicit non-goals

## 2. Constitutional specification layer

The governing, implementation-independent document MUST include:

1. Preamble
2. Constitutional definitions
3. Semantic primitives
4. Governance rules
5. Evidence Layer Contract
6. Conformance Contract
7. Execution Contract
8. Validation Contract
9. Continuity Contract (CCC)
10. Inference Contract (CIC)
11. Intent Lifecycle Contract (ILC)
12. Constitutional Knowledge Layer
13. Provenance requirements
14. Lineage and promotion rules: `Substrate → Substration → Promotion`

## 3. Reference architecture layer

This layer is non-constitutional and MUST be separately identified. It SHOULD provide:

- Reference implementation overview
- Execution environment
- Storage layer
- Operational topology
- Governance-kernel integration
- Constitutional-boundary diagram
- Evidence-capture pipeline
- Replay and verification path

Cloud Run, local execution, containers, PostgreSQL, filesystems, or other platform selections belong here—not in the constitutional specification.

## 4. Reproducibility and evidence layer

Every release MUST include a canonical release package, reproducible build instructions, conformance suite, replay evidence, operational evidence, constitutional-verification logs, reference-implementation outputs, deterministic-behavior evidence, and portability evidence for each declared supported platform in accordance with the [Repository Portability Policy](REPOSITORY-PORTABILITY-POLICY-v1.0.md) and its [Portability Implementation Specification](PORTABILITY-IMPLEMENTATION-SPEC-v1.0.md).

## 5. Release manifest

Each release MUST store a machine-readable manifest in `releases/<artifact>-v<version>/release-manifest.json` containing:

- `version`
- `artifact`
- `doi`
- `release_date`
- `canonical_package_sha256`
- `specification_path`
- `reference_architecture_path`
- `evidence_paths`
- `conformance_suite_path`
- `lineage`
- `promotion_status`

## 6. Archival layer

Zenodo deposits MUST include the canonical package, constitutional specification, reference architecture, evidence bundle, conformance suite, and lineage declaration. Metadata SHOULD include: `Constitutional Computing`, `CIEMS`, `Governed Intelligence`, `Semantic Governance`, and version-lineage terms.

## 7. Publication layer

Each release MUST provide a GitHub Release with DOI, release notes, manifest, evidence summary, and reference-architecture pointers. The documentation site MUST publish the specification, architecture, applicable API references, evidence layer, and conformance suite. Public-channel announcements MUST cross-link GitHub and Zenodo.

## 8. Stewardship layer

Each artifact MUST define maintenance rules, amendment procedures, constitutional-review cadence, evidence-renewal cadence, promotion criteria, deprecation rules, and governance-continuity requirements.

## Applicability profiles

| Artifact | Constitutional class | Governs |
| --- | --- | --- |
| CRS v1.0 | Record System | Constitutional state, lineage, evidence, and record semantics. |
| CAIP v1.0 | AI Protocol | AI intent, authority, evidence, inference, continuity, and constitutional boundaries. |

Both artifacts MUST use this release standard. Claims in resulting documents MUST be classified as **Observed**, **Specified**, or **Hypothesized** under the CRS Evidence Policy.
