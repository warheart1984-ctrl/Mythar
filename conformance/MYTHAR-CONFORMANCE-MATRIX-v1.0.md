# Mythar Conformance Matrix v1.0

**Status:** Specified — release traceability artifact  
**Scope:** Mythar DCS v1.0 draft, RA-MYTHAR-001 (in progress), RI-MYTHAR-001, and deployed API evidence.

| Requirement | DCS clause | Reference architecture | Reference implementation | Conformance test | Operational evidence | Status |
|---|---|---|---|---|---|---|
| Registry versions are explicit and immutable per release. | §3 Required Traceability | RA-MYTHAR-001: registry snapshots in managed storage | `mythar-registry/registry-v0.1.json` through `registry-v0.3.json` | JSON validation; v0.2 conformance corpus | Cloud Run v1/v2 response identifies `api_version`; Git tag `v0.3.0` | Conforming |
| Every expression preserves registry lineage. | §5 Conformance | RA-MYTHAR-001: API returns auditable semantic outputs | `mythar-v0.2/src/mythar/core.py` | v0.2 101-case suite | Live authenticated `/v1/compile` and `/v2/compile` responses | Conforming |
| Constitutional invariants are enforced. | §5 Conformance | RA-MYTHAR-001: stateless compile service | `core.py` invariant engine | v0.2 positive/negative/invariant cases | Live API returns six invariant outcomes | Conforming |
| Canonical and experimental material are distinguished. | §4 Evidence Classification | RA-MYTHAR-001: registry/version isolation | `core.py` strict/lenient mode handling | v0.2 experimental candidate cases | Strict API rejects non-canonical material; lenient emits diagnostics | Conforming |
| `ema` is a root. | §6 Amendment Procedure | RA-MYTHAR-001: versioned registry deployment | `registry-v0.3.json`; v2 compiler | `V03-EMA-ROOT` | Live `/v2/compile` accepts `ema` | Conforming |
| `fak` is a stackable particle. | §6 Amendment Procedure | RA-MYTHAR-001: versioned registry deployment | `registry-v0.3.json`; v2 compiler | `V03-FAK-PARTICLE` | Live `/v2/compile` accepts `ja fak la ma` | Conforming |
| `tila` is a postfix meta-operator with a target. | §5 Conformance; §6 Amendment Procedure | RA-MYTHAR-001: API v2 contract | `core.py` `OperatorApplication` construction | `V03-TILA-META-OPERATOR`; `V03-TILA-MISSING-TARGET` | Live `/v2/compile` yields `META-TILA` for `maia tila` | Conforming |
| API versions preserve client compatibility. | §3 Required Traceability | RA-MYTHAR-001: versioned API routes | `api.py`: `/v1/compile`, `/v2/compile` | SDK v1/v2 route selection checks | Cloud Run revisions expose both routes | Conforming |
| Secrets are not committed and runtime credentials are externally managed. | §5 Conformance | RA-MYTHAR-001: Secret Manager-backed runtime secrets | `api.py` reads `MYTHAR_API_KEYS`; no secret values in repository | Release artifact credential scan | Secret Manager rotation; unauthenticated requests return 401 | Conforming |
| Releases are reproducible and citable. | §2 Governing Artifacts; §3 Required Traceability | RA-MYTHAR-001: build from tagged container source | `releases/v0.3.0/release-manifest.json`; Cloud Build config | Manifest JSON validation; conformance command recorded | GitHub tag; Cloud Build image `v0.3.0`; Zenodo DOI pending | Partially conforming |

## Interpretation

“Conforming” means the stated evidence exists at the time of this matrix. “Partially conforming” identifies a declared requirement whose final publication evidence is pending, not a failure of the runtime or language specification.
