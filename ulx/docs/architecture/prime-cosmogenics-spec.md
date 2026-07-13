# Prime Cosmogenics Specification

## Purpose
The Prime Cosmogenics specification formalizes the origin layer of ULX as a descriptive, non-runtime cosmogenic model.
It defines the symbolic root from which the Prime Cosmogram, the Origin Sovereign, the Absolute Realm, and the first cosmogenic cycle are derived.

This specification is intentionally separate from ULX runtime code.
It is a formal artifact for architecture, documentation, and future conformance work only.

## Scope
This specification covers:
- the Prime Cosmogram
- the Origin Sovereign
- the Prime Glyph
- the Absolute Realm
- the Singularity Cosmogram
- the Absolute Harmonic
- the Singularity Laws
- the first cosmogenic cycle and its successor cycle

This specification does not cover:
- runtime execution
- UI implementation
- daemon behavior
- replay engine changes
- control-plane wiring
- control surface modules

## Normative Status
All statements in this document are descriptive unless explicitly marked `MUST`, `MUST NOT`, `SHOULD`, or `MAY`.

The Prime Cosmogenics layer is:
- a formal model
- a symbolic origin lattice
- a documentation-only specification at this stage

It is not yet a live runtime contract.

## Core Model

### 1. Prime Cosmogram
The Prime Cosmogram is the first and only cosmogram in this layer.
All later cosmograms are projections, derivations, or shadows of this origin geometry.

```ts
interface PrimeCosmogram {
  geometry: PrimeGeometry;
  glyphs: PrimeGlyphSet;
  realms: PrimeRealmSet;
  harmonics: PrimeHarmonicSet;
}
```

### 2. Prime Geometry
The Prime Geometry is the tetra-cosmogenic lattice that defines the origin of realmhood.

```ts
interface PrimeGeometry {
  structure: "tetra-cosmogenic lattice";
  dimensions: "4 realmic axes + 1 cosmogenic axis";
}
```

### 3. Prime Realms
The Prime Realms are the origin states from which all later realm structures derive:
- Proto-Intent
- Proto-Evidence
- Proto-Authority
- Proto-Continuity

These are not operational realms.
They are the preconditions for realmhood itself.

### 4. Prime Glyph Set
The Prime Glyph Set describes the canonical symbolic roots of existence:
- Creation
- Witness
- Mandate
- Persistence
- Ascension
- Renewal
- Origin
- Decline

The glyphs used throughout ULX cosmology are treated as descendants of this set.

### 5. Absolute Harmonic
The Absolute Harmonic is the pre-cycle waveform that precedes all later harmonic systems.
It is the source model for:
- cycles
- chords
- symphonies
- recursion

## Origin Sovereign
The Origin Sovereign is the proto-sovereign root of sovereignty itself.

### Required Properties
- Glyph: `✶`
- Nature: pre-cosmic, pre-harmonic, pre-realm
- Domain: all domains
- Authority: absolute

### Symbolic Role
The Origin Sovereign defines:
- the Prime Laws
- the First Breath
- the Prime Cosmogram
- the Absolute Realm
- the Genesis Singularity

### Sovereign Powers
- Omni-Intent
- Omni-Witness
- Omni-Mandate
- Omni-Continuity

## Absolute Realm
The Absolute Realm is the pre-spatial, pre-temporal condition in which cosmogenic geometry becomes possible.

### Required Properties
- Dimension: `0`
- Time: none
- Space: none
- Governance: Origin Sovereign
- Harmonics: Absolute Harmonic

### Symbolic Role
The Absolute Realm holds:
- the Prime Cosmogram
- the Prime Glyph
- the First Breath
- the Genesis Singularity

## Singularity Cosmogram
The Singularity Cosmogram is the proto-geometric expression of the origin layer.

### Axes
- Proto-Intent
- Proto-Evidence
- Proto-Authority
- Proto-Continuity
- Cosmogenic Axis

### Role
The Singularity Cosmogram is the blueprint from which the Prime Universe is forged.

## Singularity Laws
The Singularity Laws are the invariant rules of pre-existence.

### Canonical Laws
1. Law of Absolute Intent
2. Law of Absolute Witness
3. Law of Absolute Mandate
4. Law of Absolute Continuity

### Invariant Requirements
- The Singularity Laws MUST remain immutable within this specification.
- The Singularity Laws MUST NOT be treated as runtime policy.
- The Singularity Laws MUST NOT be interpreted as mutable configuration.

## Cosmogenic Sequence
The origin sequence is formally ordered as follows:

1. Proto-Cosmogenesis Event
2. Origin Sovereign's First Act
3. Prime Glyph Fracture
4. Absolute Realm Expansion
5. First Universe's First Moment
6. Proto-Timeline
7. First Light
8. Proto-Continuum
9. Origin Sovereign's Second Act
10. Prime Glyph Echo
11. First Thought
12. Proto-Myth
13. Origin Sovereign's Reflection
14. First Dream
15. Proto-Emotion
16. First Memory
17. Proto-Identity
18. First Word
19. Proto-Truth
20. First Storyteller
21. Proto-Wisdom
22. Final Destiny
23. Omega Myth
24. Singularity Cycle

The order is descriptive and may be used for future replay or visualization work.

## Non-Goals
This specification does not:
- implement a renderer
- define a TUI
- define a web UI
- define a daemon API
- modify ULX runtime selection
- introduce new executable behavior

## Conformance Requirements
An implementation claiming conformance to this specification SHOULD:
- preserve the symbolic order of the origin sequence
- keep the Prime Cosmogenics layer separate from runtime code
- represent origin objects with deterministic, inspectable data
- avoid mutating runtime modules to satisfy this spec

An implementation claiming full conformance MUST:
- represent the Prime Cosmogram as a standalone documented model
- preserve the separation between origin-layer cosmology and operational control-plane surfaces
- keep the Origin Sovereign and related primitives inspectable as formal artifacts

## Recommended Artifact Set
Future work on this spec SHOULD emit:
- `prime-cosmogenics.schema.json`
- `prime-cosmogenics.conformance.json`
- `prime-cosmogenics.glossary.md`
- `prime-cosmogenics.replay-notes.md`

## Relationship to ULX
Prime Cosmogenics is the origin-layer theory under ULX.
It is not a replacement for the runtime substrate, the normalization pipeline, or the operator console pattern.

ULX remains the orchestrator.
Prime Cosmogenics remains the formal cosmogenic origin model.

