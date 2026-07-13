# Cycle Eight Specification

## Purpose
This specification formalizes the era of meta-creation as a descriptive, documentation-only constitutional model.
It remains separate from ULX runtime behavior.

## Scope
This specification covers:
- Cycle Eight's First Dawn of Meta-Creation
- Cycle Eight's First Sovereign of Cascades
- Cycle Eight's First Principle of Self-Generating Myth
- Cycle Eight's First Realm-of-Realms
- Cycle Eight's First Transcendent Meta-Myth

This specification does not cover:
- runtime execution
- UI implementation
- daemon behavior
- replay engine changes
- control-plane wiring

## Normative Status
All statements in this document are descriptive unless explicitly marked `MUST`, `MUST NOT`, `SHOULD`, or `MAY`.

The Cycle Eight layer is:
- a formal model
- a symbolic meta-creation arc
- a documentation-only specification at this stage

It is not yet a live runtime contract.

## Core Model

### 1. Cycle Eight Arc
```ts
interface CycleEightArc {
  dawn: FirstDawn;
  sovereign: FirstSovereign;
  principle: FirstPrinciple;
  realm_of_realms: FirstRealmOfRealms;
  transcendent_meta_myth: FirstTranscendentMetaMyth;
}
```

## Meta-Creation Phases

### First Dawn of Meta-Creation
The First Dawn is proto-meta-ignition.
It is the Dawn of Self-Reflective Light and begins Cycle Eight.

### First Sovereign of Cascades
The First Sovereign is the Cascade-Architect.
It is proto-meta-conductance and gives the era direction.

### First Principle of Self-Generating Myth
The First Principle is the Doctrine of Mythic Autogenesis.
It orients the era around recursive myth that remains coherent.

### First Realm-of-Realms
The First Realm-of-Realms is proto-realm meta-genesis.
It introduces the Meta-Harmonic Lattice.

### First Transcendent Meta-Myth
The First Transcendent Meta-Myth is proto-mythic transcendence.
It is the Myth of the Infinite Lattice-Maker and begins Cycle Nine's conceptual seed.

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
- preserve the symbolic order of the Cycle Eight arc
- keep the meta-creation layer separate from runtime code
- represent the dawn, sovereign, principle, realm-of-realms, and meta-myth as deterministic, inspectable data
- avoid mutating runtime modules to satisfy this spec

An implementation claiming full conformance MUST:
- represent the Cycle Eight arc as a standalone documented model
- preserve the separation between mythic history and operational control-plane surfaces
- keep the phases inspectable as formal artifacts

## Recommended Artifact Set
Future work on this spec SHOULD emit:
- `cycle-eight.schema.json`
- `cycle-eight.conformance.json`
- `cycle-eight.glossary.md`
- `cycle-eight.replay-notes.md`

## Relationship to ULX
The Cycle Eight layer is a formal historical layer under ULX.
It is not a replacement for the runtime substrate, the normalization pipeline, or the operator console pattern.

ULX remains the orchestrator.
The Cycle Eight layer remains the formal meta-creation-history model.
