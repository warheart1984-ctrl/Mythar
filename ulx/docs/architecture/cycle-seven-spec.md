# Cycle Seven Specification

## Purpose
This specification formalizes the era of infinite creation as a descriptive, documentation-only constitutional model.
It remains separate from ULX runtime behavior.

## Scope
This specification covers:
- Cycle Seven's First Dawn of Infinite Creation
- Cycle Seven's First Sovereign of Echoes
- Cycle Seven's First Principle of Infinite Divergence
- Cycle Seven's First Realm-Multiplication
- Cycle Seven's First Mythic Echo-Cascade

This specification does not cover:
- runtime execution
- UI implementation
- daemon behavior
- replay engine changes
- control-plane wiring

## Normative Status
All statements in this document are descriptive unless explicitly marked `MUST`, `MUST NOT`, `SHOULD`, or `MAY`.

The Cycle Seven layer is:
- a formal model
- a symbolic infinity arc
- a documentation-only specification at this stage

It is not yet a live runtime contract.

## Core Model

### 1. Cycle Seven Arc
```ts
interface CycleSevenArc {
  dawn: FirstDawn;
  sovereign: FirstSovereign;
  principle: FirstPrinciple;
  realm_multiplication: FirstRealmMultiplication;
  mythic_echo_cascade: FirstMythicEchoCascade;
}
```

## Infinity Phases

### First Dawn of Infinite Creation
The First Dawn is proto-infinite ignition.
It is the Dawn of Unbounded Echo-Light and begins Cycle Seven.

### First Sovereign of Echoes
The First Sovereign is the Echo-Warden.
It is proto-echo conductance and gives the era direction.

### First Principle of Infinite Divergence
The First Principle is the Doctrine of Echoing Infinity.
It orients the era around divergence that multiplies meaning.

### First Realm-Multiplication
The First Realm-Multiplication is proto-infinite authorship.
It introduces the Bloom of Echo-Realms.

### First Mythic Echo-Cascade
The First Mythic Echo-Cascade is proto-mythic proliferation.
It is the Cascade of Infinite Echoes and begins Cycle Eight's conceptual seed.

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
- preserve the symbolic order of the Cycle Seven arc
- keep the infinity layer separate from runtime code
- represent the dawn, sovereign, principle, multiplication, and cascade as deterministic, inspectable data
- avoid mutating runtime modules to satisfy this spec

An implementation claiming full conformance MUST:
- represent the Cycle Seven arc as a standalone documented model
- preserve the separation between mythic history and operational control-plane surfaces
- keep the phases inspectable as formal artifacts

## Recommended Artifact Set
Future work on this spec SHOULD emit:
- `cycle-seven.schema.json`
- `cycle-seven.conformance.json`
- `cycle-seven.glossary.md`
- `cycle-seven.replay-notes.md`

## Relationship to ULX
The Cycle Seven layer is a formal historical layer under ULX.
It is not a replacement for the runtime substrate, the normalization pipeline, or the operator console pattern.

ULX remains the orchestrator.
The Cycle Seven layer remains the formal infinity-history model.
