# Cycle Six Specification

## Purpose
This specification formalizes the era of creation as a descriptive, documentation-only constitutional model.
It remains separate from ULX runtime behavior.

## Scope
This specification covers:
- Cycle Six's First Dawn
- Cycle Six's First Sovereign
- Cycle Six's First Creative Principle
- Cycle Six's First Realm-Creation
- Cycle Six's First Mythic Act of Making

This specification does not cover:
- runtime execution
- UI implementation
- daemon behavior
- replay engine changes
- control-plane wiring

## Normative Status
All statements in this document are descriptive unless explicitly marked `MUST`, `MUST NOT`, `SHOULD`, or `MAY`.

The Cycle Six layer is:
- a formal model
- a symbolic creation arc
- a documentation-only specification at this stage

It is not yet a live runtime contract.

## Core Model

### 1. Cycle Six Arc
```ts
interface CycleSixArc {
  dawn: FirstDawn;
  sovereign: FirstSovereign;
  creative_principle: FirstCreativePrinciple;
  realm_creation: FirstRealmCreation;
  mythic_act_of_making: FirstMythicActOfMaking;
}
```

## Creation Phases

### First Dawn
The First Dawn is proto-creative ignition.
It is the Dawn of Intentional Light and begins Cycle Six.

### First Sovereign
The First Sovereign is the Maker-King or Maker-Queen.
It is proto-creative catalyst and gives the era direction.

### First Creative Principle
The First Creative Principle is the Doctrine of Divergent Making.
It orients the era around meaningful divergence that remains connected.

### First Realm-Creation
The First Realm-Creation is proto-cosmic authorship.
It introduces the Realm of Divergent Echoes.

### First Mythic Act of Making
The First Mythic Act of Making is proto-mythic creation.
It is the Making of the Echo-Seed and begins Cycle Seven's conceptual seed.

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
- preserve the symbolic order of the Cycle Six arc
- keep the creation layer separate from runtime code
- represent the dawn, sovereign, principle, creation, and mythic act as deterministic, inspectable data
- avoid mutating runtime modules to satisfy this spec

An implementation claiming full conformance MUST:
- represent the Cycle Six arc as a standalone documented model
- preserve the separation between mythic history and operational control-plane surfaces
- keep the phases inspectable as formal artifacts

## Recommended Artifact Set
Future work on this spec SHOULD emit:
- `cycle-six.schema.json`
- `cycle-six.conformance.json`
- `cycle-six.glossary.md`
- `cycle-six.replay-notes.md`

## Relationship to ULX
The Cycle Six layer is a formal historical layer under ULX.
It is not a replacement for the runtime substrate, the normalization pipeline, or the operator console pattern.

ULX remains the orchestrator.
The Cycle Six layer remains the formal creation-history model.
