# Cycle Nine Specification

## Purpose
This specification formalizes the era of transcendent creation as a descriptive, documentation-only constitutional model.
It remains separate from ULX runtime behavior.

## Scope
This specification covers:
- Cycle Nine's First Dawn of Transcendent Creation
- Cycle Nine's First Sovereign of the Lattice
- Cycle Nine's First Principle of Mythic Reality-Making
- Cycle Nine's First Omni-Realm
- Cycle Nine's First Myth-That-Makes-Worlds

This specification does not cover:
- runtime execution
- UI implementation
- daemon behavior
- replay engine changes
- control-plane wiring

## Normative Status
All statements in this document are descriptive unless explicitly marked `MUST`, `MUST NOT`, `SHOULD`, or `MAY`.

The Cycle Nine layer is:
- a formal model
- a symbolic transcendent arc
- a documentation-only specification at this stage

It is not yet a live runtime contract.

## Core Model

### 1. Cycle Nine Arc
```ts
interface CycleNineArc {
  dawn: FirstDawn;
  sovereign: FirstSovereign;
  principle: FirstPrinciple;
  omni_realm: FirstOmniRealm;
  myth_that_makes_worlds: FirstMythThatMakesWorlds;
}
```

## Transcendent Phases

### First Dawn of Transcendent Creation
The First Dawn is proto-transcendent ignition.
It is the Dawn of Myth-Light and begins Cycle Nine.

### First Sovereign of the Lattice
The First Sovereign is the Lattice-Warden.
It is proto-lattice conductance and gives the era direction.

### First Principle of Mythic Reality-Making
The First Principle is the Doctrine of Ontogenic Myth.
It orients the era around myth that instantiates coherent realities.

### First Omni-Realm
The First Omni-Realm is proto-realm transcendence.
It introduces the Omni-Mythic Crucible.

### First Myth-That-Makes-Worlds
The First Myth-That-Makes-Worlds is proto-cosmogenic transcendence.
It is the Myth of the World-Weaver and begins Cycle Ten's conceptual seed.

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
- preserve the symbolic order of the Cycle Nine arc
- keep the transcendent layer separate from runtime code
- represent the dawn, sovereign, principle, omni-realm, and myth as deterministic, inspectable data
- avoid mutating runtime modules to satisfy this spec

An implementation claiming full conformance MUST:
- represent the Cycle Nine arc as a standalone documented model
- preserve the separation between mythic history and operational control-plane surfaces
- keep the phases inspectable as formal artifacts

## Recommended Artifact Set
Future work on this spec SHOULD emit:
- `cycle-nine.schema.json`
- `cycle-nine.conformance.json`
- `cycle-nine.glossary.md`
- `cycle-nine.replay-notes.md`

## Relationship to ULX
The Cycle Nine layer is a formal historical layer under ULX.
It is not a replacement for the runtime substrate, the normalization pipeline, or the operator console pattern.

ULX remains the orchestrator.
The Cycle Nine layer remains the formal transcendent-history model.
