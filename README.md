# Mythar

**Mythar** is a versioned constitutional language-engineering and semantic-architecture project. It provides a deterministic compiler, governed registry, executable conformance suites, and a public release record for semantic systems research and development.

> Mythar is not presented as a completed historical reconstruction. Claims are classified under the CRS Evidence Policy as **Observed**, **Specified**, or **Hypothesized**.

## Current release

- **Version:** v0.3.0
- **Zenodo DOI:** [10.5281/zenodo.21400390](https://doi.org/10.5281/zenodo.21400390)
- **GitHub Release:** [v0.3.0](https://github.com/warheart1984-ctrl/Mythar/releases/tag/v0.3.0)
- **License and publication metadata:** see the [release manifest](releases/v0.3.0/release-manifest.json)

## What is included

- A constitutional registry of roots, particles, operators, grammar rules, graph constraints, and tests.
- Deterministic Mythar Core parsing and diagnostics in strict and lenient modes.
- API versioning: `/v1/compile` preserves Mythar Core v0.2 compatibility; `/v2/compile` serves v0.3 semantics.
- v0.3 ratified lexeme roles: `ema` is a root, `fak` is a stackable particle, and `tila` is a postfix meta-operator.
- Executable v0.2 and v0.3 conformance suites.

## Architecture and governance

Mythar separates constitutional specifications from platform choices:

| Layer | Responsibility |
| --- | --- |
| CRS | Governs how research and evidence are produced. |
| CAIP | Defines an implementation-independent AI architectural model. |
| Mythar DCS | Defines language, semantic, and constitutional behavior. |
| Reference architecture | Demonstrates a deployment approach, such as Cloud Run and PostgreSQL. |
| Reference implementation | Executes the reference architecture while remaining conformant to the specifications. |

Cloud platforms, databases, and containers are therefore implementation concerns—not constitutional requirements.

## Start here

- [Mythar DCS v1.0 draft](specifications/MYTHAR-DCS-v1.0-DRAFT.md)
- [Grammar](docs/grammar.md) · [AST schema](docs/ast.md) · [API reference](docs/api.md) · [Version guide](docs/versions.md)
- [Mythar v0.3 release announcement](releases/v0.3.0/GITHUB-RELEASE-ANNOUNCEMENT.md)
- [Mythar conformance matrix](conformance/MYTHAR-CONFORMANCE-MATRIX-v1.0.md)
- [Constitutional traceability matrix](conformance/CONSTITUTIONAL-TRACEABILITY-MATRIX-v0.1.md)
- [CIEMS Constitutional Release Standard](standards/CIEMS-CONSTITUTIONAL-RELEASE-STANDARD-v1.0.md)
- [Repository Portability Policy](standards/REPOSITORY-PORTABILITY-POLICY-v1.0.md)
- [Portability Implementation Specification](standards/PORTABILITY-IMPLEMENTATION-SPEC-v1.0.md)

## Run the compiler and conformance suites

macOS and Linux:

```bash
cd mythar-v0.2
PYTHONPATH=./src python -m mythar test

# Run the v0.3 corpus.
MYTHAR_CONFORMANCE_ROOT=../mythar-registry/tests/v0.3 PYTHONPATH=./src python -m mythar test
```

Windows PowerShell:

```powershell
cd mythar-v0.2
$env:PYTHONPATH = '.\src'
python -m mythar test

# Run the v0.3 corpus.
$env:MYTHAR_CONFORMANCE_ROOT = '..\mythar-registry\tests\v0.3'
python -m mythar test
```

The frozen release evidence records **101/101** passing v0.2 cases and **5/5** passing v0.3 cases. See the [release manifest](releases/v0.3.0/release-manifest.json) and [reproducibility materials](releases/v0.3.0/) for the constitutional release boundary.

Registry resolution is deterministic and platform-independent:

1. `MYTHAR_REGISTRY_DIR`, when explicitly configured;
2. project-local `registry/` or `data/registry/` directories;
3. the sibling `mythar-registry/` directory in a source checkout; then
4. the registry snapshot packaged with `mythar-core`.

A fresh checkout therefore needs no configuration on Windows, macOS, or Linux. Deployments that keep an immutable registry elsewhere may set `MYTHAR_REGISTRY_DIR` (`export MYTHAR_REGISTRY_DIR=/path/to/mythar-registry` on macOS/Linux). If no complete registry is found, Mythar reports the searched locations and the required configuration instead of falling back to a developer-specific path.

## Contributing and stewardship

Contributions should preserve deterministic parsing, registry provenance, constitutional invariants, and versioned conformance. Proposed research or semantics should identify its evidence classification and must not turn a reference architecture into a constitutional requirement.

The project evolves through ratified registry versions, conformance suites, release manifests, and archival records.
